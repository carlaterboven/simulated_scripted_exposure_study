import data_processer

raw_data_files = ['log_oct11.csv', 'log_oct25.csv', 'log_oct26.csv', 'log_oct27.csv',
                    'log_nov1.csv', 'log_nov2.csv', 'log_nov4.csv',
                    'log_nov10.csv', 'log_nov11.csv', 'log_nov18.csv']
atmotube_data_files = ['atmotube_oct11.csv',
                       'atmotube_oct25.csv', 'atmotube_oct26.csv', 'atmotube_oct27.csv',
                       'atmotube_nov1.csv', 'atmotube_nov2.csv', 'atmotube_nov4.csv',
                       'atmotube_nov10.csv', 'atmotube_nov11.csv', 'atmotube_nov18.csv']

dataimport = data_processer.DataProcesser(raw_data_files, atmotube_data_files)
pm10_grid = dataimport.run_complete_processing()
print(pm10_grid)
dataimport.export_grid_csv(pm10_grid)
