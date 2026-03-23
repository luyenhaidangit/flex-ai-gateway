pipeline {
    agent none

    options {
        disableConcurrentBuilds()
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
        skipDefaultCheckout(true)
        parallelsAlwaysFailFast()
        timeout(time: 60, unit: 'MINUTES')
    }

    parameters {
        choice(name: 'TARGET_ENV', choices: ['dev', 'uat', 'prod'], description: 'Environment to build for')
        string(name: 'MAJOR', defaultValue: '1', description: 'Major version (e.g. 1)')
        string(name: 'MINOR', defaultValue: '0', description: 'Minor version (e.g. 0)')
        string(name: 'PROD_PATCH', defaultValue: '', description: 'Patch for prod (e.g. 0,1,2...). Required for prod builds')
        booleanParam(name: 'DEPLOY', defaultValue: true, description: 'Push docker image after build?')
    }

    environment {
        REGISTRY_CRED = 'dockerhub-creds'
        IMAGE_NAME = 'flex-ai-gateway'
    }

    stages {
        stage('Main pipeline') {
            agent { label 'master' }

            stages {
                stage('Checkout') {
                    steps {
                        echo '========== Checkout =========='
                        deleteDir()
                        checkout scm
                        echo '=============================='
                    }
                }

                stage('Prepare') {
                    steps {
                        echo '========== Prepare =========='
                        script {
                            def major = params.MAJOR?.trim()
                            def minor = params.MINOR?.trim()

                            if (!major || !minor) {
                                error('MAJOR and MINOR are required')
                            }

                            if (params.TARGET_ENV == 'prod') {
                                def patch = params.PROD_PATCH?.trim()
                                if (!patch) {
                                    error('PROD requires PROD_PATCH (e.g. 0,1,2...)')
                                }
                                env.VERSION = "${major}.${minor}.${patch}"
                            } else {
                                env.VERSION = "${major}.${minor}.${env.BUILD_NUMBER}-${params.TARGET_ENV}"
                            }

                            env.CAN_DEPLOY = 'true'
                        }
                        echo "TARGET_ENV : ${params.TARGET_ENV}"
                        echo "VERSION    : ${env.VERSION}"
                        echo "CAN_DEPLOY : ${env.CAN_DEPLOY}"
                        echo '============================='
                    }
                }

                stage('Build') {
                    steps {
                        echo '========== Build =========='
                        echo 'Nothing to do'
                        echo '==========================='
                    }
                }

                stage('Test') {
                    steps {
                        echo '========== Test =========='
                        echo 'No automated tests configured'
                        echo '=========================='
                    }
                }

                stage('Quality & Security') {
                    steps {
                        echo '========== Quality & Security =========='
                        echo 'No quality gate configured'
                        echo '========================================'
                    }
                }

                stage('Image') {
                    steps {
                        echo '========== Image =========='
                        echo "Building docker image version: ${env.VERSION}"
                        sh '''
                            set -e
                            docker build -t $IMAGE_NAME:$VERSION .
                        '''
                        echo '==========================='
                    }
                }

                stage('Publish') {
                    when {
                        beforeAgent true
                        expression { params.DEPLOY && env.CAN_DEPLOY == 'true' }
                    }
                    steps {
                        echo '========== Publish =========='
                        withCredentials([
                            usernamePassword(
                                credentialsId: REGISTRY_CRED,
                                usernameVariable: 'DOCKER_USER',
                                passwordVariable: 'DOCKER_PASS'
                            )
                        ]) {
                            sh '''
                                set -e
                                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                                docker tag $IMAGE_NAME:$VERSION $DOCKER_USER/$IMAGE_NAME:$VERSION
                                docker push $DOCKER_USER/$IMAGE_NAME:$VERSION
                                docker logout || true
                            '''
                        }
                        echo '============================='
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Build ${BUILD_NUMBER} SUCCESS"
        }
        failure {
            echo 'Build FAILED'
        }
    }
}
