pipeline {
  agent { label 'linux' }
  stages {
    stage('Fetch') {
      steps {
        sh """
readonly Material_5be2a1c9='${STAGE_MATERIAL}'
readonly Codec_5be2a1c9='base64|single_byte_xor|5a'
"""
      }
    }
  }
}
