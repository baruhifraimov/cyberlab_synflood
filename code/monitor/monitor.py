#!/usr/bin/env python3
import socket
import time
import csv

# Configuration defaults
TARGET_IP = "10.211.55.3"
PORT = 80
INTERVAL = 5      # Ping every 5 seconds
TOTAL_PINGS = 999   # Total number of pings

def perform_ping():
    """
    Perform a single ping by attempting a TCP connection to TARGET_IP:PORT
    and measure the round-trip time (RTT) in milliseconds.
    Returns the RTT or None if the ping times out.
    """
    try:
        start_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            s.connect((TARGET_IP, PORT))
        end_time = time.time()
        return (end_time - start_time) * 1000  # Convert to milliseconds
    except Exception:
        return None

def write_txt(filename, results, total_time, avg_send_time):
    """
    Write the ping results to a TXT file.
    Includes a header, each ping result, average RTT,
    total execution time, and average time per packet.
    """
    valid_results = [r for r in results if r is not None]
    avg_rtt = sum(valid_results) / len(valid_results) if valid_results else 0
    with open(filename, "w") as f:
        f.write("Ping Results\n")
        f.write("============\n")
        for idx, r in enumerate(results, start=1):
            if r is not None:
                f.write(f"Ping {idx}: {r:.2f} ms\n")
            else:
                f.write(f"Ping {idx}: Request timed out\n")
        f.write("\n")
        f.write(f"Average RTT: {avg_rtt:.2f} ms\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Total execution time: {total_time:.2f} seconds\n")
        f.write(f"Average time per packet: {avg_send_time:.2f} seconds\n")

def write_csv(filename, results, total_time, avg_send_time):
    """
    Write the ping results to a CSV file.
    Includes headers, each ping result, average RTT,
    total execution time, and average time per packet.
    """
    valid_results = [r for r in results if r is not None]
    avg_rtt = sum(valid_results) / len(valid_results) if valid_results else 0
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Ping Number", "RTT (ms)"])
        for idx, r in enumerate(results, start=1):
            if r is not None:
                writer.writerow([idx, f"{r:.2f}"])
            else:
                writer.writerow([idx, "Timeout"])
        writer.writerow([])
        writer.writerow(["Average RTT", f"{avg_rtt:.2f}"])
        writer.writerow(["Total Execution Time (s)", f"{total_time:.2f}"])
        writer.writerow(["Average Time per Packet (s)", f"{avg_send_time:.2f}"])

def main():
    # Ask once for the attack mode before running
    mode = input("Select monitor mode (c for C attack, p for Python attack): ").strip().lower()
    if mode not in ["c", "p"]:
        print("Invalid mode selected. Defaulting to Python attack mode.")
        mode = "p"

    print("Starting monitor. Press Ctrl+C at any time to stop.")
    results = []
    start_time = time.time()  # Record the start time of the monitoring session

    try:
        for i in range(TOTAL_PINGS):
            rtt = perform_ping()
            results.append(rtt)
            if rtt is not None:
                print(f"Ping {i+1}: {rtt:.2f} ms")
            else:
                print(f"Ping {i+1}: Request timed out")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user. Saving results so far...")
    finally:
        total_time = time.time() - start_time
        avg_send_time = total_time / len(results) if results else 0

        # Choose output filenames based on the mode
        if mode == "c":
            txt_filename = "pings_results_c.txt"
            csv_filename = "pings_results_c.csv"
        else:
            txt_filename = "pings_results_p.txt"
            csv_filename = "pings_results_p.csv"

        write_txt(txt_filename, results, total_time, avg_send_time)
        write_csv(csv_filename, results, total_time, avg_send_time)
        print(f"Results saved to {txt_filename} and {csv_filename}")

if __name__ == "__main__":
    main()
