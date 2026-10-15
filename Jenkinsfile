pipeline {
    agent any

    environment {
        // Replace with your public Docker Hub repository before the first build.
        IMAGE_REPO = 'uday9021/hostel-cicd'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and test') {
            steps {
                sh 'docker build --target test --tag hostel-web:test-${BUILD_NUMBER} .'
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    IMAGE_TAG=$(git rev-parse --short=12 HEAD)
                    docker build --tag "$IMAGE_REPO:$IMAGE_TAG" --tag "$IMAGE_REPO:latest" .
                '''
            }
        }

        stage('Push image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        IMAGE_TAG=$(git rev-parse --short=12 HEAD)
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                        docker push "$IMAGE_REPO:$IMAGE_TAG"
                        docker push "$IMAGE_REPO:latest"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    set -eu
                    IMAGE_TAG=$(git rev-parse --short=12 HEAD)
                    kubectl apply -f k8s/service.yaml
                    sed "s|REPLACE_WITH_DOCKERHUB_USERNAME/hostel-cicd:latest|${IMAGE_REPO}:${IMAGE_TAG}|" k8s/deployment.yaml | kubectl apply -f -
                    kubectl rollout status deployment/hostel-web --timeout=180s
                '''
            }
        }
    }
}
