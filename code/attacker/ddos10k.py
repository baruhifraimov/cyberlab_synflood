from scapy.all import IP, TCP, send
import time
import csv
import math

# Configuration parameters
TARGET_IP = "10.211.55.3"
TARGET_PORT = 80
PACKETS_PER_ITERATION = 10000
ITERATIONS = 100
PAYLOAD_SIZE = 992  # Payload size in bytes

results = []
start_time = time.time()

# Open a text log file
txt_file = open("syns_results_p.txt", "w")

# Open a CSV file for logging results
csv_file = open("syns_results_p.csv", "w", newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Packet_Number", "Elapsed_Usec", "Second"])

packet_number = 1  # Counter for the total number of packets

for iteration in range(ITERATIONS):
    packets = []
    t0 = time.time()
    # Create packets for this iteration with a configurable payload
    for _ in range(PACKETS_PER_ITERATION):
        pkt = IP(dst=TARGET_IP) / TCP(dport=TARGET_PORT, flags='S') / (b'A' * PAYLOAD_SIZE)
        packets.append(pkt)

    # Send the batch of packets
    send(packets, verbose=0)
    t1 = time.time()
    total_elapsed = t1 - t0
    elapsed_per_packet = total_elapsed / PACKETS_PER_ITERATION
    elapsed_usec = elapsed_per_packet * 1e6  # Convert seconds to microseconds

    current_time = time.time()
    second_index = int(current_time - start_time)

    # Log the results for each packet sent in this iteration
    for _ in range(PACKETS_PER_ITERATION):
        results.append(elapsed_per_packet)
        txt_file.write(f"Packet #{packet_number} | Elapsed: {elapsed_usec:.3f} µs | Second: {second_index}\n")
        csv_writer.writerow([packet_number, f"{elapsed_usec:.3f}", second_index])
        packet_number += 1

    print(f"Iteration {iteration+1}/{ITERATIONS} done")

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
