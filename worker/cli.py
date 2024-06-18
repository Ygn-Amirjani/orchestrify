import argparse

def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments and return them as a Namespace object."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ip", help="Master URL")
    return parser.parse_args()  # Parse and return the arguments
