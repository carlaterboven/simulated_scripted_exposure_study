import pandas as pd
import os

class DataLogger:
    def __init__(self, file):
        self.__file = file
        self.__logid = 0
        self.__has_header = False

    def __del__(self):
        pass

    def get_file(self):
        return self.__file

    def write_header(self, header_list):
        header = 'LogID'
        for title in header_list:
            header += ','
            header += title
        header += '\n'
        file = open(self.__file, 'w')
        file.write(header)
        file.close()
        self.__has_header = True

    def write_data(self, data):
        if self.__has_header is False:
            self.write_header(data.keys())
        data_row = str(self.__logid)
        for key, value in data.items():
            data_row += ','
            data_row += str(data[key])
        data_row += '\n'
        file = open(self.__file, 'a')
        file.write(data_row)
        file.close()
        self.__logid += 1
