# coding=utf-8
#import pandas as pd
import time
#from multiprocessing import Process
import os
import simulation
import sonification

def try_sensor_read(sensor):
    try:
        sensor.read_data()
    except KeyboardInterrupt:
        raise
    except:
        sensor.set_nan_data()




if __name__ ==  '__main__':
    print('Read and collect data. [Press Ctrl+C to exit!]')

    simulator = simulation.Simulation()
    sonify = sonification.SonificationLogic()

    try:
        while True:
            # TODO hier oder in sonification file die zeiten anpassen
            #time.sleep(1) # measure every 2 seconds

            # TODO für PM2.5 anpassen
            pm2_5 = simulator.get_value('median_PM10')
            pm10 = simulator.get_value('median_PM10')
            sonify.play_sound(pm2_5, pm10)


    except KeyboardInterrupt:
        print('KeyboardInterrupt')
