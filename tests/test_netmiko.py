from netmiko import ConnectHandler

device_ip = '150.101.20.48'
device_port = 3001
username = 'neuro'
password = 'Cisco123'
enable_password = "Cisco123"
commands = ['show version', 'show ip int brief', 'sh ip route']

device = {
    'device_type': 'cisco_ios_telnet',
    'ip': device_ip,
    'port': device_port,
    'username': username,
    'password': password,
    'secret': enable_password
}

try:
    with ConnectHandler(**device) as net_connect:
        # Enable privileged mode if needed
        if net_connect.check_enable_mode():
            net_connect.enable()
        for command in commands:
            output = net_connect.send_command(command)
            print(output)

except Exception as e:
    print(f"An error occurred: {e}")
