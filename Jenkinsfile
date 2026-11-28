pipeline{
    agent {label build-vm}
    environment{
        IMAGE = 'jyotimanab/ecommerce-order-service'
        TAG = "${env.BUILD_NUMBER}"
    }
    stages{
        stage('Git Checkout'){
            steps{
                git(url: 'https://github.com/zerotoprodevops/ecommerce-order-service.git', branch: 'main')
            }
        }
        stage('Build Stage'){
            steps{
                sh "docker build -t $IMAGE:$TAG ."
            }
        }
        stage('Scan with Trivy'){
            steps{
                sh "TMPDIR=/tempdir trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 $IMAGE:$TAG"
            }
        }
        stage('Upload to Docker Hub'){
            steps{
                   withCredentials([usernamePassword(credentialsId: 'dockerhub-cred', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                   sh """
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER ----password-stdin
                    docker push $IMAGE:$TAG
                    docker tag $IMAGE:$TAG $IMAGE:latest
                    docker push $IMAGE:latest
                   """     
                }
                

            }
        }

    }
    post{
        success{
            echo "Build $TAG successful - Image $IMAGE uploaded to Docker hub successfully"
            sh "docker rmi $IMAGE:$TAG $IMAGE:latest || echo 'Image cleanup - Image $IMAGE not found locally '"
        }
        failure{
            echo "Pipeline failed - $IMAGE:$TAG left locally for debugging"
        }
    }

}