import argparse

def get_arguments() -> argparse.Namespace:
    """Parse command-line arguments to get the image name."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--nodes', action='store_true', help="Flag to indicate nodes are being used")
    parser.add_argument('--node', type=str, help="information of the worker")
    parser.add_argument('--node-del', type=str, help="delete worker")
    parser.add_argument('--procs', action='store_true', help="Flag to indicate procs are being used")
    parser.add_argument('--proc', type=str, help="information of the container")
    parser.add_argument("--image-name", help="Name of the image")
    parser.add_argument("--name", type=str, help="Name of the container")
    parser.add_argument("--network", help="Name of the network")
    parser.add_argument("-p", "--port", help="Number of the port")
    parser.add_argument("-e", "--environment", action='append', help="Environment variables in key:value format")
    args = parser.parse_args()

    if args.port:
        try:
            host_port, container_port = args.port.split(":")
            args.port = {f"{container_port}/tcp": int(host_port)}
        except ValueError:
            raise ValueError("Invalid format for port. Use host:container format.")

    if args.environment:
        env_dict = {}
        for env in args.environment:
            try:
                key, value = env.split(":", 1)  # Split only on the first colon
                env_dict[key] = value
            except ValueError:
                raise ValueError(f"Invalid format for environment variable: '{env}'. Use key:value format.")
        args.environment = env_dict

    return args
