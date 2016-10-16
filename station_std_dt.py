import glob
import os
import errno
import numpy as np
import datetime
from argparse import ArgumentParser

def main():
    parser = createParser()
    options = parser.parse_args()

    stations = {}
    now = datetime.datetime.now()

    for file in glob.glob("*." + options.ext):
        for line in open(file):
            line_list = line.split()
            if len(line_list) == 9:
                station_name  = line_list[0].replace('\x00', '')
                std = float(line_list[2])
                delay_time = float(line_list[8])
                if station_name not in stations.keys():
                    stations[station_name] = [[file], [std], [delay_time]]
                else: 
                    stations[station_name][0].append(file)
                    stations[station_name][1].append(std)
                    stations[station_name][2].append(delay_time)

    for station in stations.keys():
        output_filename = options.ext + "_stations_data/" + station + ".stdmean.of.stddelay." + now.strftime("%Y%m%d") + ".txt"
        if not os.path.exists(os.path.dirname(output_filename)):
            try:
                os.mkdir(os.path.dirname(output_filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        col_names = "filename,\tstd,\tdelay_times\n"
        with open(output_filename, 'w') as f:
            f.write("Created on " + now.strftime("%b %d, %Y %H:%M") + '\n')
            f.write(col_names)

            data = stations[station]
            file = data[0]
            stds = data[1]
            delay_times = data[2]
            for i in range(len(stds)):
                output_line = file[i] + '\t' + str(stds[i]) + '\t' + str(delay_times[i]) + '\n'
                f.write(output_line)
            stdSTD = np.std(stds)
            meanSTD = np.mean(stds)
            stdDelay = np.std(delay_times)
            meanDelay = np.mean(delay_times)

            f.write("STD_of_std: " + '{:.4f}'.format(stdSTD) + '\n')
            f.write("Mean_std: " + '{:.4f}'.format(meanSTD) + '\n')
            f.write("STD_of_delay_times: " + '{:.4f}'.format(stdDelay) + '\n')
            f.write("Mean_delay_times: " + '{:.4f}'.format(meanDelay) + '\n')

def createParser():
    # Add cmd line argument for choosing directory
    parser = ArgumentParser()

    parser.add_argument('-e','-ext', 
            dest='ext', help='file extension',
            metavar='EXT', required=True)

    return parser

if __name__ == '__main__':
    main()