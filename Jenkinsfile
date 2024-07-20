pipeline {
    agent any

    environment {
        VENV_PATH = 'workspace/flask/venv'
        FLASK_APP_PATH = 'workspace/flask/app.py'
        PATH = "${env.WORKSPACE}/${VENV_PATH}/bin:${env.PATH}"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'squ_870452dbd1725e753c04f7220aa9e3459b2e00ca'
        DEPENDENCY_CHECK_HOME = '/var/jenkins_home/tools/org.jenkinsci.plugins.DependencyCheck.tools.DependencyCheckInstallation/OWASP_Dependency-Check/dependency-check'
    }

    stages {
        stage('Check Docker') {
            steps {
                sh 'docker --version'
            }
        }

        stage('Clone Repository') {
            steps {
                dir('workspace') {
                    git branch: 'main', url: 'https://github.com/vroomtest/XSS_SQL_Test'
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                dir('workspace/flask') {
                    sh 'python3 -m venv ${VENV_PATH}'
                }
            }
        }

        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        #!/bin/bash
                        set +e
                        source "${WORKSPACE}/workspace/flask/venv/bin/activate"
                        pip install -r requirements.txt
                        set -e
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('workspace/flask') {
                    sh 'docker build -t flask-app .'
                }
            }
        }

        stage('Deploy Flask App') {
            steps {
                script {
                    echo 'Deploying Flask App...'
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop || true'
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm || true'
                    sh 'docker run -d -p 5000:5000 flask-app'
                    sh 'sleep 10'
                }
            }
        }

        stage('Integration Testing') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        #!/bin/bash
                        set +e
                        source "${WORKSPACE}/workspace/flask/venv/bin/activate"
                        pytest --junitxml=integration-test-results.xml
                        set -e
                    '''
                }
            }
        }

        stage('Dependency Check') {
            steps {
                script {
                    sh 'mkdir -p workspace/flask/dependency-check-report'
                    sh 'echo "Dependency Check Home: $DEPENDENCY_CHECK_HOME"'
                    sh 'ls -l $DEPENDENCY_CHECK_HOME/bin'
                    sh '''
                    ${DEPENDENCY_CHECK_HOME}/bin/dependency-check.sh --project "Flask App" --scan . --format "ALL" --out workspace/flask/dependency-check-report || true
                    '''
                }
            }
        }

        stage('UI Testing') {
            steps {
                dir('workspace/flask') {
                    script {
                        echo 'Running SQL Injection Test'
                        def sql_injection_response = sh(script: 'curl -s -X POST http://localhost:5000/search -d "search_term=\' OR 1=1--" || true', returnStdout: true).trim()
                        echo "SQL Injection Test Response: ${sql_injection_response}"
                        if (!sql_injection_response.contains("SQL injection attack detected")) {
                            error "SQL injection test failed"
                        }

                        echo 'Running XSS Attack Test'
                        def xss_attack_response = sh(script: 'curl -s -X POST http://localhost:5000/search -d "search_term=<script>alert(\'XSS\')</script>" || true', returnStdout: true).trim()
                        echo "XSS Attack Test Response: ${xss_attack_response}"
                        if (!xss_attack_response.contains("XSS attack detected")) {
                            error "XSS attack test failed"
                        }
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    dir('workspace/flask') {
                        sh '''
                        #!/bin/bash
                        ${SONARQUBE_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=flask-app \
                        -Dsonar.sources=. \
                        -Dsonar.inclusions=app.py \
                        -Dsonar.host.url=http://sonarqube:9000 \
                        -Dsonar.login=${SONARQUBE_TOKEN}
                        '''
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo 'Build failed, not deploying Flask app.'
            }
        }
        always {
            archiveArtifacts artifacts: 'workspace/flask/dependency-check-report/*.*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'workspace/flask/integration-test-results.xml', allowEmptyArchive: true
        }
    }
}
