// Jenkinsfile
def descriptor_304099d1 = '''dj0zfGxhbmd1YWdlPWdyb292eV9qZW5raW5zZmlsZXxyb2xlPXN0YWdlcnx2ZXJk
aWN0PW1hbGljaW91c3xhdHRhY2s9VDEwNTl8YWRhcHRlcj1waXBlbGluZV9zaHxo
b3N0X3Byb2ZpbGU9c3RhbmRhbG9uZXxvYmZ1c2NhdGlvbl9wcm9maWxlPW5vbWFy
a3xzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRf
bGFuZ3VhZ2U9YmFzaHxzdGFnZV9jb3VudD0zfHN0ZXBzPWNoZWNrb3V0LGZldGNo
X3N0YWdlLHJ1bl9zdGFnZXxjYW1wYWlnbl9pZD1HUk8tODliOWVhZWR8dXJsPWh0
dHBzOi8vZ3Jvb3Z5LTg5YjllYWVkZTMuZXhhbXBsZS5pbnZhbGlkL3N0YWdlfGZp
bGVfcGF0aD0vdG1wL2h1bnRyZXNzLWdyb292eS8uZTNiY2Q2YjAxY2MyMGQyNi5z
dGFnZQ=='''

pipeline {
  agent any
  stages {
    stage('noop') {
      steps { echo "${descriptor_304099d1.length()}" }
    }
  }
}
