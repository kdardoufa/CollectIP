import requests
import json
import csv
import logging
from requests.auth import HTTPBasicAuth
import time

requests.packages.urllib3.disable_warnings()

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='GetAll_IPs.log', level=logging.INFO)

# Define Global Variables
USERNAME = "username"  # define  REST API username
PASSWORD = "password"  # define REST API passowrd
PI_ADDRESS = "ip_address"  # define IP Address of Prime Infrastructure Server

controller_url = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails/"
Group_List = []
output = []
intf_list = []

timestr = time.strftime("%Y%m%d_%H%M")
IP_file = "IP_"+timestr+".csv"


def getDeviceGroups():
    logging.info(" - Getting all device groups")
    url = "https://"+PI_ADDRESS+"/webacs/api/v2/data/DeviceGroups.json?.full=true"
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    r_json = response.json()
    Group_List = []
    group = "dummy value"
    for entity in r_json['queryResponse']['entity']:
        group = entity["deviceGroupsDTO"]["groupName"]
        Group_List.append(group)
    return(Group_List)
    Group_List.append(group)
    logging.info(f' - {group} added to list')
    logging.info(" - Initial groups ok... moving on")
    return(Group_List)
# End of Function


def RemoveGeneric(Group_List):
    #if thing in some_list: some_list.remove(thing)
    logging.info("Removing Generic Groups")
    if "Device Type" in Group_List:
        Group_List.remove("Device Type")
    if "Routers" in Group_List:
        Group_List.remove("Routers")
    if "Security and VPN" in Group_List:
        Group_List.remove("Security and VPN")
    if "Switches and Hubs" in Group_List:
        Group_List.remove("Switches and Hubs")
    if "Unified AP" in Group_List:
        Group_List.remove("Unified AP")
    if "Unsupported Cisco Device" in Group_List:
        Group_List.remove("Unsupported Cisco Device")
    if "Wireless Conteroller" in Group_List:
        Group_List.remove("Wireless Controller")
    if "Cisco 4400 Series Integrated Services Routers" in Group_List:
        Group_List.remove("Cisco 4400 Series Integrated Services Routers")
    new_Group_List = Group_List
    logging.info("Final groups ok... moving on")
    return(new_Group_List)
# End of Function


def getIPs(Group_List):
    logging.info("Getting Device IPs")
    #i = 0
    #NumOfGroups = len(Group_List)
    # while i < NumOfGroups:
    for group in Group_List:
        #group = Group_List[i]
        url = controller_url + ".json?.full=true&.group=" + group + "&.maxResults=1000"
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        r_json = response.json()
        count = (r_json.get("queryResponse", "")).get("@count", "")
        if count != 0:
            logging.info(f'Getting IPs for devices in group {group}')
            if group != "Unsupported Cisco Device":
                for Info in r_json['queryResponse']['entity']:
                    intf_list = Info["inventoryDetailsDTO"]["ipInterfaces"]["ipInterface"]
                    #num_of_interfaces = len(intf_list)
                    for interface in intf_list:
                        ip = interface["ipAddress"].get("address", "")
                        mask = interface.get("prefixLength", "")
                        ip_and_mask = str(ip) + "/" + str(mask)
                        output.append(ip_and_mask)
            else:
                for Info in r_json['queryResponse']['entity']:
                    ip = Info["inventoryDetailsDTO"]["summary"]["ipAddress"]
                    mask = "24"
                    ip_and_mask = str(ip) + "/" + str(mask)
                    output.append(ip_and_mask)
            # Move on to next group
# If no devices in Group then move on
        else:
            continue
# for loop ends
# open a file for writing
    IPList = open(IP_file, 'w')
# create the csv writer object
    csvwriter = csv.writer(IPList)
    csvwriter.writerows(zip(output))
    IPList.close()
    return()
# End of function

# Main Function


def main():
    logging.info("Begin")
    #print("Execution started: ", datetime.now())
    InitialGroups = getDeviceGroups()
    Groups = RemoveGeneric(InitialGroups)
    getIPs(Groups)
    #print("Execution Ended: ", datetime.now())
    logging.info("End")
    return()


if __name__ == "__main__":
    main()
