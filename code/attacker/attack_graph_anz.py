#!/usr/bin/env python3
"""
This script processes packet sending time data from CSV files for two attack types (C and Python).
It calculates basic statistics (mean and standard deviation) and creates histograms of the packet sending time values.
The x-axis shows the time taken to send a packet in seconds, and the y-axis shows the number of packets (on a logarithmic scale).
Each histogram is saved as an image file.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_packet_data(filename):
    """
    Loads packet sending time data from a CSV file.
    
    The CSV is expected to contain columns: 'Packet_Number', 'Elapsed_Usec', 'Second'.
    
    Parameters:
        filename (str): Path to the CSV file.
    
    Returns:
        pd.Series: A series containing the Elapsed_Usec values (packet sending times in microseconds).
    """
    try:
        # Read the CSV file
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None
    
    # Ensure the "Elapsed_Usec" column exists
    if "Elapsed_Usec" not in df.columns:
        print(f"Column 'Elapsed_Usec' not found in {filename}.")
        return None
    
    # Return the Elapsed_Usec column as a numeric series
    return pd.to_numeric(df["Elapsed_Usec"], errors='coerce').dropna()

def plot_packet_time_histogram(data, title, output_filename, bins=20):
    """
    Creates and saves a histogram for packet sending time data.
    
    The values in 'data' are converted from microseconds to seconds.
    
    Parameters:
        data (pd.Series): The Elapsed_Usec data (time taken to send a packet in microseconds).
        title (str): Title for the histogram.
        output_filename (str): The filename for the saved image.
        bins (int): Number of bins for the histogram.
    """
    # Convert the data from microseconds to seconds.
    data_seconds = data / 1e6

    plt.figure()
    
    # Create equally spaced bin edges from the minimum to the maximum packet sending time (in seconds).
    bin_edges = np.linspace(data_seconds.min(), data_seconds.max(), bins + 1)
    
    # Plot the histogram with black bin edges.
    plt.hist(data_seconds, bins=bin_edges, edgecolor='black')
    
    # Label the x-axis as seconds.
    plt.xlabel("Time to Send a Packet (Seconds)")
    plt.ylabel("Number of Packets")
    
    # Set y-axis to logarithmic scale for better visualization.
    plt.yscale("log")
    
    # Set the plot title.
    plt.title(title)
    
    # Save the histogram image file.
    plt.savefig(output_filename)
    plt.close()

def main():
    """
    Main function to load packet data, calculate statistics, and generate histograms.
    
    It processes two datasets:
      - 'syns_results_c.csv' for the C attack.
      - 'syns_results_p.csv' for the Python attack.
    """
    # Define the filenames for the CSV files.
    c_file = "syns_results_c.csv"
    p_file = "syns_results_p.csv"
    
    # Process packet sending time data for the C attack.
    data_c = load_packet_data(c_file)
    if data_c is not None and not data_c.empty:
        mean_c = data_c.mean() / 1e6  # convert to seconds
        std_c = data_c.std() / 1e6    # convert to seconds
        print("C Attack Packet Sending Time Data Statistics:")
        print(f"Mean Time: {mean_c:.6f} s")
        print(f"Standard Deviation: {std_c:.6f} s")
        # Create and save histogram for the C attack.
        plot_packet_time_histogram(data_c, "Packet Sending Time for C Attack", "Packet_Time_C.png")
    else:
        print("No valid data found for the C attack.")
    
    # Process packet sending time data for the Python attack.
    data_p = load_packet_data(p_file)
    if data_p is not None and not data_p.empty:
        mean_p = data_p.mean() / 1e6  # convert to seconds
        std_p = data_p.std() / 1e6    # convert to seconds
        print("Python Attack Packet Sending Time Data Statistics:")
        print(f"Mean Time: {mean_p:.6f} s")
        print(f"Standard Deviation: {std_p:.6f} s")
        # Create and save histogram for the Python attack.
        plot_packet_time_histogram(data_p, "Packet Sending Time for Python Attack", "Packet_Time_Python.png")
    else:
        print("No valid data found for the Python attack.")

if __name__ == '__main__':
    main()
