pipeline {
    agent any

    environment {
        TEST_EXEC_KEY = 'IT-4'  // Replace with your Xray Test Execution key
        TEST_KEY = 'IT-3'       // Replace with your Xray Test key
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    # Install pytest if missing
                    if ! command -v pytest &> /dev/null; then
                        pip install --user pytest
                        export PATH=$PATH:~/.local/bin
                    fi
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    mkdir -p logs
                    pytest --tb=short -q tests/ > logs/logs.txt || true
                '''
            }
        }

        stage('Prepare JSON for Xray') {
            steps {
                script {
                    def logsBase64 = sh(script: 'base64 -w0 logs/logs.txt', returnStdout: true).trim()
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
                          "comment": "Version creation failed - see logs",
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

        stage('Upload Results to Xray') {
            steps {
                withCredentials([
                    string(credentialsId: 'xray-client-id', variable: 'XRAY_CLIENT_ID'),
                    string(credentialsId: 'xray-client-secret', variable: 'XRAY_CLIENT_SECRET')
                ]) {
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
    }
}
