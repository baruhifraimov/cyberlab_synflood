#define _POSIX_C_SOURCE 199309L
#define __FAVOR_BSD
#define _DEFAULT_SOURCE

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netinet/ip.h>
#include <time.h>
#include <math.h>

#define DEST_PORT 80
#define PACKETS_PER_LOOP 10000
#define LOOPS 100
#define MAX_SECONDS 3600  // Enough for one hour of runtime
#define PAYLOAD_SIZE 992  // Payload size in bytes

// Checksum function for computing the checksum value
unsigned short checksum(unsigned short *ptr, int nbytes) {
    long sum = 0;
    unsigned short oddbyte;
    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }
    if (nbytes == 1) {
        oddbyte = 0;
        *((unsigned char *)&oddbyte) = *(unsigned char *)ptr;
        sum += oddbyte;
    }
    sum = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

// Compute the time difference in microseconds
double timeval_diff_usec(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) * 1e6 +
           (end.tv_nsec - start.tv_nsec) / 1e3;
}

int main(int argc, char *argv[]) {
    const char *target_ip = "10.211.55.3";
    if (argc >= 2) {
        target_ip = argv[1];
    }

    // Create a raw socket
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (sock < 0) {
        perror("Socket creation failed (run with sudo?)");
        return 1;
    }

    int one = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("setsockopt failed");
        close(sock);
        return 1;
    }

    struct sockaddr_in target_addr;
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(DEST_PORT);
    target_addr.sin_addr.s_addr = inet_addr(target_ip);

    // Allocate memory for the packet buffer, which includes IP header, TCP header, and payload
    char packet[4096];
    int packet_size = sizeof(struct iphdr) + sizeof(struct tcphdr) + PAYLOAD_SIZE;
    
    // Open log and CSV output files
    FILE *log = fopen("syns_results_c.txt", "w");
    FILE *csv = fopen("syns_results_c.csv", "w");
    if (!log || !csv) {
        perror("Failed to open output files");
        return 1;
    }
    
    // Write CSV header
    fprintf(csv, "Packet_Number,Elapsed_Usec,Second\n");

    double time_per_second[MAX_SECONDS] = {0};
    int packets_per_second[MAX_SECONDS] = {0};

    struct timespec global_start, global_end;
    clock_gettime(CLOCK_MONOTONIC, &global_start);

    // Loop to send packets
    for (int loop = 0; loop < LOOPS; loop++) {
        for (int i = 0; i < PACKETS_PER_LOOP; i++) {
            // Clear the packet buffer for each packet
            memset(packet, 0, sizeof(packet));
            
            // Set pointers for the IP header, TCP header, and payload
            struct iphdr *ip = (struct iphdr *)packet;
            struct tcphdr *tcp = (struct tcphdr *)(packet + sizeof(struct iphdr));
            char *payload = packet + sizeof(struct iphdr) + sizeof(struct tcphdr);
            
            // Fill the payload with the character 'A'
            memset(payload, 'A', PAYLOAD_SIZE);

            // Fill the IP header
            ip->ihl = 5;
            ip->version = 4;
            ip->tos = 0;
            ip->tot_len = htons(packet_size);  // Total length includes IP header, TCP header, and payload
            ip->id = htons(rand() % 65535);
            ip->frag_off = 0;
            ip->ttl = 64;
            ip->protocol = IPPROTO_TCP;
            ip->saddr = inet_addr("1.2.3.4");
            ip->daddr = inet_addr(target_ip);
            ip->check = checksum((unsigned short *)ip, sizeof(struct iphdr));
            
            // Fill the TCP header
            tcp->source = htons(rand() % 65535);
            tcp->dest = htons(DEST_PORT);
            tcp->seq = htonl(0);
            tcp->ack_seq = 0;
            tcp->doff = 5;  // TCP header length in 32-bit words
            tcp->syn = 1;
            tcp->window = htons(5840);
            tcp->check = 0;  // Will be calculated later

            // Build pseudo header for TCP checksum calculation, including the payload
            struct pseudo_header {
                unsigned int src_addr;
                unsigned int dst_addr;
                unsigned char placeholder;
                unsigned char protocol;
                unsigned short tcp_length;
            } pseudo;

            char pseudo_packet[1024];
            pseudo.src_addr = ip->saddr;
            pseudo.dst_addr = ip->daddr;
            pseudo.placeholder = 0;
            pseudo.protocol = IPPROTO_TCP;
            pseudo.tcp_length = htons(sizeof(struct tcphdr) + PAYLOAD_SIZE);
            
            // Copy pseudo header, TCP header, and payload into one buffer
            memcpy(pseudo_packet, &pseudo, sizeof(pseudo));
            memcpy(pseudo_packet + sizeof(pseudo), tcp, sizeof(struct tcphdr));
            memcpy(pseudo_packet + sizeof(pseudo) + sizeof(struct tcphdr), payload, PAYLOAD_SIZE);
            
            // Compute TCP checksum over the pseudo packet
            tcp->check = checksum((unsigned short *)pseudo_packet,
                                  sizeof(pseudo) + sizeof(struct tcphdr) + PAYLOAD_SIZE);
            
            // Measure time and send the packet
            struct timespec t0, t1;
            // Sleep for 1 microsecond
            // usleep(1);
            clock_gettime(CLOCK_MONOTONIC, &t0);
            ssize_t sent = sendto(sock, packet, packet_size, 0,
                                  (struct sockaddr *)&target_addr, sizeof(target_addr));
            clock_gettime(CLOCK_MONOTONIC, &t1);
            
            if (sent > 0) {
                double elapsed_usec = timeval_diff_usec(t0, t1);
                double elapsed_sec = (t0.tv_sec - global_start.tv_sec) + (t0.tv_nsec - global_start.tv_nsec) / 1e9;
                int second_index = (int)floor(elapsed_sec);
                int packet_index = loop * PACKETS_PER_LOOP + i + 1;
                
                // Write to the TXT log file
                fprintf(log, "Packet #%d | Elapsed: %.3f µs | Second: %d\n",
                        packet_index, elapsed_usec, second_index);
                // Write to the CSV file
                fprintf(csv, "%d,%.3f,%d\n", packet_index, elapsed_usec, second_index);
                
                if (second_index < MAX_SECONDS) {
                    time_per_second[second_index] += elapsed_usec;
                    packets_per_second[second_index]++;
                }
            }
        }
        printf("Completed loop %d/%d\n", loop + 1, LOOPS);
    }
    
    clock_gettime(CLOCK_MONOTONIC, &global_end);
    double total_seconds = (global_end.tv_sec - global_start.tv_sec) +
                           (global_end.tv_nsec - global_start.tv_nsec) / 1e9;
    
    double total_time = 0.0;
    int total_packets = 0;
    for (int i = 0; i < MAX_SECONDS; i++) {
        if (packets_per_second[i] > 0) {
            double avg_usec = time_per_second[i] / packets_per_second[i];
            fprintf(log, "SECOND %d: AVG_TIME_PER_PACKET_US %.3f\n", i, avg_usec);
            total_time += time_per_second[i];
            total_packets += packets_per_second[i];
        }
    }
    
    fprintf(log, "TOTAL_PACKETS %d\n", total_packets);
    fprintf(log, "TOTAL_TIME_SECONDS %.3f\n", total_seconds);
    fprintf(log, "AVG_TIME_PER_PACKET_US %.3f\n", total_time / total_packets);
    
    fclose(log);
    fclose(csv);
    close(sock);
    printf("Done. Total packets sent: %d\n", total_packets);
    return 0;
}

