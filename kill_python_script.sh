#!/bin/bash

# Array of Docker container names
containers=("web_scraper_app_1" "web_scraper_app_2" "web_scraper_app_3" "web_scraper_app_4", "web_scraper_app_5", "web_scraper_app_6", "web_scraper_app_7", "web_scraper_app_8", "web_scraper_app_9", "web_scraper_app_10", "web_scraper_app_11", "web_scraper_app_12")

# Loop through each container
for container in "${containers[@]}"; do
	    echo "Checking container: $container"
	        
	        # Get the PID of the python3 /app/script.py process
		    pid=$(sudo docker top "$container" | grep "python3 /app/script.py" | awk '{print $2}')
		        
		        if [ -z "$pid" ]; then
				        echo "No python3 /app/script.py process found in $container."
					    else
						            echo "Found process with PID $pid in $container. Killing it..."
							            sudo kill -9 "$pid"
								            echo "Process $pid killed in $container."
									        fi
									done

									echo "Script execution completed."

