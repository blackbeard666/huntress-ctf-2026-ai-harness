def host = System.getenv('BUILD_HOST')
def descriptor_decoy = "${host}" + new String('dj0zfGxhbmd1YWdlPWdyb292eV9qZW5raW5zZmls'.decodeBase64())
def label = ['build', 'test'].join('-').reverse()
