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

timestr = time.strftime("%Y%m%d_%H%M")
Device_List = "DeviceList_"+timestr+".csv"


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
    # if thing in some_list: some_list.remove(thing)
    logging.info(" - Removing Generic Groups")
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
    if "Wireless Controller" in Group_List:
        Group_List.remove("Wireless Controller")
    new_Group_List = Group_List
    logging.info(" - Final groups ok... moving on")
    return(new_Group_List)
# End of Function


def getDevices(Group_List):
    logging.info(" - Getting Device Info")
    i = 0
    DeviceFileList = []
    NumOfGroups = len(Group_List)
    # remove last / from controller url
    new_url = controller_url[:-1]
    while i < NumOfGroups:
        group = Group_List[i]
        url = new_url + ".json?.full=true&.group=" + group + "&.maxResults=300"
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        r_json = response.json()
        count = (r_json.get("queryResponse", "")).get("@count", "")
        if count != 0:  # no devices in group
            logging.info(f' - Getting devices in group {group}')
            for entity in r_json["queryResponse"]["entity"]:
                Info = entity["inventoryDetailsDTO"]
                DeviceName = Info.get("summary").get("deviceName", "")
                IP_Addr = Info.get("summary").get("ipAddress", "")
                Location = Info.get("summary", "").get("location", "")
                if group != ("Unsupported Cisco Device"):
                    Model = Info["chassis"]["chassis"][0]["modelNr"]
                    SN = Info["chassis"]["chassis"][0]["serialNr"]
                else:
                    Model = "-"
                    SN = "-"
                new_row = [DeviceName, IP_Addr, Location, Model, SN]
                DeviceFileList.append(new_row)
            # Move on to next group
            i += 1
        # no devices in group
        else:
            # move on to next group
            i += 1
    logging.info(" - All info has been collected.\nEND")
    # open a file for writing
    DeviceList = open(Device_List, 'w')
    # create the csv writer object
    csvwriter = csv.writer(DeviceList)
    header = ["DeviceName", "IP_Address", "Location", "Type", "Serial Number"]
    csvwriter.writerow(header)
    for line in DeviceFileList:
        csvwriter.writerow(line)
    DeviceList.close()
    logging.info(" - All done.\nEND")
    return()
# End of function


def main():
    InitialGroups = getDeviceGroups()
    Groups = RemoveGeneric(InitialGroups)
    getDevices(Groups)
    return()


if __name__ == "__main__":
    main()


