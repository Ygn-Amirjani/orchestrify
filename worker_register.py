import requests
import uuid
import psutil, multiprocessing
import argparse

def post(url: str, data: dict) -> requests.Response:
    return requests.post(url, json=data)

def register(master_url: str, worker_ip: str) -> None:
    """sends its information to the master in a dictionary"""
    data = {
        "id": str(uuid.uuid4()),
        "ip": worker_ip,
        "ram": psutil.virtual_memory().total,
        "cpu": multiprocessing.cpu_count(),
        "status": "RUNNING",
    }
    result = post(f"{master_url}/worker", data)
    if result.status_code == 200:
        print("Worker registered successfully")
    else:
        print(result.text)
        raise Exception(f"Worker registration failed {result.status_code}")
    
def get_aruments() -> argparse.Namespace:
    """Get arguments from CLI using argparse"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--master-ip", help="Master URL")
    parser.add_argument("-i", "--worker-ip", help="Worker IP")
    return parser.parse_args()

def main(args: argparse.Namespace):
    register(args.master_ip, args.worker_ip)

if __name__ == "__main__":
    main(get_aruments())