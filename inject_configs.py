import docker
import os
import tarfile
import io

def copy_file_to_container(container, src_file, dest_path):
    try:
        # Create a tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            # Add the file to the tar archive
            tar.add(src_file, arcname=os.path.basename(src_file))

        tar_stream.seek(0)  # Rewind the stream to the beginning

        # Use the Docker API to copy the file to the container
        container.put_archive(dest_path, tar_stream)
        print(f"Successfully copied {src_file} to {container.name}:{dest_path}")
    except Exception as e:
        print(f"Failed to copy {src_file} to {container.name}: {e}")

# Function to handle copying config files into containers
def inject_configs_into_containers(config_dir, container_prefix, num_configs, target_dir):
    client = docker.from_env()  # Get Docker client
    for i in range(1, num_configs + 1):
        container_name = f"{container_prefix}_{i}"  # Example: scraper-app-1, scraper-app-2, etc.
        config_file = os.path.join(config_dir, f"config_{i}.json")  # Example: config_1.json, config_2.json, etc.

        try:
            # Get the container by name
            container = client.containers.get(container_name)

            # Check if config file exists
            if not os.path.exists(config_file):
                print(f"Config file {config_file} does not exist. Skipping container {container_name}.")
                continue

            # Copy the config file to the container's /app directory
            copy_file_to_container(container, config_file, target_dir)
        except docker.errors.NotFound:
            print(f"Container {container_name} not found. Skipping.")
        except Exception as e:
            print(f"Error handling container {container_name}: {e}")

if __name__ == "__main__":
    # Define paths and parameters
    config_dir = "./configs"  # Directory where config files are located
    container_prefix = "web_scraper_app"  # The prefix of the Docker container names
    num_configs = 12  # Number of configs (and containers)
    target_dir = "/app"  # Destination directory inside the container

    # Inject config files into the respective containers
    inject_configs_into_containers(config_dir, container_prefix, num_configs, target_dir)
