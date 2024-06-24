# Attacking-Foscam
Final project code for lab on offensive computer security

# Brute_Force
This code helps the attacker crack weak username and password combinations, with the use of two text files that contain common used usernames and passwords.
It is only necessary to provide the IP address of the Foscam camera that is to be brute forced.
(Note that the code is written for specifically Foscam C1 V3 IP camera)

# MITM_RTSP
This code helps the attacker perform a man in the middle attack when the IP address of two targets are given.
With the credentials obtained from the brute force, an RTSP infiltration to the live stream can be done also the video footage can be downloaded with the use of same credentials. (IP address should also be provided)

# DoS 
This code helos the attacker to exhaust the victim device with SYN flood on the cameras open ports. In the code the static ports are written inside a list however, the camera has a dynamic port that changes daily thus using an nmap scan to find the port an adding to the "ports" list may be useful. The code is specifically written to work on Foscam C1 V3 cameras. 



