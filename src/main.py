# coding=utf-8
import time
#import os
import simulation
import sonification

if __name__ ==  '__main__':
    print('Read and collect data. [Press Ctrl+C to exit!]')
    sampling_time = 2 # measure every 2 seconds

    simulator = simulation.Simulation()
    sonify = sonification.SonificationLogic(sampling_time)

    try:
        while True:
            time.sleep(sampling_time - 0.6)

            position = simulator.get_gps()
            # TODO für PM2.5 anpassen
            pm2_5 = simulator.get_value('median_PM10', position)
            pm10 = simulator.get_value('median_PM10', position)
            sonify.play_sound(pm2_5, pm10)

            print(position, pm2_5, pm10)


    except KeyboardInterrupt:
        print('KeyboardInterrupt')
