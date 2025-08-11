pipeline {
    agent any
    environment {
        XRAY_CLIENT_ID = credentials('xray-client-id')   // Jenkins credentials ID
        XRAY_CLIENT_SECRET = credentials('xray-client-secret')
    }
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m ensurepip --upgrade || sudo apt-get update && sudo apt-get install -y python3-pip
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    pytest --tb=short -q tests/ > logs.txt || true
                '''
            }
        }
        stage('Run Python Script for Xray Upload') {
            steps {
                sh '''
                    python3 xray_upload.py
                '''
            }
        }
    }
    post {
        failure {
            echo "Pipeline failed. Check Xray for results."
        }
    }
}

