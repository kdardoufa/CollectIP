from nornir import InitNornir
from nornir.plugins.functions.text import print_result,print_title
from nornir.plugins.tasks.networking import netmiko_send_command,netmiko_send_config
from datetime import datetime
import time
import netmiko
import re
import csv


device_list = []
ip_list =[]

timestr = time.strftime("%Y%m%d_%H%M")



print("On which devices should the command be run? Choose one of the following: Test, GetVPN, Switches, DataCenter")
device = input("Please state your answer:")
dev = device.strip().lower()
# if dev == "somegroup":
#   nr = InitNornir(config_file="somgroup.yaml")
if dev == "test":
    nr = InitNornir(config_file="test_router.yaml")
elif dev == "getvpn":
    nr = InitNornir(config_file="getvpn.yaml")
elif dev == "switches":
    nr = InitNornir(config_file="switches.yaml")
elif dev == "datacenter":
    nr = InitNornir(config_file="datacenter.yaml")


IP_file = "IP_"+dev+".csv"

print("Execution started: ", datetime.now())

if dev == "datacenter":
    info = nr.run(task=netmiko_send_command, command_string="show ip interface | in \"IP subnet\"")
    with open(IP_file, 'w') as filehandle:
        csvwriter = csv.writer(filehandle)
        for dev in nr.inventory.hosts.keys():
            i = 0
            output =  info[dev].result
            ip_addr = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{2}', output)
            for i in range(len(ip_addr)):
                csvwriter.writerow(ip_addr[i].split("/"))
            i += 1
else:
    info = nr.run(task=netmiko_send_command, command_string="show ip interface | in Internet")
    with open(IP_file, 'w') as filehandle:
        csvwriter = csv.writer(filehandle)
        for dev in nr.inventory.hosts.keys():
            i = 0
            output =  info[dev].result
            ip_addr = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{2}', output)
            for i in range(len(ip_addr)):
                csvwriter.writerow(ip_addr[i].split("/"))
            i += 1

nr.close_connections()
print("Execution ended: ", datetime.now())
