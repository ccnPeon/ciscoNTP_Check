#Intake system arguments
#sys.argv[1] is the deviceGroup argument

from netmiko import ConnectHandler
from class_systemGroups import systemGroups
from class_ntpServers import ntpServers
import getpass, sys, json


#set device group class to variable
deviceList = systemGroups.groups
#set ntp server list class to variable
ntpServerList = ntpServers.servers


#set deviceGroup choice from sys argument and check to make sure it is valid in the class file
try:
    deviceGroup = sys.argv[1]
    if deviceGroup in deviceList:
        print("Using Device Group: " + deviceGroup)
    else:
        print("Invalid Argument (1)")
        exit()

except:
    print("Invalid Argument (1)")
    exit()

#Develop variable to check for NTP Servers

ntpMatch = ''''''
for server in sorted(ntpServerList):
    ntpMatch += "ntp server " + server + "\n"

#Remove empty line from ntpMatch
ntpMatch = ntpMatch[:-1]


#Get user credentials to initial SSH session
credUser = input("Please enter username: ")
credPass = getpass.getpass("Please enter password: ")


#Begin connection
for deviceName, deviceIP in deviceList[deviceGroup].items():
    print("Establishing Connection...")
    net_connect = ConnectHandler(device_type='arista_eos',ip=deviceIP,username=credUser,password=credPass)

    #Enter privileged Exec mode
    print("Entering priviledged exec mode...")
    net_connect.enable()

    #send command
    print("Checking NTP Servers...")
    checkNTP = net_connect.send_command("show run | section ntp server")


    #Compare strings to see if configs match.
    if ntpMatch == checkNTP:
        print("Configuration in Sync")

    #If strings don't match, remove only the invalid lines.
    else:
        print("Incorrect servers, updating configuration...")
        ntpRemove = checkNTP.splitlines()
        for line in ntpRemove:
            if line not in ntpMatch:
                print("Removing: " + line)
                net_connect.config_mode()
                net_connect.send_command("no " + line)


        ntpNew = ntpMatch.splitlines()

        for line in ntpNew:
            if line not in checkNTP:
                print("Adding: " + line)
                net_connect.config_mode()
                net_connect.send_command(line)

            elif line in checkNTP:
                print("Command '" + line + "' already exists. Ignoring this line.")

        print("Configuration updated.")
