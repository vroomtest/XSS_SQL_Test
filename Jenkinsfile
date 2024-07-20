pipeline {
    agent any

    environment {
        VENV_PATH = 'venv'
        FLASK_APP_PATH = 'workspace/flask/app.py'  // Correct path to the Flask app
        PATH = "$VENV_PATH/bin:$PATH"
        SONARQUBE_SCANNER_HOME = tool name: 'SonarQube Scanner'
        SONARQUBE_TOKEN = 'squ_e3d6a2992414e7e93c5d36c6c4a7fb9c5ce6902d'  // Set your new SonarQube token here
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
                    git branch: 'main', url: 'https://github.com/vroomtest/vroom'
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                dir('workspace/flask') {
                    sh 'python3 -m venv $VENV_PATH'
                }
            }
        }
        
        stage('Activate Virtual Environment and Install Dependencies') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        set +e  # Allow non-zero exit codes
                        source $VENV_PATH/bin/activate
                        pip install -r requirements.txt
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
                    ${DEPENDENCY_CHECK_HOME}/bin/dependency-check.sh --project "Flask App" --scan . --format "ALL" --out workspace/flask/dependency-check-report || true
                    '''
                }
            }
        }
        
        stage('Security Testing') {
            steps {
                dir('workspace/flask') {
                    script {
                        // Start the Flask app in the background
                        sh '''
                            set +e  # Allow non-zero exit codes
                            source $VENV_PATH/bin/activate
                            FLASK_APP=$FLASK_APP_PATH flask run &
                            FLASK_PID=$!
                            sleep 10  # Allow time for Flask app to start
                            
                            echo "Running SQL Injection Test"
                            sql_injection_response=$(curl -s -X POST http://127.0.0.1:5000/search -d "search_term=' OR 1=1--")
                            echo "SQL Injection Response: $sql_injection_response"
                            if [[ ! "$sql_injection_response" =~ "SQL injection attack detected" ]]; then
                                echo "SQL injection test failed"
                                exit 1
                            fi

                            echo "Running XSS Attack Test"
                            xss_attack_response=$(curl -s -X POST http://127.0.0.1:5000/search -d "search_term=<script>alert('XSS')</script>")
                            echo "XSS Attack Response: $xss_attack_response"
                            if [[ ! "$xss_attack_response" =~ "XSS attack detected" ]]; then
                                echo "XSS attack test failed"
                                exit 1
                            fi
                            
                            # Stop Flask app
                            kill $FLASK_PID
                            set -e  # Disallow non-zero exit codes
                        '''
                    }
                }
            }
        }
        
        stage('Integration Testing') {
            steps {
                dir('workspace/flask') {
                    sh '''
                        set +e  # Allow non-zero exit codes
                        source $VENV_PATH/bin/activate
                        pytest --junitxml=integration-test-results.xml
                        set -e  # Disallow non-zero exit codes
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
                    // Stop any running container on port 5000
                    sh 'docker ps --filter publish=5000 --format "{{.ID}}" | xargs -r docker stop'
                    // Remove the stopped container
                    sh 'docker ps -a --filter status=exited --filter publish=5000 --format "{{.ID}}" | xargs -r docker rm'
                    // Run the new Flask app container
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
