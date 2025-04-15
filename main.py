import yaml
import requests
import time
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
# Function to load configuration from the YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to perform health checks
def check_health(endpoint):
    url = endpoint['url']
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers')
    body = endpoint.get('body')
    try:
        startReqTime = time.time()
        response = requests.request(method, url, headers=headers, json=body)
        timeTaken = (time.time() - startReqTime) * 1000
        if 200 <= response.status_code < 300 and timeTaken < 500:
            return "UP"
        else:
            return "DOWN"
    except requests.RequestException as e:
        logging.error(f"Request failed for {url}: {e}")
        return "DOWN"

# Main function to monitor endpoints
def monitor_endpoints(file_path):
    config = load_config(file_path)

    while True:
        domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
        for endpoint in config:
            required_fields = ["url", "name"]
            if "url" not in endpoint or not endpoint["url"]:
                logging.warning(f"Skipping endpoint: missing or empty 'url' → {endpoint}")
                continue
            if "name" not in endpoint or not endpoint["name"]:
                logging.warning(f"Skipping endpoint: missing or empty 'name' → {endpoint}")
                continue    

            domainUrl = endpoint["url"].split("//")[-1].split("/")[0]
            domain = domainUrl.split(":")[0]
            result = check_health(endpoint)
            logging.info(f"The result of the endpoint '{endpoint['name']}' ({endpoint['url']}) is [{result}]")

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            logging.info(f"{domain} has {availability}% availability percentage")

        logging.info("✅ Completed health check cycle. Waiting for next cycle...\n")
        time.sleep(15)

# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        logging.error("Usage: python monitor.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")