# coding=utf-8
import time
import simulation
import sonification

if __name__ ==  '__main__':
    print('Read and sonify data. [Press Ctrl+C to exit!]')
    sampling_time = 2 # measure every 2 seconds

    simulator = simulation.Simulation(live_gps = False)
    sonify = sonification.SonificationLogic(sampling_time)

    try:
        while True:
            position = simulator.get_gps()

            pm2_5 = simulator.get_value('PM2.5', position)
            pm10 = simulator.get_value('PM10', position)
            sonify.play_sound(pm2_5, pm10)

            #print('position, pm2.5, pm10: ', position, pm2_5, pm10)

            time.sleep(sampling_time)


    except KeyboardInterrupt:
        print('KeyboardInterrupt')
