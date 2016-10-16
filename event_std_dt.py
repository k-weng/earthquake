import glob
import datetime
import numpy as np
from argparse import ArgumentParser

def main():
    parser = createParser()
    options = parser.parse_args()

    now = datetime.datetime.now()
    output_filename = options.ext + ".event.stdmean.of.stddelay." + now.strftime("%Y%m%d") + ".txt"
    col_names = "filename, mean of std, std of delay_times, mean of delay_times\n"

    with open(output_filename, 'w') as f:
        f.write("Created on " + now.strftime("%b %d, %Y %H:%M") + '\n')
        f.write(col_names)

        for file in glob.glob("*." + options.ext):
            std_list = []
            delay_times_list = []
            output_filename = file
            for line in open(file):
                line_list = line.split()
                if len(line_list) == 9:
                    std_list.append(float(line_list[2]))
                    delay_times_list.append(float(line_list[8]))

            output_line = output_filename  + '\t'
            output_line += '{:.4f}'.format(np.mean(std_list)) + '\t'
            output_line += '{:.4f}'.format(np.std(delay_times_list)) + '\t' + '{:.4f}'.format(np.mean(delay_times_list)) +'\n'
            f.write(output_line)

def createParser():
    # Add cmd line argument for choosing directory
    parser = ArgumentParser()

    parser.add_argument('-e','-ext', 
            dest='ext', help='file extension',
            metavar='EXT', required=True)

    return parser

if __name__ == '__main__':
    main()