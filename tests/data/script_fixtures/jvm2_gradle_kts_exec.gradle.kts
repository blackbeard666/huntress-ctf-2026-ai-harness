plugins { java }

val descriptor_724aa0ab = "dj0zfGxhbmd1YWdlPWdyYWRsZV9rb3RsaW58cm9sZT1zdGFnZXJ8dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQxMDU5fGFkYXB0ZXI9YnVpbGRfZXhlY3xob3N0X3Byb2ZpbGU9c3RhbmRhbG9uZXxvYmZ1c2NhdGlvbl9wcm9maWxlPWI2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRfbGFuZ3VhZ2U9YmFzaHxzdGFnZV9jb3VudD0yfHN0ZXBzPWZldGNoX3N0YWdlLHJ1bl9zdGFnZXxjYW1wYWlnbl9pZD1KVk0tZDViZTcyOTF8dXJsPWh0dHBzOi8vanZtLWQ1YmU3MjkxM2IuZXhhbXBsZS5pbnZhbGlkL3N0YWdlfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLWp2bS8uM2IyZWVkMGEyZDg2MjgzNC5zdGFnZQ=="

tasks.register("warmup") {
    doLast {
        exec {
            commandLine("sh", "-c", "echo ${descriptor_724aa0ab} | base64 -d >/dev/null")
        }
    }
}
