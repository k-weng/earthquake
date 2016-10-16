import numpy as np
import numpy.linalg as la
from numpy.linalg import LinAlgError
from argparse import ArgumentParser
import os

def main():
    parser = createParser()
    options = parser.parse_args()

    # Directory of station data
    folder_name = options.ext + "_stations_data"

    # Initialize lists
    station_list = []
    event_list = []
    dt_list = []

    # Index variables for station and event indexes
    i = -1
    j = 0

    # Dictionary with delay time keys and values with corresponding station and event indexes
    d_ij = {}

    # Access each station file
    for filename in os.listdir(folder_name):
        file = filename.split(".")

        # Check for valid station file
        if len(file) != 7:
            continue

        # Get station name and append to station list
        station = ".".join(file[:2])
        i += 1
        station_list.append(station)

        # Read events of station
        for line in open(folder_name + "/" + filename):
            line_list = line.split()

            # Check for valid event
            if len(line_list) not in [3, 4] or line_list[-1] == "delay_times":
                continue

            # Get event name and corresponding delay time
            event = line_list[0] if len(line_list) == 3 else " ".join(line_list[:2])
            dt = float(line_list[2])

            # Check if event in event list
            for e in range(len(event_list)):

                # If event in event list, j is the index of the event in the list already
                if (event_list[e] == event):
                    j = e

            # If event not in event list, append event to the list and j is the index of the event
            if event not in event_list:
                event_list.append(event)
                j = len(event_list) - 1

            # Add delay time and corresponding (i, j) to dictionary
            d_ij[dt] = (i, j)

            # Add delay time to delay time list
            dt_list.append(dt)

    model_vector = modelVector(dt_list, station_list, event_list, d_ij)

    return model_vector

def modelVector(dt_list, station_list, event_list, d_ij):
    # Get length of the lists
    k = len(dt_list)
    n = len(station_list)
    m = len(event_list)

    # Change delay time list into a numpy vector
    dt_vector = np.array(dt_list)

    # Create the matrix G with k rows and n + m columns and fill with zeros
    g_dims = (k, n + m)
    g_matrix = np.zeros(g_dims)

    # Populate matrix G for each delay time row
    for d in range(len(dt_list)):

        # Set G(d, i) and G(d, n + j) to 1
        g_matrix[d, d_ij[dt_list[d]][0]] = 1
        g_matrix[d, n + d_ij[dt_list[d]][1]] = 1

    # Solve for model vector m in equation Gm = d where d is the vector of delay times
    # To solve, m = (G^T * G)^(-1) * G^T * d
    gT_mult_g = np.matmul(g_matrix.transpose(), g_matrix)
    gT_mult_dt = np.matmul(g_matrix.transpose(), dt_vector)

    # If (G^T * G) is singular and non-invertible, find the pseudoinverse
    try:
        gTg_inv = la.inv(gT_mult_g)
    except LinAlgError:
        gTg_inv = la.pinv(gT_mult_g)

    # 
    model_vector = np.matmul(gTg_inv, gT_mult_dt)

    # return model_vector
    return np.matmul(g_matrix, model_vector)


def createParser():
    # Add cmd line argument for choosing directory
    parser = ArgumentParser()

    parser.add_argument('-e','-ext', 
            dest='ext', help='file extension',
            metavar='EXT', required=True)

    return parser

if __name__ == '__main__':
    print main()
