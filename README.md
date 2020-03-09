# CollectIP
This code is used to extract IP addresses in the infrastructure via two methods:

-	Using REST APIs to collect IP Address from Prime Infrastructure
-	Using Nornir to collect live data from your infrastructure

Make sure you edit the contents of the .py files to set the name of your PI server and the credentials for the API user.

Get_All_IPs_from_PI.py
The script includes a couple of functions. 
- getDeviceGroups gets a list of all the device type groups in Prime.
- removeGeneric removes device types that act as "Titles" as well as device types that do not contain ip address in their inventory output.
- getIPs goes through the inventory details of all devices in the groups and returns a csv with the information

Get_IPs_Nornir.py
The user can either enter a group of devices to get the IP information (appropriate host files need to be created) or it can run for the whole infrastructure with a bit of tweaking.




