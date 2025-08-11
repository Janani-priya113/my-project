pipeline {
    agent any

    environment {
        XRAY_CLIENT_ID     = credentials('xray-client-id')
        XRAY_CLIENT_SECRET = credentials('xray-client-secret')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'git@github.com:Janani-priya113/my-project.git',
                        credentialsId: 'github-ssh-key' // SSH key ID in Jenkins
                    ]]
                ])
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    if ! command -v pytest >/dev/null 2>&1; then
                        echo "pytest not found, installing..."
                        pip install --user pytest
                        export PATH=$PATH:$HOME/.local/bin
                    fi
                    pytest --tb=short -q tests/ | tee logs.txt
                '''
            }
        }

        stage('Prepare JSON for Xray') {
            steps {
                script {
                    def logBase64 = sh(script: "base64 -w0 logs.txt", returnStdout: true).trim()
                    writeFile file: 'results.json', text: """{
                        "testExecutionKey": "TEST-123",
                        "info": {
                            "summary": "Automated test execution",
                            "description": "Results uploaded from Jenkins"
                        },
                        "logs": "${logBase64}"
                    }"""
                }
            }
        }

        stage('Upload Results to Xray') {
            steps {
                sh '''
                    curl -X POST -H "Content-Type: application/json" \
                         -u $XRAY_CLIENT_ID:$XRAY_CLIENT_SECRET \
                         --data @results.json \
                         https://xray.cloud.getxray.app/api/v2/import/execution
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'logs.txt, results.json', onlyIfSuccessful: false
        }
    }
}
