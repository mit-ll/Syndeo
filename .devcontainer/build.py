import subprocess

image_name = "development-base"

# Build the image from the development Dockerfile
subprocess.run(["docker", "build", "-t", image_name, "."])
