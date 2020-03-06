import requests
import json
import csv
import logging
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime

requests.packages.urllib3.disable_warnings()

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='GetAll_IPs.log', level=logging.INFO)

controller_url = "https://10.130.107.30/webacs/api/v4/data/InventoryDetails/"
Group_List = []
output = []
intf_list = []

timestr = time.strftime("%Y%m%d_%H%M")
IP_file = "IP_"+timestr+".csv"


def getDeviceGroups():
    logging.info("Getting all device groups")
    url = "https://10.130.107.30/webacs/api/v2/data/DeviceGroups.json"
    response = requests.get(url, auth=HTTPBasicAuth("username", "password"), verify=False)
    r_json = response.json()
    Group_List = []
    group = "dummy value"
    for entity in r_json['queryResponse']['entityId']:
        for value in entity.values():
            if "https" in value:
                new_url = value + ".json"
                # print(new_url)
                group_response = requests.get(
                    new_url, auth=HTTPBasicAuth("username", "password"), verify=False)
                group_json = group_response.json()
                # print(new_url)
                dev_dict = group_json["queryResponse"]["entity"][0]
                deviceGroupsDTO = dev_dict.get("deviceGroupsDTO", "None")
                group = deviceGroupsDTO.get("groupName", "")
                time.sleep(1)
                Group_List.append(group)
                logging.info(f'{group} added to list')
    logging.info("Initial groups ok... moving on")
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
        Group_List.remove("Wireless Contorller")
    if "Cisco 4400 Series Integrated Services Routers" in Group_List:
        Group_List.remove("Cisco 4400 Series Integrated Services Routers")
    new_Group_List = Group_List
    logging.info("Final groups ok... moving on")
    return(new_Group_List)
# End of Function


def getIPs(Group_List):
    logging.info("Getting Device IPs")
    i = 0
    NumOfGroups = len(Group_List)
    # open a file for writing
    IPList = open(IP_file, 'w')
    # create the csv writer object
    csvwriter = csv.writer(IPList)
    while i < NumOfGroups:
        group = Group_List[i]
        url = controller_url + ".json?.group=" + group
        response = requests.get(url, auth=HTTPBasicAuth("username", "password"), verify=False)
        r_json = response.json()
        count = (r_json.get("queryResponse", "")).get("@count", "")
        if count == 0:
            # Move on to next group
            i += 1
            continue
        else:
            logging.info(f'Getting IPs for devices in group {group}')
            for entity in r_json['queryResponse']['entityId']:
                for value in entity.values():
                    if "https" in value:
                        new_url = value + ".json"
                        device_response = requests.get(new_url, auth=HTTPBasicAuth(
                            "username", "password"), verify=False)
                        device_json = device_response.json()
                        if (type(device_json) != str)and(group != "Unsupported Cisco Device"):
                            intf_list = device_json["queryResponse"]["entity"][0].get(
                                "inventoryDetailsDTO", "").get("ipInterfaces", "").get("ipInterface", "")
                            time.sleep(1)
                            num_of_interfaces = len(intf_list)
                            j = 0
                            while j < num_of_interfaces:
                                ip = intf_list[j].get(
                                    "ipAddress", "").get("address", "")
                                mask = intf_list[j].get("prefixLength", "")
                                ip_and_mask = str(ip) + "/" + str(mask)
                                output.append(ip_and_mask)
                                j += 1
        # Moving on to next Group
        i += 1
    csvwriter.writerows(zip(output))
    IPList.close()
    return()
# End of function

# Main Function


def main():
    logging.info("Begin")
    InitialGroups = getDeviceGroups()
    Groups = RemoveGeneric(InitialGroups)
    getIPs(Groups)
    logging.info("End")
    return()


if __name__ == "__main__":
    main()
