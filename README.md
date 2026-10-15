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

1. Keep this repository in GitHub and create a public Docker Hub repository named `hostel-cicd` under `uday9021`.
2. The `Jenkinsfile` is configured to publish to `uday9021/hostel-cicd`.
3. In Jenkins, store the Docker Hub username and access token as a username/password credential with ID `dockerhub-creds`. The GitHub repository is public, so the Pipeline SCM credential can be left as `- none -`.
4. Create a Pipeline job using **Pipeline script from SCM** with repository URL `https://github.com/Uday9021/Hostel-Management-System.git`, branch `*/master`, and script path `Jenkinsfile`.
5. Jenkins runs on an Amazon Linux 2023 EC2 instance. Ensure Git, Docker, `kubectl`, and Minikube are installed and available to the Jenkins account, and that Jenkins can use Docker and the Minikube cluster.
6. Run the job. It checks out the repository, runs the six unit tests in the Docker test target, builds a Docker image tagged with the Git commit, pushes that image to Docker Hub, applies the Kubernetes manifests, and waits for the rollout.
7. For the source-change demonstration, the dashboard heading was changed from `Hostel rooms — CI/CD update` to `Hostel rooms — CI/CD update v2`. The change was pushed to `master` and redeployed through Jenkins.

The Docker Hub repository must be public for the supplied Kubernetes manifest to pull the image without an image-pull secret. If it is private, configure a Kubernetes image-pull secret and reference it in the Deployment.

## Open the deployed application from a browser

On the EC2 host, run this in a terminal and leave it running during the demo:

```bash
sudo -u jenkins -H kubectl port-forward --address 0.0.0.0 service/hostel-web 8081:80
```

Allow inbound TCP port `8081` from your IP in the EC2 security group, then open `http://YOUR_EC2_PUBLIC_IP:8081` from your laptop. Capture screenshots of the Jenkins stages, Docker Hub image tag, Kubernetes resources, app page, and the second run after a source-code change.
