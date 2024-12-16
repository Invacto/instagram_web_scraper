Modify config.yaml to fit VM specs

sudo docker-compose up -d

sudo python3 generate_configs.py
sudo python3 inject_configs.py
sudo python3 config_and_run.py

sudo python3 monitor_containers_with_logging.py

sudo docker exec -it web_scraper_app_X /bin/bash

sudo bash kill_python_script.sh (Kill Running Python Scripts in Containers)
