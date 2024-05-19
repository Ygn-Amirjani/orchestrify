import argparse

def get_arguments() -> argparse.Namespace:
    """Get arguments from CLI using argparse"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image-name", help="Image NAME")
    return parser.parse_args()
