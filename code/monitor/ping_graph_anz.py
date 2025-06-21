#!/usr/bin/env python3
"""
This script analyzes packet RTT data from updated CSV files produced by the monitor.
It creates a histogram showing the RTT (in seconds),
with a logarithmic y-axis for the number of packets per RTT group.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_rtt_data(filename):
    """
    Load RTT data from a CSV file.
    Converts 'Timeout' values to 999, parses the rest as float,
    and converts the values from milliseconds to seconds.
    Returns the values as float (in seconds).
    """
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Failed to read {filename}: {e}")
        return None
    
    if "RTT (ms)" not in df.columns:
        print(f"'RTT (ms)' column not found in {filename}.")
        return None

    # Replace "Timeout" strings with 999
    df["RTT (ms)"] = df["RTT (ms)"].replace("Timeout", "999")

    # Convert RTT column to numeric (float), drop invalid values
    rtt_ms = pd.to_numeric(df["RTT (ms)"], errors='coerce').dropna()
    
    # Convert milliseconds to seconds
    rtt_sec = rtt_ms / 1000.0
    return rtt_sec

def plot_histogram(rtt_data, title, output_file):
    """
    Plot a histogram of RTT (in seconds) with a log-scaled y-axis.
    """
    plt.figure(figsize=(10, 6))
    # Define bins from the minimum to maximum RTT (in seconds)
    bins = np.linspace(rtt_data.min(), rtt_data.max(), 50)
    
    plt.hist(rtt_data, bins=bins, edgecolor='black')
    plt.xlabel("RTT (Seconds)", fontsize=12)
    plt.ylabel("Number of Packets (Log Scale)", fontsize=12)
    plt.yscale("log")
    plt.title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    c_file = "pings_results_c.csv"
    p_file = "pings_results_p.csv"

    # C attack
    data_c = load_rtt_data(c_file)
    if data_c is not None and not data_c.empty:
        print(f"C Attack: Loaded {len(data_c)} RTT records.")
        plot_histogram(data_c, "RTT Distribution for C Attack", "c_rtt_distribution.png")
    else:
        print("No valid RTT data found for C attack.")

    # Python attack
    data_p = load_rtt_data(p_file)
    if data_p is not None and not data_p.empty:
        print(f"Python Attack: Loaded {len(data_p)} RTT records.")
        plot_histogram(data_p, "RTT Distribution for Python Attack", "python_rtt_distribution.png")
    else:
        print("No valid RTT data found for Python attack.")

if __name__ == "__main__":
    main()
