import numpy as np
import pandas as pd

class DataProcesser:
    def __init__(self, raw_data_files):
        self.__step = 0.0001
        self.__raspi_data = pd.DataFrame()
        self.__all_data = pd.DataFrame()
        self.__data_files = raw_data_files
        self.__pm25_model = {'intercept': 236.811578,
                                'Temperature': -0.8362344519399749,
                                'Relative_Humidity': -0.2450215855176837,
                                'Pressure': -0.20451594934190478,
                                'adjusted_7003_nc1': -24.078732881769838,
                                'adjusted_7003_nc2.5': 24.40651305536212,
                                'SPS_nc1': -0.2001422164432161,
                                'SPS_nc2.5': 0.1448523455040038}
        self.__pm10_model = {'intercept': 198.428905,
                                'Temperature': -0.14278992737700533,
                                'Relative_Humidity': -0.34871100871820576,
                                'Pressure': -0.16117068286679956,
                                'adjusted_7003_nc5': -165.22398021677273,
                                'adjusted_7003_nc10': 165.40755230000087,
                                'SPS_nc4': -8.278088841232316,
                                'SPS_nc10': 8.298401220613906}

    def __del__(self):
        pass

    def get_data(self):
        return self.__all_data

    def run_complete_processing(self):
        self.import_data()
        self.treat_outliers()
        self.calibrate_data()
        self.calculate_grid_index()
        pm2_5_grid = self.get_median_squares_filtered('PM2.5')
        pm10_grid = self.get_median_squares_filtered('PM10')
        complete_grid = pd.concat([pm2_5_grid, pm10_grid], axis=1)
        return complete_grid

    def import_data(self):
        for filename in self.__data_files:
            file = pd.read_csv('../raw_data/' + filename)
            # clear NaN locations (usually due to startup)
            file.dropna(subset=['lat', 'lon', 'alt', 'time'], inplace=True)
            # convert to timezone of Potsdam
            file['time'] = pd.to_datetime(file['time'], format='%Y-%m-%d %H:%M:%S.%f').dt.tz_convert('CET')
            file['time'] = file['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
            # string back to datetime format
            file['time'] = pd.to_datetime(file['time'])
            # use timestamp as new index
            file.drop('LogID', axis=1, inplace=True)
            file.set_index('time', inplace=True)
            # add all files to one dataframe
            self.__raspi_data = pd.concat([self.__raspi_data, file])
        self.__all_data = self.__raspi_data
        self.level_bme680()
        self.adjust_nc_7003()

    def level_bme680(self):
        self.__all_data['Relative_Humidity'] = self.__all_data['Relative_Humidity'] + 8
        self.__all_data['Temperature'] = self.__all_data['Temperature'] - 4
        # deal with missing data: use atmotube dec7 and dec9
        missing_data_df = pd.DataFrame()
        atmotube_filenames = ['atmotube_dec7.csv', 'atmotube_dec9.csv']
        for filename in atmotube_filenames:
            file = pd.read_csv('../raw_data/' + filename)
            file.rename(columns={"Date": "time"}, inplace=True)
            file = file[['time', 'atmotube_Temperature[˚C]','atmotube_Humidity[%]','atmotube_Pressure[hPa]']]
            file['time'] = pd.to_datetime(file['time'], format='%Y-%m-%d %H:%M:%S.%f')
            # remove redundant measurements outside the test route
            date = file['time'][0].date()
            date_data = self.__raspi_data[self.__raspi_data.apply(lambda row : row.name.date() == date,axis=1)]
            min_time = date_data.index.min() - pd.Timedelta(minutes=1)
            max_time = date_data.index.max()
            file.drop(file[file['time'] < min_time].index, inplace=True)
            file.drop(file[file['time'] > max_time].index, inplace=True)
            # order dataframe with ascending time (needed for merge)
            file = file.iloc[::-1]
            file['time'] = pd.to_datetime(file['time'])
            file.set_index('time', inplace=True)
            # enriching the data points with the atmotube data per minute
            combined_data = pd.merge_asof(date_data, file, on='time', direction='backward')
            combined_data.name = str(date)
            missing_data_df = pd.concat([missing_data_df, combined_data], ignore_index=True)
        missing_data_df['Temperature'] = missing_data_df['atmotube_Temperature[˚C]']
        missing_data_df['Relative_Humidity'] = missing_data_df['atmotube_Humidity[%]']
        missing_data_df['Pressure'] = missing_data_df['atmotube_Pressure[hPa]']
        missing_data_df.drop(['atmotube_Temperature[˚C]','atmotube_Humidity[%]','atmotube_Pressure[hPa]'], axis=1, inplace=True)
        missing_data_df.set_index('time', inplace=True)
        self.__all_data = self.__all_data.fillna(missing_data_df)

    def adjust_nc_7003(self):
        self.__all_data.loc[:,'adjusted_7003_nc0.3'] = self.__all_data.loc[:, '7003_nc0.3'] / 100
        self.__all_data.loc[:,'adjusted_7003_nc0.5'] = self.__all_data.loc[:, ('7003_nc0.3', '7003_nc0.5')].sum(axis=1) / 100
        self.__all_data.loc[:,'adjusted_7003_nc1'] = self.__all_data.loc[:, ('7003_nc0.3', '7003_nc0.5', '7003_nc1')].sum(axis=1) / 100
        self.__all_data.loc[:,'adjusted_7003_nc2.5'] = self.__all_data.loc[:, ('7003_nc0.3', '7003_nc0.5', '7003_nc1', '7003_nc2.5')].sum(axis=1) / 100
        self.__all_data.loc[:,'adjusted_7003_nc5'] = self.__all_data.loc[:, ('7003_nc0.3', '7003_nc0.5', '7003_nc1', '7003_nc2.5', '7003_nc5')].sum(axis=1) / 100
        self.__all_data.loc[:,'adjusted_7003_nc10'] = self.__all_data.loc[:, ('7003_nc0.3', '7003_nc0.5', '7003_nc1', '7003_nc2.5', '7003_nc5', '7003_nc10')].sum(axis=1) / 100

    def treat_outliers(self):
        # treat outliers (nan when z-score > 3)
        columns = ['Temperature', 'Relative_Humidity', 'Pressure',
                    'adjusted_7003_nc1', 'adjusted_7003_nc2.5', 'adjusted_7003_nc5', 'adjusted_7003_nc10',
                    'SPS_nc1', 'SPS_nc2.5', 'SPS_nc4', 'SPS_nc10']
        for column in columns:
            mean = np.mean(self.__all_data[column])
            std = np.std(self.__all_data[column])
            self.__all_data['zscore_' + column] = (self.__all_data[column] - mean) / std
        for column in columns:
            if self.__all_data['zscore_' + column].all() != np.NaN:
                self.__all_data[abs(self.__all_data['zscore_' + column]) > 3] = np.NaN
        self.__all_data.dropna(inplace=True)

    def calibrate_data(self):
        self.__all_data['intercept'] = 1
        self.__all_data['PM2.5'] = 0
        self.__all_data['PM10'] = 0
        for parameter in self.__pm25_model.keys():
            self.__all_data['PM2.5'] = self.__all_data['PM2.5'] + self.__pm25_model[parameter] * self.__all_data[parameter]
        self.__all_data.loc[self.__all_data['PM2.5'] < 0, 'PM2.5'] = 0.0
        for parameter in self.__pm10_model.keys():
            self.__all_data['PM10'] = self.__all_data['PM10'] + self.__pm10_model[parameter] * self.__all_data[parameter]
        self.__all_data.loc[self.__all_data['PM10'] < 0, 'PM10'] = 0.0

    def calculate_means(self):
        # calculate means for each data point (PM2.5, PM10)
        self.__all_data['mean_PM2.5'] = self.__all_data[['5003_PM2.5', '7003_PM2.5', 'SPS_PM2.5']].mean(axis=1)
        self.__all_data['mean_PM10'] = self.__all_data[['5003_PM10', '7003_PM10', 'SPS_PM10']].mean(axis=1)

    def calculate_medians(self):
        # calculate medians for each data point (PM2.5, PM10)
        self.__all_data['median_PM2.5'] = self.__all_data[['5003_PM2.5', '7003_PM2.5', 'SPS_PM2.5']].median(axis=1)
        self.__all_data['median_PM10'] = self.__all_data[['5003_PM10', '7003_PM10', 'SPS_PM10']].median(axis=1)

    def calculate_grid_index(self):
        self.__all_data['latitude_index'] = self.__all_data.apply(lambda row: np.floor(row['lat'] / self.__step) * self.__step, axis=1)
        self.__all_data['longitude_index'] = self.__all_data.apply(lambda row: np.floor(row['lon'] / self.__step) * self.__step, axis=1)
        self.__all_data['grid_index'] = self.__all_data.apply(lambda row: [np.floor(row['lat'] / self.__step) * self.__step, np.floor(row['lon'] / self.__step) * self.__step], axis=1)
        self.__all_data = self.__all_data.astype({'grid_index':'string'})

    def get_median_squares(self, feature):
        # make sure that data column does not contain nan values
        df = self.__all_data.dropna(subset=[feature])
        median_grid = df.groupby(pd.Grouper(key='grid_index')).median()
        median_grid = median_grid[['latitude_index', 'longitude_index', feature]]
        median_grid = median_grid.set_index(['latitude_index', 'longitude_index'])
        return median_grid

    def get_median_squares_filtered(self, feature, min_record_filter = 9):
        # make sure that data column does not contain nan values
        df = self.__all_data.dropna(subset=[feature])
        median_grid = df.groupby(pd.Grouper(key='grid_index')).median()
        # only use fields in grid that have 3 (min_record_filter) or more data records
        number_datapoints = df.groupby(pd.Grouper(key='grid_index')).size()
        min_record_grid = median_grid.drop(number_datapoints[number_datapoints < min_record_filter].index)
        min_record_grid = min_record_grid[['latitude_index', 'longitude_index', feature]]
        min_record_grid = min_record_grid.set_index(['latitude_index', 'longitude_index'])
        return min_record_grid

    def export_grid_csv(self, grid):
        grid.to_csv('../simulation_data/simulation_data.csv')
