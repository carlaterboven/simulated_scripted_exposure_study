from random import uniform
import pandas as pd

class GpsMock:
    def __init__(self):
        self.__lat = 0
        self.__lon = 0
        self.__alt = 0
        self.__time = 0
        self.__logid = 0
        mock_path = '../study_monitoring_data/gps_testrun.csv'
        #mock_path = '../study_monitoring_data/log_test_area.csv'
        #mock_path = '../simulation_data/simulation_data.csv'
        self.__mock_file = pd.read_csv(mock_path)

    def __del__(self):
        pass

    def get_position(self):
        self.read_time_series()
        return [self.get_lat(), self.get_lon()]
        # return [uniform(52.393, 52.394), uniform(13.0409, 13.0413)] # random gps generation for testing

    def read_time_series(self):
        self.__time = self.__mock_file.loc[self.__logid, 'time']
        self.__lat = self.__mock_file.loc[self.__logid, 'lat']
        self.__lon = self.__mock_file.loc[self.__logid, 'lon']
        self.__alt = self.__mock_file.loc[self.__logid, 'alt']
        #self.__lat = self.__mock_file.loc[self.__logid, 'latitude_index']
        #self.__lon = self.__mock_file.loc[self.__logid, 'longitude_index']
        self.__logid += 1

    def get_lat(self):
        return self.__lat

    def get_lon(self):
        return self.__lon

    def get_alt(self):
        return self.__alt

    def get_time(self):
        return self.__time

    def get_data(self):
        return {
            'lat': self.__lat,
            'lon': self.__lon,
            'alt': self.__alt,
            'time': self.__time
            }
