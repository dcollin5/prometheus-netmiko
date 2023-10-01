from prometheus_client import start_http_server, Gauge
import re
from netmiko import ConnectHandler
import random
import time

# Create a Prometheus Gauge metric to track power usage on switches
upower = Gauge('switch_system_power_used', 'System Power Used (AC)', ['server_name'])

def gather_server_metrics(switch_power_used):
    # Replace this with actual logic to gather server metrics
    # For this example, we're simulating server status with random values
    #return random.choice([0, 1])
    #[('Max Power Usage', 81)]
    return switch_power_used[0][1]

# Function to process the command output and remove unnecessary lines
def process_output(output, server_name):
    # Replace this function with your specific output processing logic
    # You can filter or format the output as needed
    # Regular expression patterns to match the desired lines and extract the values
    system_power_pattern = r'System Power Used \(AC\)  (\d+) Watts'#System Power Used (AC)  39 Watts
    max_power_pattern = r'Max Power Usage:\(Watts\) (\d+)'#Max Power Usage:(Watts) 81

    # Initialize an empty list to store the extracted values
    power_values = []

    # Iterate through each line in the output
    for line in output.splitlines():
        # Use re.search to find the pattern in the line
        system_power_match = re.search(system_power_pattern, line)
        max_power_match = re.search(max_power_pattern, line)

        if system_power_match:
            # Extract the numeric value and add it to the list
            power_values.append(("System Power Used (AC)", int(system_power_match.group(1))))

        if max_power_match:
            # Extract the numeric value and add it to the list
            power_values.append(("Max Power Usage", int(max_power_match.group(1))))

    # Print the list of extracted values
    return(power_values)

if __name__ == '__main__':
    # Start an HTTP server to expose metrics
    start_http_server(8000)

    # Read device IPs from a file
    with open('device_ips.txt', 'r') as file:
        device_ips = file.read().splitlines()

    # Define common device credentials
    common_device_info = {
        'device_type': 'cisco_ios',  # Change this to match your device type
        'username': 'username', # Replace with your username
        'password': 'password' # Replace with your password
    }

    while True:
        # Loop through device IPs and perform the query
        for ip in device_ips:
            device_info = common_device_info.copy()
            device_info['ip'] = ip

            try:
                connection = ConnectHandler(**device_info)
                print(f"Connected to {ip}.")

                # Send the query/command
                command = 'show power'  # Replace with your desired command
                output = connection.send_command(command)

                # Process the output and update Prometheus metric
                switch_power_values=process_output(output, ip)

                # Update the Prometheus metric for system power used (AC)
                #upower.labels(server_name).set(power_values[0][1]) if power_values else upower.labels(server_name).set(0)
                upower.labels(ip).set(gather_server_metrics(switch_power_values))

                # Print the processed output
                print(f"Processed output from {ip}:")
                print(output)

            except Exception as e:
                print(f"An error occurred with {ip}: {str(e)}")
            finally:
                # Close the SSH connection
                connection.disconnect()
                print(f"Disconnected from {ip}.")

        # Sleep for some time before gathering metrics again
        time.sleep(3600)
