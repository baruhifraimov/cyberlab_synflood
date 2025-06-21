#!/usr/bin/env python3
from scapy.all import IP, TCP, send
import time
import csv

# Configuration parameters
TARGET_IP = "10.211.55.3"
TARGET_PORT = 80
TOTAL_PACKETS = 1000000
PAYLOAD_SIZE = 992  # Payload size in bytes

results = []
start_time = time.time()

# Open a text log file
txt_file = open("syns_results_p.txt", "w")

# Open a CSV file for logging results
csv_file = open("syns_results_p.csv", "w", newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Packet_Number", "Elapsed_Usec", "Second"])

# Loop through each packet (one at a time)
for packet_number in range(1, TOTAL_PACKETS + 1):
    t0 = time.time()
    # Create a single SYN packet with payload of the defined size
    pkt = IP(dst=TARGET_IP) / TCP(dport=TARGET_PORT, flags='S') / (b'A' * PAYLOAD_SIZE)
    # Send the packet immediately
    send(pkt, verbose=0)
    t1 = time.time()
    
    # Calculate elapsed time for sending this packet
    elapsed = t1 - t0
    elapsed_usec = elapsed * 1e6  # convert seconds to microseconds
    
    # Calculate current second index relative to the start
    second_index = int(time.time() - start_time)
    
    # Record the elapsed time for this packet
    results.append(elapsed)
    txt_file.write(f"Packet #{packet_number} | Elapsed: {elapsed_usec:.3f} µs | Second: {second_index}\n")
    csv_writer.writerow([packet_number, f"{elapsed_usec:.3f}", second_index])
    
    # Print progress every 10,000 packets
    if packet_number % 1000 == 0:
        print(f"Sent {packet_number} packets")

# Final overall statistics calculation
end_time = time.time()
total_duration = end_time - start_time
average_time = sum(results) / len(results)

txt_file.write(f"\nTotal time: {total_duration:.3f} sec\n")
txt_file.write(f"Average time per packet: {average_time * 1e6:.3f} µs\n")
csv_writer.writerow([])
csv_writer.writerow(["Total_Packets", len(results)])
csv_writer.writerow(["Total_Time_Seconds", f"{total_duration:.3f}"])
csv_writer.writerow(["Avg_Time_Per_Packet_Usec", f"{average_time * 1e6:.3f}"])

txt_file.close()
csv_file.close()
