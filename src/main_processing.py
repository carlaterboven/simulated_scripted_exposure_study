import data_processer

raw_data_files = ['log_oct10.csv', 'log_oct11.csv',
                    'log_oct25.csv', 'log_oct26.csv', 'log_oct27.csv',
                    'log_nov1.csv', 'log_nov2.csv', 'log_nov4.csv',
                    'log_nov10.csv', 'log_nov11.csv', 'log_nov18.csv',
                    'log_dec7.csv', 'log_dec9.csv', 'log_dec12_1.csv', 'log_dec12_2.csv',
                    'log_dec13.csv', 'log_dec14.csv', 'log_dec15.csv'
                    ]

dataimport = data_processer.DataProcesser(raw_data_files)
data_grid = dataimport.run_complete_processing()
print(data_grid)
dataimport.export_grid_csv(data_grid)
