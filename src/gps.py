from gps3 import agps3
import RPi.GPIO as GPIO
from random import uniform

class Gps:
    def __init__(self):
        self.__lat = 0
        self.__lon = 0
        self.__alt = 0
        self.__time = 0
        self.__gps_socket = agps3.GPSDSocket()
        self.__data_stream = agps3.DataStream()

        self.__gps_socket.connect()
        self.__gps_socket.watch()

        GPIO.setmode(GPIO.BCM)
        self.__RED_LED = 27
        GPIO.setup(self.__RED_LED, GPIO.OUT)
        GPIO.output(self.__RED_LED, GPIO.LOW)
        self.__GREEN_LED = 17
        GPIO.setup(self.__GREEN_LED, GPIO.OUT)
        GPIO.output(self.__GREEN_LED, GPIO.LOW)
        
        self.green_led()

    def __del__(self):
        GPIO.output(self.__GREEN_LED, GPIO.LOW)
        GPIO.output(self.__RED_LED, GPIO.LOW)
        GPIO.cleanup()
        pass

    # TODO replace this when GPS sensor is available again
    def get_position(self):
        self.compute_position()
        return [self.get_lat(), self.get_lon()]
        #return [52.393768, 13.041159]
        #return [uniform(52.393, 52.394), uniform(13.0409, 13.0413)] # random gps generation for testing

    def show_feedback(self):
        # use green LED to show successfull GPS
        if self.get_lat() != 'n/a':
            self.green_led()
        else:
            self.red_led()

    def green_led(self):
        # use green LED to show successfull GPS
        GPIO.output(self.__RED_LED, GPIO.LOW)
        GPIO.output(self.__GREEN_LED, GPIO.HIGH)

    def red_led(self):
        GPIO.output(self.__GREEN_LED, GPIO.LOW)
        GPIO.output(self.__RED_LED, GPIO.HIGH)

    def compute_position(self):
        try:
            for new_data in self.__gps_socket:
                if new_data:
                    self.__data_stream.unpack(new_data)
                    self.__time = self.__data_stream.time
                    self.__lat = self.__data_stream.lat
                    self.__lon = self.__data_stream.lon
                    self.__alt = self.__data_stream.alt
                    self.show_feedback()    # use red and green led
                    return
        except:
            print('GPS Error')
            self.red_led()

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
