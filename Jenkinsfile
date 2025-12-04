pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Staidlogic-AI-Labs/TAG_Testsuite.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Selenium Tests') {
            steps {
                bat 'pytest -v --junitxml=reports/results.xml'
            }
        }
    }

    post {
        always {
            junit 'reports/results.xml'
        }
    }
}
