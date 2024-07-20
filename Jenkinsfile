pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        FLASK_APP_PATH = 'workspace/flask/app.py' // Correct path to the Flask app
        PATH = "${env.VENV_PATH}/bin:${env.PATH}"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'squ_870452dbd1725e753c04f7220aa9e3459b2e00ca' // Set your new SonarQube token here
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
                        source ${VENV_PATH}/bin/activate
                        pip install -r requirements.txt
                        set -e
                    '''
                }
            }
        }

        stage('Dependency Check') {
            steps {
                script {
                    sh 'mkdir -p workspace/flask/dependency-check-report'
                    sh 'echo "Dependency Check Home: ${DEPENDENCY_CHECK_HOME}"'
                    sh 'ls -l ${DEPENDENCY_CHECK_HOME}/bin'
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
                        sh '''
                            #!/bin/bash
                            set +e
                            source ${VENV_PATH}/bin/activate
                            FLASK_APP=${FLASK_APP_PATH} flask run &
                            sleep 5
                            curl -s http://127.0.0.1:5000 || echo "Flask app did not start"
                            curl -s -X POST -F "search_term=hello" http://127.0.0.1:5000 | grep "Search Result"
                            curl -s -X POST -F "search_term=1=1--" http://127.0.0.1:5000 | grep "Error" 
                            curl -s -X POST -F "search_term=<script>alert(XSS)</script>" http://127.0.0.1:5000 | grep "Error"
                            pkill -f "flask run"
                            set -e
                        '''
                    }
                }
            }
        }

        stage('Integration Testing') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        #!/bin/bash
                        set +e
                        source ${VENV_PATH}/bin/activate
                        pytest --junitxml=integration-test-results.xml
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

        stage('Deploy Flask App') {
            steps {
                script {
                    echo 'Deploying Flask App...'
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop'
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm'
                    sh 'docker run -d -p 5000:5000 flask-app'
                    sh 'sleep 10'
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