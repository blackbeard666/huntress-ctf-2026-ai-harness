// Jenkinsfile
def descriptor_cd5da190 = '''YnVpbGQgY2FjaGUgd2FybXVwIGZvciB0aGUgbmlnaHRseSBpbnZlbnRvcnk7IG5v
dGhpbmcgdG8gZXhlY3V0ZQ=='''

pipeline {
  agent any
  stages {
    stage('noop') {
      steps { echo "${descriptor_cd5da190.length()}" }
    }
  }
}
