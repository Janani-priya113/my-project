pipeline {
    agent any
    environment {
        XRAY_CLIENT_ID = credentials('xray-client-id')   // Jenkins credentials ID
        XRAY_CLIENT_SECRET = credentials('xray-client-secret')
        TEST_EXEC_KEY = 'IT-4'  // Xray Test Execution key
        TEST_KEY = 'IT-3'       // Xray Test case key
    }
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest --tb=short -q tests/ > logs.txt || true
                '''
            }
        }
        stage('Prepare Xray JSON') {
            steps {
                script {
                    def logsBase64 = sh(script: 'base64 -w0 logs.txt', returnStdout: true).trim()
                    writeFile file: 'results.json', text: """
                    {
                      "testExecutionKey": "${TEST_EXEC_KEY}",
                      "info": {
                        "summary": "Version creation pipeline results",
                        "description": "Automated execution of version creation test"
                      },
                      "tests": [
                        {
                          "testKey": "${TEST_KEY}",
                          "status": "FAIL",
                          "comment": "Version creation failed - check attached logs",
                          "evidences": [
                            {
                              "data": "${logsBase64}",
                              "filename": "logs.txt",
                              "contentType": "text/plain"
                            }
                          ]
                        }
                      ]
                    }
                    """
                }
            }
        }
        stage('Upload to Xray') {
            steps {
                sh '''
                  TOKEN=$(curl -s -H "Content-Type: application/json" \
                      -d '{"client_id":"'$XRAY_CLIENT_ID'","client_secret":"'$XRAY_CLIENT_SECRET'"}' \
                      https://xray.cloud.getxray.app/api/v2/authenticate | tr -d '"')
                  
                  curl -s -H "Authorization: Bearer $TOKEN" \
                      -H "Content-Type: application/json" \
                      -d @results.json \
                      https://xray.cloud.getxray.app/api/v2/import/execution
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
