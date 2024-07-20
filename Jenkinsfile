pipeline {
    agent any

    environment {
        VENV_PATH = 'workspace/flask/venv'
        FLASK_APP_PATH = 'workspace/flask/app.py'  // Correct path to the Flask app
        PATH = "${env.WORKSPACE}/${VENV_PATH}/bin:${env.PATH}"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'squ_870452dbd1725e753c04f7220aa9e3459b2e00ca'  // Set your new SonarQube token here
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
                        set +e  # Allow non-zero exit codes
                        source "${VENV_PATH}/bin/activate"
                        pip install -r requirements.txt
                        set -e  # Disallow non-zero exit codes
                    '''
                }
            }
        }
        
        stage('Ensure Template Directory') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        #!/bin/bash
                        mkdir -p templates
                        mv index templates/index.html
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
                    // Stop any running container on port 5000
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop || true'
                    // Remove the stopped container
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm || true'
                    // Run the new Flask app container
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
                        set +e  # Allow non-zero exit codes
                        source "${VENV_PATH}/bin/activate"
                        pytest --junitxml=integration-test-results.xml
                        set -e  # Disallow non-zero exit codes
                    '''
                }
            }
        }
        
        stage('Dependency Check') {
            steps {
                script {
                    // Create the output directory for the dependency check report
                    sh 'mkdir -p workspace/flask/dependency-check-report'
                    // Print the dependency check home directory for debugging
                    sh 'echo "Dependency Check Home: $DEPENDENCY_CHECK_HOME"'
                    sh 'ls -l $DEPENDENCY_CHECK_HOME/bin'
                    sh '''
                   
