import subprocess
import time
import itertools
import threading
import logging

# Configure logging to log both to console and to a file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("container_monitor.log"),
                        logging.StreamHandler()
                    ])

# A lock to ensure thread-safe printing and logging
log_lock = threading.Lock()

# Function to get the count of files in the 'jsons' directory inside a container
def get_json_count(container_name):
    try:
        command = f"sudo docker exec {container_name} ls jsons | wc -l"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            with log_lock:
                logging.error(f"Failed to get json count for {container_name}")
            return None
    except subprocess.CalledProcessError as e:
        with log_lock:
            logging.error(f"Failed to get json count for {container_name}: {e}")
        return None

# Function to check if the script is running inside the container
def check_script_running(container_name):
    try:
        command = f"sudo docker top {container_name} | grep 'python3 /app/script.py'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return "running"
        else:
            return "stopped"
    except subprocess.CalledProcessError as e:
        with log_lock:
            logging.error(f"Failed to check {container_name}: {e}")
        return "stopped"

# Function to show a loading animation while waiting
def show_loading(duration):
    animation = itertools.cycle(['|', '/', '-', '\\'])
    end_time = time.time() + duration
    while time.time() < end_time:
        with log_lock:
            print(f"\rChecking containers... {next(animation)}", end='', flush=True)
        time.sleep(0.1)
    print("\r", end='')

# Function to monitor a single container
def monitor_container(container_name, interval_seconds, total_users, container_idx):
    while True:
        # Step 1: Check if the script is running
        status = check_script_running(container_name)
        with log_lock:
            logging.info(f"Container {container_name} is {status}")

        if status == "running":
            # Step 2: Get initial JSON file count
            initial_count = get_json_count(container_name)
            if initial_count is None:
                continue

            # Step 3: Show loading animation and wait for the interval
            with log_lock:
                logging.info(f"Monitoring {container_name} for {interval_seconds} seconds...")
            show_loading(interval_seconds)

            # Step 4: Get final JSON file count after the interval
            final_count = get_json_count(container_name)
            if final_count is None:
                continue

            # Step 5: Calculate users processed per minute
            processed_files = final_count - initial_count
            users_per_min = (processed_files / (interval_seconds / 60))
            with log_lock:
                logging.info(f"Container {container_name} processed {users_per_min:.2f} users per minute.")
                total_users[container_idx] = processed_files  # Store processed files for this container
        else:
            with log_lock:
                logging.info(f"Container {container_name} is not running the script.")
        time.sleep(5)  # Small pause before checking again

# Function to monitor all containers concurrently using threads and sum users scraped
def monitor_multiple_containers(container_prefix, num_containers, interval_seconds):
    threads = []
    total_users = [0] * num_containers  # List to store the processed users for each container

    # Create and start a thread for each container
    for i in range(1, num_containers + 1):
        container_name = f"{container_prefix}_{i}"
        thread = threading.Thread(target=monitor_container, args=(container_name, interval_seconds, total_users, i-1))
        thread.start()
        threads.append(thread)

    # Monitor the containers in rounds
    while True:
        time.sleep(interval_seconds + 5)  # Wait for the monitoring round to finish
        # Sum all users processed in this round
        total_users_scraped = sum(total_users)
        with log_lock:
            logging.info(f"Total users scraped across all containers: {total_users_scraped} users in the last {interval_seconds} seconds.")

    # Wait for all threads to complete (they won't actually complete, as the loop is infinite)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Define container prefix, number of containers, and time interval in seconds
    container_prefix = "web_scraper_app"  # Prefix of the container names
    num_containers = 12  # Number of containers to monitor
    interval_seconds = 60  # Time interval in seconds (e.g., 30s, 1min (60s), 2min (120s))

    # Monitor the containers concurrently using threads and log total users scraped
    monitor_multiple_containers(container_prefix, num_containers, interval_seconds)
