from random import uniform

class GpsMock:
    def __init__(self):
        self.__lat = 0
        self.__lon = 0
        self.__alt = 0
        self.__time = 0


    def __del__(self):
        pass

    def get_position(self):
        # TODO read monitored data
        # self.read_time_series()
        return [uniform(52.393, 52.394), uniform(13.0409, 13.0413)] # random gps generation for testing

    def read_time_series(self):
        pass

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
