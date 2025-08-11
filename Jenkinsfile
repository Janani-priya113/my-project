pipeline {
    agent any
    environment {
        XRAY_CLIENT_ID = credentials('F9904F2A07584DF694A61E36E7AE4EB1')
        XRAY_CLIENT_SECRET = credentials('70764cd4c0252d388a60de53f3d08f68829a7526be1f213eaeff7cde5dba9f5c')
        TEST_EXEC_KEY = 'IT-4'  // Replace with your Xray Test Execution key
        TEST_KEY = 'IT-3'       // Replace with your Xray Test key
    }
    stages {
        stage('Run Tests') {
            steps {
                sh 'pytest --tb=short -q tests/ || true'
            }
        }
        stage('Prepare JSON for Xray') {
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
