import numpy as np
import numpy.linalg as la
import errno
from numpy.linalg import LinAlgError
from argparse import ArgumentParser
import os

# NOTE: If jlist and ilist are desired, uncomment lines 23, 24, 48, 81, 104, 105

def main():
    parser = createParser()
    options = parser.parse_args()

    # Directory of station data
    folder_name = options.ext + "_stations_data"

    # Initialize lists
    stations = []
    events = []
    dtimes = []
    # If necessary, uncomment the two lines below for ilist and jlist
    # ilist = []
    # jlist = []

    # Index variables for station and event indexes
    i = -1
    j = 0

    # Dictionary with delay time keys and values with corresponding station and event indexes
    # Example: dtimes[-0.1234] => (25, 10) - station at index 25 of stations and event at index 10 of events 
    dtimes_ij = {}

    # Access each station file
    for filename in os.listdir(folder_name):
        file = filename.split(".")

        # Check for valid station file
        if len(file) != 7:
            continue

        # Get station name and append to station list
        station = ".".join(file[:2])
        stations.append(station)

        i += 1
        # Add i into ilist, if necessary uncomment line below
        # ilist.append(i)

        # Read events of station
        for line in open(folder_name + "/" + filename):
            line_list = line.split()

            # Check for valid event
            if len(line_list) not in [3, 4] or line_list[-1] == "delay_times":
                continue

            # Get event name and corresponding delay time
            event = line_list[0] if len(line_list) == 3 else " ".join(line_list[:2])
            dt = float(line_list[2]) if len(line_list) == 3 else float(line_list[3])

            # Check if event in event list
            for e in range(len(events)):

                # If event in event list, j is the index of the event in the list
                if (events[e] == event):
                    j = e

            # If event not in event list, append event to the list and j is the index of the event
            if event not in events:
                events.append(event)
                j = len(events) - 1

            # Add delay time and corresponding (i, j) to dictionary
            dtimes_ij[dt] = (i, j)

            # Add delay time to delay time list
            dtimes.append(dt)

            # Add j into jlist, if necessary uncomment line below
            # jlist.append(j)

        

    m = modelVector(dtimes, stations, events, dtimes_ij)

    # Check if output folder already exists, and if not create it
    output_dir = options.ext + "_analysis_outputs/"
    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Write lists to separate files
    header = output_dir + options.ext
    writeVector(header + "_model_vector.txt", m)
    writeList(header + "_stations.txt", stations)
    writeList(header + "_events.txt", events)
    writeDict(header + "_dtimes.txt", dtimes_ij)

    # If ilist and jlist are desired, uncomment next two lines below
    # writeList(header + "_ilist.txt", ilist)
    # writeList(header + "_jlist.txt", jlist)


def modelVector(dtimes, stations, events, dtimes_ij):
    # Get length of the lists
    k = len(dtimes)
    n = len(stations)
    m = len(events)

    # Change delay time list into a numpy vector
    dt_vector = np.array(dtimes)

    # Create the matrix G with k rows and n + m columns and fill with zeros
    g_dims = (k, n + m)
    g_matrix = np.zeros(g_dims)

    # Populate matrix G for each delay time row
    for d in range(len(dtimes)):

        # Set G(d, i) and G(d, n + j) to 1
        g_matrix[d, dtimes_ij[dtimes[d]][0]] = 1
        g_matrix[d, n + dtimes_ij[dtimes[d]][1]] = 1

    # Solve for model vector m in equation Gm = d where d is the vector of delay times
    # To solve, m = (G^T * G)^(-1) * G^T * d
    gT_mult_g = np.matmul(g_matrix.transpose(), g_matrix)

    # If (G^T * G) is singular and non-invertible, find the pseudoinverse
    try:
        gTg_inv = la.inv(gT_mult_g)
    except LinAlgError:
        gTg_inv = la.pinv(gT_mult_g)

    gT_mult_dt = np.matmul(g_matrix.transpose(), dt_vector)

    return np.matmul(gTg_inv, gT_mult_dt)

def writeVector(filename, vector):
    with open(filename, 'w') as f:
        for val in np.nditer(vector):
            output = str(val) + "\n"
            f.write(output)

def writeDict(filename, dict):
    with open(filename, 'w') as f:
        f.write("dtimes\tstation i\tevent j\n")
        for dt in dict:
            output = "%s\t%s\t%s\n" % (dt, dict[dt][0], dict[dt][1])
            f.write(output)

def writeList(filename, list):
    with open(filename, 'w') as f:
        for val in list:
            output = str(val) + "\n"
            f.write(output)

def createParser():
    # Add cmd line argument for choosing directory
    parser = ArgumentParser()

    parser.add_argument('-e','-ext', 
            dest='ext', help='file extension',
            metavar='EXT', required=True)

    return parser

if __name__ == '__main__':
    main()
