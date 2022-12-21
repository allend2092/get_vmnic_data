import netmiko
import re
import json
import sys

# Set up the connection parameters and DNS server address
connection_parameters = {
    "device_type": "generic",
    "username": "root",
    "password": "Apple123@",
}
dns_server = "172.17.8.20"

# Check if a file name was provided as a command line argument
if len(sys.argv) < 2:
    print("Usage: python script.py host_file")
    sys.exit()

# Read the file of hostnames or IP addresses
with open(sys.argv[1], "r") as f:
    hosts = f.read().splitlines()

# Initialize a list to store the collected data
data = []

# Iterate over the list of hosts
for host in hosts:
    # Update the connection parameters with the current host
    connection_parameters["ip"] = host

    # Connect to the device using netmiko
    connection = netmiko.ConnectHandler(**connection_parameters)

    # Run the nslookup command using the server's IP address and the DNS server address
    nslookup_command = "nslookup {} {}".format(host, dns_server)
    output = connection.send_command(nslookup_command)

    # Use a regular expression to extract the fully qualified domain name from the nslookup output
    match = re.search(r"name = (.*)", output)
    if match:
        hostname = match.group(1)
    else:
        hostname = host

    # Print the hostname
    print(hostname)

    # Run the command to retrieve the vmnic information
    output = connection.send_command("net-stats -l | grep vmnic")

    # Initialize an empty list to store the vmnic names
    vmnic_names = []

    # Iterate over the lines of the output
    for line in output.split("\n"):
        # Split the line into columns
        columns = line.split()
        # If the line has at least 6 columns, the sixth column is the vmnic name
        if len(columns) >= 6:
            vmnic_names.append(columns[5])

    # Close the connection
    connection.disconnect()

    # Print the list of vmnic names
    print(vmnic_names)

    # Store the hostname and vmnic names in the data list
    data.append({
        "hostname": hostname,
        "vmnic_names": vmnic_names
    })

# Write the data to a JSON file in a pretty-printed format
with open("vmnic_data.json", "w") as f:
    json.dump(data, f, indent=2)
