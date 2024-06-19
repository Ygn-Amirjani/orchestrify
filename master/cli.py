import argparse

def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments to get the image name."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-name", help="Name of the image")
    parser.add_argument("--name", type=str, help="Name of the container")
    parser.add_argument("--network", help="Name of the networke")
    parser.add_argument("-p", "--port", help="Number of the port")
    parser.add_argument("-e", "--environment", help="Name of the env")
    args = parser.parse_args()

    if args.port:
        try:
            host_port, container_port = args.port.split(":")
            args.port = {f"{container_port}/tcp": int(host_port)}
        except ValueError:
            raise ValueError("Invalid format for port. Use host:container format.")

    if args.environment:
        try:
            key, value = args.environment.split(":")
            args.environment = {key:value}
        except ValueError:
            raise ValueError("Invalid format for environment variable. Use key:value format.")

    return args
