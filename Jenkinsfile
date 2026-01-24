pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "backend"
        FRONTEND_IMAGE = "frontend"
        NGINX_IMAGE    = "nginx"
        BUILD_TAG      = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                script {
                    echo "Building backend, frontend and nginx images..."
                    dir('backend')  { sh "docker build -t ${BACKEND_IMAGE}:${BUILD_TAG} ." }
                    dir('frontend') { sh "docker build -t ${FRONTEND_IMAGE}:${BUILD_TAG} ." }
                    dir('nginx')    { sh "docker build -t ${NGINX_IMAGE}:${BUILD_TAG} ." }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deployment with docker-compose..."
                sh "docker-compose up"
            }
        }
    }

    post {
        always {
            echo "Cleaning up old Docker data..."
            sh "docker image prune -f"
        }
    }
}
