# coding=utf-8
#import pandas as pd
import time
#from multiprocessing import Process
import os
import simulation

def try_sensor_read(sensor):
    try:
        sensor.read_data()
    except KeyboardInterrupt:
        raise
    except:
        sensor.set_nan_data()




if __name__ ==  '__main__':
    print('Read and collect data. [Press Ctrl+C to exit!]')

    sim = simulation.Simulation()

    try:
        while True:
            # collect data for 3 seconds
            t_end = time.time() + 3
            while time.time() < t_end:
                time.sleep(1) # measure every second

            print(sim.get_value('median_PM10'))

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
