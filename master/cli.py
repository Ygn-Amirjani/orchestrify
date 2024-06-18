import argparse

def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments to get the image name."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-name", help="Name of the image")
    return parser.parse_args()  # Parse and return the arguments
