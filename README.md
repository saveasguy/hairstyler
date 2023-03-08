# Hairstyle Recommendation App
## About
Hairstyle Recommendation App is a separate service which takes image of client, applies pipeline of recommandation algorithms and returns recommendation scores for each hairstyle.

## Installation
* Conda (https://docs.conda.io/en/latest/miniconda.html)
* Tensorflow (https://www.tensorflow.org/install/pip)
* Python packages
  * `pip install tensorflow-gpu`
  * `pip install pillow opencv-python numpy`
* (optional) Nvidia GPU support
  * CUDA 11.2 (https://developer.nvidia.com/cuda-toolkit-archive)
  * cuDNN 8.1 (https://developer.nvidia.com/rdp/cudnn-download)
* Flask: `pip install flask flask-cors`

### Docker (recommended)
* Docker (https://docs.docker.com/engine/install/ubuntu/)
* (optional) nvidia-docker2 (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
* tensorflow for Docker (https://www.tensorflow.org/install/docker)
* Build dev-server application: `DOCKER_BUILDKIT=1 docker build -t hairstyler-dev -f Dockerfile.dev .`
  * (optional) Build dev-server-application with GPU support: `DOCKER_BUILDKIT=1 docker build -t hairstyler-gpu-dev -f Dockerfile.gpu.dev .`
* Build tests: `DOCKER_BUILDKIT=1 docker build -t hairstyler-tests -f Dockerfile.tests .`
  * (optional) Build tests with GPU support: `DOCKER_BUILDKIT=1 docker build -t hairstyler-gpu-tests -f Dockerfile.gpu.tests .`

## Running
To run dev-server application execute following command: `flask --app hairstyler run --cert=certificates/cert.pem --key=certificates/key.pem --host=0.0.0.0`.   
To run unit tests execute: `python -m unittest discover -v`.

### Docker (recommended)
* To run dev-server application execute following command: `docker run -p 5000:5000 hairstyler-dev`
  * (optional) To run dev-server with GPU support execute: `docker run --gpus all -p 5000:5000 hairstyler-gpu-dev`
* To run unit tests execute: `docker run hairstyler-tests`
  * (optional) To run unit tests with GPU support execute: `docker run --gpus all hairstyler-gpu-tests`
