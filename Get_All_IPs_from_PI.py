#import requests
#import json
#import csv
import logging
#from requests.auth import HTTPBasicAuth
#import time
from PrimeDeviceFunctions import getDeviceGroups, RemoveGeneric, getIPs,writeIPs

# Define Global Variables
#USERNAME = "username"  # define  REST API username
#PASSWORD = "password"  # define REST API passowrd
#PI_ADDRESS = "ip_address"  # define IP Address of Prime Infrastructure Server


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename='GetAll_IPs.log', level=logging.INFO)
    logging.info("Begin")
    #print("Execution started: ", datetime.now())
    InitialGroups = getDeviceGroups()
    Groups = RemoveGeneric(InitialGroups)
    IPs_List=getIPs(Groups)
    writeIPs(IPs_List)
    #print("Execution Ended: ", datetime.now())
    logging.info("End")
    return()


if __name__ == "__main__":
    main()
