from flask import Flask, request
import docker

app = Flask(__name__)

app.debug = True

@app.route("/pull_image", methods=["POST"])
def send_image():
    image_name = request.get_json()
    try:
        # Create a Docker client
        client = docker.from_env()

        # Pull the image
        image = client.images.pull(image_name)

        # Print the pulled image details
        print(f"Successfully pulled image: {image_name}")
        print(f"Image ID: {image.id}")
        print(f"Tags: {', '.join(image.tags)}")
        return {"status": "ok", "image": image_name}
    except docker.errors.APIError as e:
        return (f"Failed to pull image: {image_name}. Error: {e}")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=18081)