# Hairstyle Recommendation App 2023.11
## About
Hairstyle Recommendation App is a separate service which takes image of client, applies pipeline of recommandation algorithms and returns recommendation scores for each hairstyle.

## Installation
### Local
* Install Redis(https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/).
* Install python3 requirements: `pip3 install -r requrements.txt`.

### Minikube (recommended)
* Install Docker (https://docs.docker.com/engine/install/ubuntu/).
* Install Minikube (https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download).
* Build dev-server application: `docker build -t hairstyler .`

## Running
### Local
* To run dev-server application execute the following command: `flask --app hairstyler run --cert=certificates/cert.pem --key=certificates/key.pem --host=0.0.0.0`.   
* To run unit tests execute: `python3 -m unittest discover -v`.
* Check how API works by playing around with `https://127.0.0.1:5000/docs` in your browser.

### Minikube (recommended)
* Run Minikube: `minikube start`
* Apply k8s config and start the application: `kubectl apply -f ./configs/k8s.yaml`
* To run unit tests execute: `kubectl exec --stdin --tty hairstyler -- python3 -m unittest discover -v`
* Check IP of Minikube by running: `minikube ip`.
* Check how API works by playing around with `https://<minikube-ip>:30500/docs` in your browser.

#### Troubleshooting
* Point minikube to docker-daemon: `eval $(minikube -p minikube docker-env)`
