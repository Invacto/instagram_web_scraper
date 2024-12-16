import requests
import yaml
import json
import random
import time

# Function to read YAML config file
def read_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to read proxies from a file
def read_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                proxies.append(line)
    return proxies

# Function to read usernames from a file
def read_usernames(file_path):
    usernames = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                usernames.append(line)
    return usernames

# Function to test a proxy with retries
def test_proxy_with_retries(proxy, retries=3, delay=10, url="https://httpbin.org/ip"):
    proxy_host, proxy_port, proxy_username, proxy_password = proxy.split(':')
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
    proxy_dict = {"http": proxy_url, "https": proxy_url}

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, proxies=proxy_dict, timeout=5)
            print(f"Attempt {attempt}: Response from proxy {proxy} - {response.text}")
            return True  # Success
        except Exception as e:
            print(f"Attempt {attempt}: Error testing proxy {proxy} - {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Proxy {proxy} failed after {retries} attempts.")
                return False  # Failed after retries

# Function to generate config files
def generate_config_file(config_number, res_proxies, dc_proxies, usernames):
    config_data = {
        "residential-proxies": res_proxies,
        "datacenter-proxies": dc_proxies,
        "usernames": usernames
    }

    # Write the config to a JSON file
    file_name = f"./configs/config_{config_number}.json"
    with open(file_name, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)

    print(f"Configuration saved to {file_name}")

# Main function to handle all configs
def process_configs(config_file, res_proxy_file, dc_proxy_file, usernames_file):
    config = read_yaml_config(config_file)

    # Load resources based on YAML settings
    res_proxies = read_proxies(res_proxy_file)
    dc_proxies = read_proxies(dc_proxy_file)
    usernames = read_usernames(usernames_file)

    num_configs = config['server-config']['configs']
    num_res_proxies_required = config['server-config']['residential-proxies']
    num_dc_proxies_required = config['server-config']['datacenter-proxies']
    num_users_required = config['server-config']['users']

    # Create the required number of configs
    for i in range(num_configs):
        print(f"\nProcessing Config {i+1}:")

        # Select random residential proxies and ensure the required number pass the test
        selected_res_proxies = []
        attempts = 0

        while len(selected_res_proxies) < num_res_proxies_required and attempts < len(res_proxies) * 3:
            proxy = random.choice(res_proxies)
            if proxy not in selected_res_proxies:
                print(f"Testing residential proxy {proxy}...")
                if test_proxy_with_retries(proxy):
                    selected_res_proxies.append(proxy)
            attempts += 1

        if len(selected_res_proxies) < num_res_proxies_required:
            print(f"Failed to find {num_res_proxies_required} working residential proxies for config {i+1}. Skipping...")
            continue

        # Select random datacenter proxies and ensure the required number pass the test
        selected_dc_proxies = []
        attempts = 0

        while len(selected_dc_proxies) < num_dc_proxies_required and attempts < len(dc_proxies) * 3:
            proxy = random.choice(dc_proxies)
            if proxy not in selected_dc_proxies:
                print(f"Testing datacenter proxy {proxy}...")
                if test_proxy_with_retries(proxy):
                    selected_dc_proxies.append(proxy)
            attempts += 1

        if len(selected_dc_proxies) < num_dc_proxies_required:
            print(f"Failed to find {num_dc_proxies_required} working datacenter proxies for config {i+1}. Skipping...")
            continue

        # Select usernames for each config
        selected_usernames = random.sample(usernames, num_users_required)
        print(f"Selected usernames for config {i+1}: {selected_usernames[:5]}...")  # Display first 5 for brevity

        # Generate JSON config file
        generate_config_file(i + 1, selected_res_proxies, selected_dc_proxies, selected_usernames)

if __name__ == "__main__":
    # Paths to the files
    config_file = "config.yaml"
    res_proxy_file = "res_proxy.txt"
    dc_proxy_file = "datacenter_proxies.txt"
    usernames_file = "usernames.txt"

    # Process configs based on YAML file
    process_configs(config_file, res_proxy_file, dc_proxy_file, usernames_file)
