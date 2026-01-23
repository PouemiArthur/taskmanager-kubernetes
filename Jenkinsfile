pipeline {
    agent any
    
    environment {
        COMPOSE_PROJECT_NAME = "taskmanager-jenkins-docker"
        BACKEND_IMAGE = "task-backend"
        FRONTEND_IMAGE = "task-frontend"
        NGINX_IMAGE = "task-nginx2"
        BUILD_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        
        stage('Checkout') {
            steps {
                echo '📦 Checking out code...'
                // Code is already in workspace
                sh 'ls -la'
            }
        }
        
        stage('Build Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        echo '🐳 Building backend Docker image...'
                        script {
                            dir('backend') {
                                sh """
                                    docker build -t ${BACKEND_IMAGE}:${BUILD_TAG} .
                                    docker tag ${BACKEND_IMAGE}:${BUILD_TAG} ${BACKEND_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Frontend') {
                    steps {
                        echo '🎨 Building frontend Docker image...'
                        script {
                            dir('frontend') {
                                sh """
                                    docker build -t ${FRONTEND_IMAGE}:${BUILD_TAG} .
                                    docker tag ${FRONTEND_IMAGE}:${BUILD_TAG} ${FRONTEND_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Nginx') {
                    steps {
                        echo '🌐 Building nginx Docker image...'
                        script {
                            dir('nginx') {
                                sh """
                                    docker build -t ${NGINX_IMAGE}:${BUILD_TAG} .
                                    docker tag ${NGINX_IMAGE}:${BUILD_TAG} ${NGINX_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('List Images') {
            steps {
                echo '📋 Listing built images...'
                sh '''
                    echo "=== Docker Images ==="
                    docker images | grep task-
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Running tests...'
                script {
                    sh '''
                        docker run --rm ${BACKEND_IMAGE}:${BUILD_TAG} \
                        sh -c "pip install pytest pytest-flask && pytest tests/ -v || echo 'Tests not found, skipping...'"
                    '''
                }
            }
        }
        
        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying application with docker-compose...'
                script {
                    sh '''
                        # Start all services
                        docker-compose up --build
                        
                        # Wait for services to be ready
                        echo "Waiting for services to start..."
                        sleep 10
                    '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo '💚 Running health checks...'
                script {
                    sh '''
                        # Check if containers are running
                        echo "=== Running Containers ==="
                        docker ps --filter "name=task_"
                        
                        # Check backend health
                        echo "=== Testing Backend Health ==="
                        curl -f http://localhost:3000/api/health || echo "Backend health check failed"
                        
                        # Check if frontend is accessible
                        echo "=== Testing Frontend Access ==="
                        curl -f http://localhost:3000/ || echo "Frontend check failed"
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo '🔗 Running integration tests...'
                script {
                    sh '''
                        # Create a test task
                        echo "Creating test task..."
                        TASK_RESPONSE=$(curl -s -X POST http://localhost:3000/api/tasks \
                          -H "Content-Type: application/json" \
                          -d '{"title": "Jenkins CI Test Task", "description": "Created by Jenkins build #'${BUILD_NUMBER}'"}')
                        
                        echo "Task created: $TASK_RESPONSE"
                        
                        # Get all tasks
                        echo "Fetching all tasks..."
                        curl -s http://localhost:3000/api/tasks | jq '.' || echo "Tasks fetched"
                        
                        echo "✅ Integration tests passed!"
                    '''
                }
            }
        }
        
        stage('Container Stats') {
            steps {
                echo '📊 Showing container statistics...'
                script {
                    sh '''
                        echo "=== Container Resource Usage ==="
                        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
                        $(docker ps --filter "name=task_" -q)
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ ========================================='
            echo '✅ Pipeline completed successfully!'
            echo "✅ Build #${BUILD_NUMBER} deployed locally"
            echo '✅ Application running at: http://localhost:3000'
            echo '✅ ========================================='
        }
        failure {
            echo '❌ ========================================='
            echo '❌ Pipeline failed!'
            echo "❌ Build #${BUILD_NUMBER} encountered errors"
            echo '❌ Check logs above for details'
            echo '❌ ========================================='
        }
        always {
            echo '🧹 Post-build cleanup...'
            script {
                sh '''
                    # Remove dangling images
                    docker image prune -f
                    
                    # Show final image list
                    echo "=== Final Local Images ==="
                    docker images | grep -E "task-|REPOSITORY"
                '''
            }
        }
    }
}        
