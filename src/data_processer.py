import numpy as np
import pandas as pd

class DataProcesser:
    def __init__(self, raw_data_files, atmotube_data_files):
        self.__step = 0.0001
        self.__raspi_data = pd.DataFrame()
        self.__all_data = pd.DataFrame()
        self.__data_files = raw_data_files
        self.__atmotube_data_files = atmotube_data_files

    def __del__(self):
        pass

    def get_data(self):
        return self.__all_data

    def run_complete_processing(self):
        self.import_data()
        self.treat_outliers()
        self.calibrate_data()
        self.calculate_grid_index()
        pm2_5_grid = self.get_median_squares_filtered('median_PM2.5')
        pm10_grid = self.get_median_squares_filtered('median_PM10')
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

        for filename in self.__atmotube_data_files:
            file = pd.read_csv('../raw_data/' + filename)
            file.rename(columns={"Date": "time"}, inplace=True)
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
            self.__all_data = pd.concat([self.__all_data, combined_data])

    def treat_outliers(self):
        # treat outliers (nan when z-score > 3)
        columns = ['5003_PM2.5', '7003_PM2.5', 'SPS_PM2.5', 'atmotube_PM2.5[µg/m³]', '5003_PM10', '7003_PM10', 'SPS_PM10', 'atmotube_PM10[µg/m³]']

        for column in columns:
            mean = np.mean(self.__all_data[column])
            std = np.std(self.__all_data[column])
            self.__all_data['zscore_' + column] = (self.__all_data[column] - mean) / std

        for column in columns:
            if self.__all_data['zscore_' + column].all() != np.NaN:
                self.__all_data[abs(self.__all_data['zscore_' + column]) > 3] = np.NaN

    def calibrate_data(self):
        # calculate means and median for each data point (PM2.5, PM10, Temp, Hum)
        # TODO: replace this with the regression model
        self.__all_data['mean_PM2.5'] = self.__all_data[['5003_PM2.5', '7003_PM2.5', 'SPS_PM2.5', 'atmotube_PM2.5[µg/m³]']].mean(axis=1)
        self.__all_data['mean_PM10'] = self.__all_data[['5003_PM10', '7003_PM10', 'SPS_PM10', 'atmotube_PM10[µg/m³]']].mean(axis=1)
        self.__all_data['mean_Temp'] = self.__all_data[['Temperature', 'atmotube_Temperature[˚C]']].mean(axis=1)
        self.__all_data['mean_Rel_Hum'] = self.__all_data[['Relative_Humidity', 'atmotube_Humidity[%]']].mean(axis=1)

        self.__all_data['median_PM2.5'] = self.__all_data[['5003_PM2.5', '7003_PM2.5', 'SPS_PM2.5', 'atmotube_PM2.5[µg/m³]']].median(axis=1)
        self.__all_data['median_PM10'] = self.__all_data[['5003_PM10', '7003_PM10', 'SPS_PM10', 'atmotube_PM10[µg/m³]']].median(axis=1)
        self.__all_data['median_Temp'] = self.__all_data[['Temperature', 'atmotube_Temperature[˚C]']].median(axis=1)
        self.__all_data['median_Rel_Hum'] = self.__all_data[['Relative_Humidity', 'atmotube_Humidity[%]']].median(axis=1)

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

    def get_median_squares_filtered(self, feature, min_record_filter = 3):
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
