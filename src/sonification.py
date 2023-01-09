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
        # handle gps outside test area like 0-values -> no sound
        # when preferring e.g. alarm sounds change these if-statements
        if math.isnan(pm2_5):
            pm2_5 = 0
        if math.isnan(pm10):
            pm10 = 0
        #p1 = Process(target=self.__oscmessenger.geiger_counter, args=[pm2_5])
        p2 = Process(target=self.__oscmessenger.string_sound, args=[pm10])
        #p1.start()
        p2.start()
        #p1.join()
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

    def midi(self, pm10):
        OSCMessenger.client.send_message("/midi", [40 + int(pm10)*2])

    def beep(self, pm10):
        #OSCMessenger.client.send_message("/beep", [int(pm10)*2])
        num_samples_schrillkurz = 24476
        duration_schrillkurz = 555
        duration = min(duration_schrillkurz * pm10 , self.__sampling_time * 1000)
        print('duration: ', duration)
        # send [sampling time in ms, time for one sample (metronome), start in sample, end in sample, duration]
        OSCMessenger.client.send_message("/beep", [self.__sampling_time * 1000, duration, 0, num_samples_schrillkurz, duration])


    def string_sound(self, pm10):
        num_samples_sound5 = 436992
        num_samples = num_samples_sound5 * (2000 / 4552)
        duration_sound5 = 4552
        num_samples_sound6 = 284770
        duration_sound6 = 2966
        #duration = duration_sound5 * (2000 / 4552) / pm10
        #duration = -50 * pm10 + 2700
        min_pm10 = 0
        max_pm10 = 40
        duration_minpm = 1000
        duration_maxpm = 700
        duration = (duration_maxpm - duration_minpm)/(max_pm10 - min_pm10) * pm10 + duration_minpm
        print('duration string_sound: ', duration)
        OSCMessenger.client.send_message("/string_sound", [self.__sampling_time * 1000, duration, 0, num_samples, duration])

    def cello(self, pm10):
        duration_cello_wav = 3500
        duration_fadeinout = 500
        num_samples = 168002
        #duration_solo = duration_cello_wav - duration_fadeinout

        min_pm10 = 0
        max_pm10 = 40
        duration_minpm = 2300
        duration_maxpm = 700
        duration_sample = (duration_maxpm - duration_minpm)/(max_pm10 - min_pm10) * pm10 + duration_minpm

        duration_solo = 6/7 * duration_sample
        metronome_time = 2 * duration_solo

        #duration = min(self.__sampling_time * 1000, duration_cello_wav - duration_fadeinout)
        OSCMessenger.client.send_message("/cello", [self.__sampling_time * 1000, duration_solo, 0, num_samples, duration_sample, metronome_time])

    def cello2(self, pm10):
        duration_cello_wav = 1000
        duration_fadeinout = 500
        num_samples = 48004
        #duration_solo = duration_cello_wav - duration_fadeinout

        min_pm10 = 0
        max_pm10 = 40
        duration_minpm = 1000
        duration_maxpm = 200
        duration_sample = (duration_maxpm - duration_minpm)/(max_pm10 - min_pm10) * pm10 + duration_minpm

        duration_solo = 0.4 * duration_sample
        metronome_time = 2 * duration_solo

        #duration = min(self.__sampling_time * 1000, duration_cello_wav - duration_fadeinout)
        OSCMessenger.client.send_message("/cello2", [self.__sampling_time * 1000, duration_solo, 0, num_samples, duration_sample, metronome_time])

    def mystic(self, pm10):
        # set the time in seconds while there is sound
        sampling_time = 2

        # pm10 between 0 and 20
        # if 0 -> max_duration 4552
        # if 20 -> min_duration ca 400
        multiplier = 1 - (pm10 / 20)
        max_duration = 4552 - 400
        duration = multiplier * max_duration + 400

        time_left = sampling_time * 1000
        num_samples_sound5 = 436992
        while time_left >= duration:
            client.send_message("/sound5", [0, num_samples_sound5, duration])
            time_left = time_left - duration
            time.sleep(duration/1000)
        if time_left > 0:
            # lücken weg bekommen?! time_left = time_left + 500
            client.send_message("/sound5", [0, num_samples_sound5/duration * time_left, time_left])
            #time.sleep(time_left/1000)


    def geiger_counter(self, pm2_5):
        pm2_5 = round(pm2_5)
        # click once for every 2µg disjoint PM2.5 pollution
        num_clicks = pm2_5//2
        if num_clicks == 0:
            return
        else:
            OSCMessenger.client.send_message("/geiger", [self.__sampling_time * 1000, (self.__sampling_time * 1000) / num_clicks, 0, 1585, 33])


    def asthma_inhaler(self, pm10s, joint_pm10):
        # only click if higher than threshold
        if joint_pm10 <= pm10_WHO_threshold:
            time.sleep(10)
        else:
            for pm10 in pm10s:
                # times of inhaling asthma spray is based on pm 10 (between 0 and 25, all outliers rounded to 25)
                pm10 = round(pm10)
                if pm10 > 25:
                    pm10 = 25

                # set time in seconds while geiger clicks
                sampling_time = 10/len(pm10s)
                # click once for every 5µg disjoint PM10 pollution
                num_clicks = pm10//5
                if num_clicks == 0:
                    time.sleep(sampling_time)
                else:
                    for click in range(num_clicks):
                        client.send_message("/asthma", [0, 42889, 893])
                        time.sleep(sampling_time/num_clicks)


    def air_bubbles(self, pm2_5):
        if pm2_5 < 7:
            for i in range(5):
                client.send_message("/air_bubble", [0, 8837, 600])
                time.sleep(2)
        elif pm2_5 < 15:
            for i in range(10):
                client.send_message("/air_bubble", [0, 8837, 500])
                time.sleep(1)
        elif pm2_5 < 28:
            for i in range(20):
                client.send_message("/air_bubble", [0, 8837, 400])
                time.sleep(0.5)
        else:
            for i in range(25):
                client.send_message("/air_bubble", [0, 8837, 400])
                time.sleep(0.4)


    def breath(self, pm1):
        # most relaxed breath is 10 sec
        # one slow breath is 7 sec
        # fastest breath here is 1 sec
        if pm1 < 15:
            client.send_message("/breath", [0, 336001, 10000])
            time.sleep(10)
        elif pm1 < 21:
            client.send_message("/breath", [0, 336001, 5000])
            time.sleep(5)
            client.send_message("/breath", [0, 336001, 5000])
            time.sleep(5)
        elif pm1 < 31:
            for i in range(4):
                client.send_message("/breath", [0, 336001, 2500])
                time.sleep(2.5)
        else:
            for i in range(10):
                client.send_message("/breath", [0, 336001, 1000])
                time.sleep(1)
