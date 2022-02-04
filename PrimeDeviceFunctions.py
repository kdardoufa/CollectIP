import requests
import csv
import logging
from requests.auth import HTTPBasicAuth
import time
from primeapidata import PI_ADDRESS, USERNAME, PASSWORD

requests.packages.urllib3.disable_warnings()
''' 
Call one of those from the main function or put one out of comments here, be carefull of the different filenames.
It should probably be transfered into a function and pass the filename as a parameter.
But then maybe the logging object would need to be passed around. Not sure. Will test.

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='GetAllDevices.log', level=logging.INFO)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='GetAll_IPs.log', level=logging.INFO)
'''

#timestr = time.strftime("%Y%m%d_%H%M")
#Device_List = "DeviceList_"+timestr+".csv"
#IP_file = "IP_"+timestr+".csv"

# Define Global Variables - these should be included in a separate file named primeapaidata.py
#USERNAME = "username"  # define  REST API username
#PASSWORD = "password"  # define REST API passowrd
#PI_ADDRESS = "ip_address"  # define IP Address of Prime Infrastructure Server

def getAPIResponse(apiurl):
    response = requests.get(apiurl, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    r_json = response.json()
    return (r_json)

# Beginning of Function
def getDeviceGroups():
    logging.info("Getting all device groups")
    apiurl = "https://"+PI_ADDRESS+"/webacs/api/v2/data/DeviceGroups.json?.full=true"
    r_json = getAPIResponse(apiurl)
    Group_List = []
    for entity in r_json['queryResponse']['entity']:
        group = entity["deviceGroupsDTO"]["groupName"]
        Group_List.append(group)
        logging.info(f" - added group {group}")
    logging.info("Initial groups ok... moving on")
    return(Group_List)
# End of Function

# Beginning of Function
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
    if "Wireless Controller" in Group_List:
        Group_List.remove("Wireless Controller")
    if "Cisco 4400 Series Integrated Services Routers" in Group_List:
        Group_List.remove("Cisco 4400 Series Integrated Services Routers")
    new_Group_List = Group_List
    logging.info("Final groups ok... moving on")
    return(new_Group_List)
# End of Function

# Beginning of Function
def getDevices_old(Group_List):
    timestr = time.strftime("%Y%m%d_%H%M")
    Device_List = "DeviceList_"+timestr+".csv"
    logging.info(" - Getting Device Info")
    i = 0
    DeviceFileList = []
    NumOfGroups = len(Group_List)
    # remove last / from controller url
    new_url = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails"
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

# Beginning of function
def getDevices(Group_List):
    logging.info("Getting Device Info")
    #create a list of list of strings for the device file
    DeviceList = []
    for group in Group_List:
        apiurl = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails.json?.full=true&.maxResults=1000&.group=" + group
        r_json = getAPIResponse(apiurl)
        try:
            count = int(r_json["queryResponse"]["@count"])
            if count != 0:
                logging.info(f' - Getting devices in group {group} with count {count}')
                for entity in r_json["queryResponse"]["entity"]:
                    Info = entity["inventoryDetailsDTO"]
                    DeviceName = Info["summary"]["deviceName"]
                    IP_Addr = Info["summary"]["ipAddress"]
                    Location = Info["summary"]["location"]
                    DevType = Info["summary"]["deviceType"]
                    if group != "Unsupported Cisco Device":
                        SN = Info["chassis"]["chassis"][0]["serialNr"]
                        Model = Info["chassis"]["chassis"][0]["modelNr"]
                    else:
                        SN = "-"
                        Model = "-"
                    new_row = [DeviceName, IP_Addr, Location, Model, SN]
                    DeviceList.append(new_row)
            else:
                continue
        except:
            logging.info(" - Moving on to next group - due to error")
            continue
        # exit try and move to next group
    logging.info(" - All info has been collected.")
    return(DeviceList)

def getIPs_old(Group_List):
    logging.info("Getting Device IPs")
    timestr = time.strftime("%Y%m%d_%H%M")
    IP_file = "IP_"+timestr+".csv"
    output = []
    controller_url = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails/"
    for group in Group_List:
        url = controller_url + ".json?.full=true&.group=" + group + "&.maxResults=1000"
        response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        r_json = response.json()
        count = (r_json.get("queryResponse", "")).get("@count", "")
        if count != 0:
            logging.info(f'Getting IPs for devices in group {group}')
            ''' This group has already been removed from the group list, the if clause is redundant'''
            if group != "Unsupported Cisco Device":
                for Info in r_json['queryResponse']['entity']:
                    intf_list = Info["inventoryDetailsDTO"]["ipInterfaces"]["ipInterface"]
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

def getIPs(Group_List):
    logging.info("Getting Device IPs")
    IPs_List = []
    for group in Group_List:
        apiurl = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails.json?.full=true&.maxResults=1000&.group=" + group
        r_json = getAPIResponse(apiurl)
        try:
            # get the number of devices in group
            count = int(r_json["queryResponse"]["@count"])
            # if there are devices in this group process them
            if count != 0:
                logging.info(f' - Getting IPs for devices in group {group}')
                ''' This group has already been removed from the group list, the if clause is redundant'''
                if group != "Unsupported Cisco Device":
                    for Info in r_json['queryResponse']['entity']:
                        intf_list = Info["inventoryDetailsDTO"]["ipInterfaces"]["ipInterface"]
                        for interface in intf_list:
                            ip = interface["ipAddress"].get("address", "")
                            mask = interface.get("prefixLength", "")
                            ip_and_mask = str(ip) + "/" + str(mask)
                            IPs_List.append(ip_and_mask)
                else:
                    for Info in r_json['queryResponse']['entity']:
                        ip = Info["inventoryDetailsDTO"]["summary"]["ipAddress"]
                        mask = "24"
                        ip_and_mask = str(ip) + "/" + str(mask)
                        IPs_List.append(ip_and_mask)
                # Move on to next group
            # If no devices in Group then move on
            else:
                continue
            count = (r_json.get("queryResponse", "")).get("@count", "")
        except:
            logging.info(" - Moving on to next group - due to error")
            continue
    return IPs_List
# for loop ends

'''
This Functions needs to be reviewed.
Would be nice if the filename is passed as a parameter.
Also if the list of fields is also parameter, 
then we can have a single function for exporting
to csv format.
'''
def writeDevices(DeviceFileList):
    logging.info("Writing data to file.")
    timestr = time.strftime("%Y%m%d_%H%M")
    Device_List = "DeviceList_"+timestr+".csv"
    # open a file for writing
    DeviceList = open(Device_List, 'w')
    # create the csv writer object
    csvwriter = csv.writer(DeviceList)
    header = ["DeviceName", "IP_Address", "Location", "Type", "Serial Number"]
    csvwriter.writerow(header)
    for line in DeviceFileList:
        csvwriter.writerow(line)
    DeviceList.close()
    logging.info("All done.")
    return()
# End of function

def writeIPs(IPs_List):
    timestr = time.strftime("%Y%m%d_%H%M")
    IP_file = "IP_"+timestr+".csv"
    # open a file for writing
    IPList = open(IP_file, 'w')
    # create the csv writer object
    csvwriter = csv.writer(IPList)
    '''
    zip is needed to put the IP addresses together without commas between each string.
    We may look for a better solution.
    '''
    csvwriter.writerows(zip(IPs_List))
    IPList.close()
    return()

# just get serials and type
def getDevicesSerials(Group_List):
    logging.info(" - Getting Device Info")
    #create a list of list of strings for the device file
    DeviceList = []
    for group in Group_List:
        apiurl = "https://"+PI_ADDRESS+"/webacs/api/v4/data/InventoryDetails.json?.full=true&.maxResults=1000&.group=" + group
        r_json = getAPIResponse(apiurl)
        try:
            count = int(r_json["queryResponse"]["@count"])
            if count != 0:
                logging.info(f' - Getting devices in group {group} with count {count}')
                for entity in r_json["queryResponse"]["entity"]:
                    if group == "Unsupported Cisco Device":
                        continue
                    Info = entity["inventoryDetailsDTO"]
                    DeviceDetails = dict()
                    DeviceDetails["code"] = Info["chassis"]["chassis"][0]["modelNr"]
                    DeviceDetails["serial"] = Info["chassis"]["chassis"][0]["serialNr"]
                    DeviceList.append(DeviceDetails)
            else:
                continue
        except:
            logging.info(" - Moving on to next group - due to error")
            continue
        # exit try and move to next group
    logging.info(" - All info has been collected.")
    return(DeviceList)

def getSimpleDeviceSerials():
    logging.info(" - Getting Device Info")
    #create a list of list of strings for the device file
    apiurl = "https://"+PI_ADDRESS+"/webacs/api/v4/data/Devices.json?.full=true&.maxResults=1000"
    resp = getAPIResponse(apiurl)
    DeviceList = []
    counter = 0
    last_url = ""
    try:
        count = int(resp["queryResponse"]["@count"])
        logging.info(f" - {count} Devices found")
        if count > 0:
            logging.info(" - Looping on Devices")
            for entity in resp["queryResponse"]["entity"]:
                dev_url = entity['@url']
                if "devicesDTO" not in entity.keys():
                    logging.warning(f" - Device at url: {dev_url}.json is missing deviceDTO section")
                    continue
                dev_info = entity["devicesDTO"]
                if dev_info["adminStatus"] == "UNMANAGED":
                    logging.warning(f" - Device at url: {dev_url}.json is UNMANAGED")
                    continue
                if "manufacturerPartNrs" not in dev_info.keys():
                    logging.warning(f" - Device at url: {dev_url}.json is unsupported and missing manufacturer section")
                    continue
                if dev_info["managementStatus"].strip() not in ["MANAGED_AND_SYNCHRONIZED","INSERVICE_MAINTENANCE"]:
                    logging.warning(f" - Device at url: {dev_url}.json is {dev_info['managementStatus']}")
                    continue
                if "serialNumber" not in dev_info["manufacturerPartNrs"]["manufacturerPartNr"][0].keys():
                    logging.warning(f" - Device at url: {dev_url}.json does not have serial number block")
                    continue
                serial_counter = 0
                for chassis in dev_info["manufacturerPartNrs"]["manufacturerPartNr"]:
                    DeviceDetails = dict()
                    DeviceDetails["hostname"] = dev_info["deviceName"]
                    DeviceDetails["code"] = chassis["partNumber"]
                    DeviceDetails["serial"] = chassis["serialNumber"]
                    if serial_counter == 0:
                        DeviceDetails["ipaddress"] = dev_info["ipAddress"]
                    else:
                        DeviceDetails["ipaddress"] = ""
                    DeviceList.append(DeviceDetails)
                    serial_counter += 1
                    counter = counter + 1
                last_url = entity['@url']
    except:
        logging.info(f" - Some device is not conform. Last correct one was at {last_url}.json")
    logging.info(" - All info has been collected, "+str(counter)+ " devices gathered from Prime")
    return(DeviceList)

def getAccessPoints():
    logging.info(" - Getting Access Points Info")
    #create a list of list of strings for the device file
    apiurl = "https://"+PI_ADDRESS+"/webacs/api/v4/data/AccessPointDetails.json?.full=true&.maxResults=1000"
    resp = getAPIResponse(apiurl)
    AcpList = []
    counter = 0
    last_url = ""
    try:
        count = int(resp["queryResponse"]["@count"])
        logging.info(f" - {count} Wifi Access Points found")
        if count > 0:
            logging.info(" - Looping on Access Points")
            for entity in resp["queryResponse"]["entity"]:
                acp_url = entity['@url']
                if "accessPointDetailsDTO" not in entity.keys():
                    logging.warning(f" - Device at url: {acp_url}.json is missing accessPointDetailsDTO section")
                    continue
                acp_info = entity["accessPointDetailsDTO"]
                if acp_info["adminStatus"] != "ENABLE":
                    logging.warning(f" - Access Point at url: {acp_url}.json is DISABLED")
                    continue
                if acp_info["status"].strip() != "CLEARED":
                    logging.warning(f" - Device at url: {acp_url}.json is {acp_info['status']}")
                    continue
                AcpDetails = dict()
                AcpDetails["hostname"] = acp_info["name"]
                AcpDetails["code"] = acp_info["model"]
                AcpDetails["serial"] = acp_info["serialNumber"]
                AcpDetails["ipaddress"] = acp_info["ipAddress"]["address"]
                AcpList.append(AcpDetails)
                counter = counter + 1
                last_url = entity['@url']
    except:
        logging.info(f" - Some device is not conform. Last correct one was at {last_url}.json")
    logging.info(" - All info has been collected, "+str(counter)+ " devices gathered from Prime")
    return(AcpList)

def getFinalDeviceGroups():
    InitialGroups = getDeviceGroups()
    Groups = RemoveGeneric(InitialGroups)
    return(Groups)

def exportDeviceSerials():
    Groups = getFinalDeviceGroups()
    DeviceSerials = getDevicesSerials(Groups)
    return(DeviceSerials)

def exportDeviceDetailsCsv():
    Groups = getFinalDeviceGroups()
    DeviceList = getDevices(Groups)
    writeDevices(DeviceList)
    return()

# Main Function
def main():
    exportDeviceDetailsCsv()
    return()


if __name__ == "__main__":
    main()
