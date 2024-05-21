import argparse

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ip", help="Master URL")
    return parser.parse_args()
