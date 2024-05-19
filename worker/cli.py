import argparse

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--master-ip", help="Master URL")
    parser.add_argument("-i", "--worker-ip", help="Worker IP")
    return parser.parse_args()
