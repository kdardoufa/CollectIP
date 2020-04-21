# Description

Use Cisco Prime Infrastructure 3.5 REST APIs to get all the IP Addresses of the devices monitored by Prime Infrastructure. The script gathers the IP addresses based on the type of the device. It uses the following functions:

- getDeviceGroups(): Gets all the device type groups (Routers/4300/4200/Switches etc). 
- Remove Generic(): Any group that is considered as a parent directory is removed. Any device type that does not contain IP addresses in its inventory, is also removed. In our case these were devices Cisco4400.
- getIPs(): iterates through the groups and gathers the required information. If the group is empty, it moves on to the next group.

The information is written into a csv file, in order to be used as input into another application. The csv created has a naming convention of:
IP_current_date_time.csv. 
The primary goal was to gather the information and feed it into netbox.

# Configuration
The following global variables should be configured by the user, according to their environment.
- USERNAME: define REST API username
- PASSWORD: define REST API password
- PI_ADDRESS: define IP Address of Prime Infrastructure Server

# Technologies & Frameworks Used
Prime Infratructure APIs are used.
NO Third-Party products or Services are used.
The script is written in Python 3

# Installation
1.	Clone the repo
 - git clone https://github.com/kdardoufa/CollectIP.git

2.	cd into directory
 - cd CollectIP

3.	Create the virtual environment in a sub dir in the same directory
 - python3 -m venv venv

4.	Start the virtual environment and install requirements.txt
 - source venv/bin/activate
 - pip install -r requirements.txt

5.	Execute the script as any other Python script form console. 
 - python get_All_IPs_from_PI.py

# Known issues
-

# Author(s)
This project was written and is maintained by the following individuals
- Katerina Dardoufa (kdardoufa@gmail.com)






