import docker
import subprocess

# Function to execute a command inside a container and capture the output
def exec_in_container(container, command):
    try:
        exec_log = container.exec_run(command, detach=False)  # Run the command and wait for completion
        output = exec_log.output  # Get the output
        if isinstance(output, bytes):
            output = output.decode("utf-8").strip()  # Decode output if it's in bytes
        if exec_log.exit_code == 0:
            print(f"Command '{command}' executed successfully in {container.name}")
        else:
            print(f"Command '{command}' failed in {container.name}")
        return output
    except Exception as e:
        print(f"Error executing command in {container.name}: {e}")
        return None

# Function to rename config file inside the container
def process_container(container, config_dir):
    try:
        # Step 1: List files in the config directory
        list_files_command = f"ls {config_dir}"
        files = exec_in_container(container, list_files_command)

        if not files:
            print(f"No files found in {config_dir} for {container.name}")
            return

        # Step 2: Find a file that matches "config_*.json"
        config_file = None
        for file in files.splitlines():
            if file.startswith("config_") and file.endswith(".json"):
                config_file = file
                break

        if not config_file:
            print(f"No matching config file found in {container.name}")
            return

        # Step 3: Rename the found config file to "config.json"
        rename_command = f"mv {config_dir}/{config_file} {config_dir}/config.json"
        exec_in_container(container, rename_command)

    except Exception as e:
        print(f"Error processing container {container.name}: {e}")

# Function to run the Python script in the container from outside
def run_script_in_container(container_name):
    try:
        # Run the Python script in the background using Docker exec from the host machine
        command = f"docker exec -d {container_name} python3 /app/script.py"
        subprocess.run(command, shell=True, check=True)
        print(f"Started script.py in {container_name} in the background.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run script.py in {container_name}: {e}")

# Main function to process multiple containers
def process_containers(container_prefix, num_containers, config_dir):
    client = docker.from_env()
    for i in range(1, num_containers + 1):
        container_name = f"{container_prefix}_{i}"
        try:
            # Get the container by name
            container = client.containers.get(container_name)
            print(f"Processing container: {container.name}")
            process_container(container, config_dir)  # Rename config file
            run_script_in_container(container.name)  # Run the script from outside the container
        except docker.errors.NotFound:
            print(f"Container {container_name} not found. Skipping.")
        except Exception as e:
            print(f"Error handling container {container_name}: {e}")

if __name__ == "__main__":
    # Define container prefix and number of containers
    container_prefix = "web_scraper_app"  # Prefix of the container names
    num_containers = 12  # Number of containers
    config_dir = "/app"  # Directory where config files are located inside the container

    # Process the containers
    process_containers(container_prefix, num_containers, config_dir)
