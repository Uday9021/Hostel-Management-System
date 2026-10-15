# Hostel Management System: CI/CD deployment project

This repository retains the original NetBeans Java Swing project in `HostelManagementSystem/` and adds `hostel-web/`, a small browser-accessible room dashboard based on the same hostel-management project. The web companion provides a reliable HTTP application for the CCA 2 Docker and Kubernetes demonstration. Its sample room records are kept in memory and reset when the container restarts; it does not connect to the legacy Swing application's MySQL database.

## Web companion features

- Room directory with bed capacity, occupancy, and available-bed totals
- Add-room form with validation and duplicate-name protection
- JSON endpoints at `/api/rooms` and a health endpoint at `/health`
- Automated unit tests run in the Docker build's `test` target

## Repository layout

```text
hostel-web/       Flask web app, tests, and requirements
Dockerfile        Root image build with a test target and runtime target
k8s/              Kubernetes Deployment and Service manifests
Jenkinsfile       Declarative CI/CD pipeline
HostelManagementSystem/  Original Java Swing academic project
```

## Run locally with Python

From the repository root:

```bash
cd hostel-web
python -m venv .venv
```

Activate the environment, then install and run. In Windows CMD, activate with `.venv\Scripts\activate.bat`; in a Linux shell, use `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m flask --app app run --host 0.0.0.0 --port 5000
```

Open `http://localhost:5000`. The app uses demo data held in memory.

## CI/CD setup

1. Push this repository to GitHub and create a public Docker Hub repository named `hostel-cicd`.
2. Edit `IMAGE_REPO` near the top of `Jenkinsfile`, replacing `REPLACE_WITH_DOCKERHUB_USERNAME` with your Docker Hub username.
3. In Jenkins, add a Docker Hub username and access token credential with ID `dockerhub-creds`.
4. Create a Pipeline job using **Pipeline script from SCM**, point it at this GitHub repository and branch, and set the script path to `Jenkinsfile`.
5. Ensure the Jenkins account can run Docker and `kubectl` against the Minikube cluster.
6. Run the job. It checks out the repository, builds the test target, builds and pushes a commit-tagged image, applies the manifests, and waits for the rollout.

The Docker Hub repository must be public for the supplied Kubernetes manifest to pull the image without an image-pull secret. If it is private, configure a Kubernetes image-pull secret and reference it in the Deployment.

## Open the deployed application from a browser

On the EC2 host, run this in a terminal and leave it running during the demo:

```bash
sudo -u jenkins -H kubectl port-forward --address 0.0.0.0 service/hostel-web 8081:80
```

Allow inbound TCP port `8081` from your IP in the EC2 security group, then open `http://YOUR_EC2_PUBLIC_IP:8081` from your laptop. Capture screenshots of the Jenkins stages, Docker Hub image tag, Kubernetes resources, app page, and the second run after a source-code change.
