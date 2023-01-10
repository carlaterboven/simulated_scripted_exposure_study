import time
import math
from pythonosc.udp_client import SimpleUDPClient
from multiprocessing import Process

class SonificationLogic:
    def __init__(self, sampling_time):
        self.__oscmessenger = OSCMessenger(sampling_time)

    def __del__(self):
        pass

    def play_sound(self, pm2_5, pm10):
        p1 = Process(target=self.__oscmessenger.geiger_counter, args=[pm2_5])
        p2 = Process(target=self.__oscmessenger.string_sound, args=[pm10])
        p1.start()
        p2.start()
        p1.join()
        p2.join()

class OSCMessenger:
    client = SimpleUDPClient("127.0.0.1", 6666)
    pm2_5_EU_threshold = 25
    pm2_5_WHO_threshold = 10
    pm10_EU_threshold = 40
    pm10_WHO_threshold = 20

    def __init__(self, sampling_time):
        # time in seconds until next sound interval
        self.__sampling_time = sampling_time
        self.start_sound()

    def __del__(self):
        pass

    def start_sound(self):
        # TODO add introduction to sonification concepts
        pass

    def string_sound(self, pm10):
        # TODO maybe other sound at 15 (WHO) and 40 (EU)
        duration_original_sample = 2966
        num_samples = 284770
        min_pm10 = 0
        max_pm10 = 36
        duration_minpm = 2100
        duration_maxpm = 700
        if math.isnan(pm10): # gps outside of test area -> no sound
            duration = 0
        else:
            duration = (duration_maxpm - duration_minpm)/(max_pm10 - min_pm10) * pm10 + duration_minpm
        OSCMessenger.client.send_message("/string_sound", [self.__sampling_time * 1000, duration, 0, num_samples, duration])

    def geiger_counter(self, pm2_5):
        if math.isnan(pm2_5):
            pm2_5 = 0
        pm2_5 = round(pm2_5)
        # click once for every 2µg disjoint PM2.5 pollution
        num_clicks = pm2_5//2
        if num_clicks == 0:
            return
        else:
            OSCMessenger.client.send_message("/geiger", [self.__sampling_time * 1000, (self.__sampling_time * 1000) / num_clicks, 0, 1585, 33])
