import numpy as np
import pandas as pd
import math
import gps
import gps_mock

class Simulation:
    def __init__(self, live_gps):
        self.__step = 0.0001   # size of grid fields for underlying pm data
        self.__last_valid_index = [52.3894,13.0393]
        self.__gps_sensor = gps.Gps() if live_gps else gps_mock.GpsMock()
        pc_path = '../simulation_data/simulation_data.csv'
        raspi_path = '/home/pi/Dokumente/simulated_scripted_exposure_study/simulation_data/simulation_data.csv'
        self.__data_path = raspi_path if live_gps else pc_path
        self.__data = self.get_dataframe()

    def __del__(self):
        pass

    def get_value(self, feature, position):
        index = self.get_index(position[0], position[1])
        value = self.get_value_from_df(feature, index)
        if math.isnan(value):
            # choose one of the following methods to handle gps data outside test area
            #return self.get_last_valid_value(feature)
            return math.nan
        else:
            #self.__last_valid_index = index
            return value

    def get_last_valid_value(self, feature):
        # no simulated data for gps position - return last valid value till GPS is "back on track"
        # TODO send notice when this happens for a longer time period or return 'false' value
        return self.get_value_from_df(feature, self.__last_valid_index)

    def get_gps(self):
        return self.__gps_sensor.get_position()

    def get_step(self):
        return self.__step

    def get_index(self, lat, lon):
        if lat == 'n/a' or lon == 'n/a':
            return math.nan
        lat_idx = np.floor(lat / self.get_step()) * self.get_step()
        lon_idx = np.floor(lon / self.get_step()) * self.get_step()
        return [lat_idx, lon_idx]

    def get_dataframe(self):
        dataframe = pd.read_csv(self.__data_path)
        dataframe = dataframe.set_index(['latitude_index', 'longitude_index'])
        return dataframe

    def get_value_from_df(self, feature, index):
        try:
            return self.__data.loc[round(index[0], 4), round(index[1], 4)][feature]
        except:
            return math.nan
