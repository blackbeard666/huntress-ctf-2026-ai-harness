import java.util.Base64
import java.nio.charset.StandardCharsets
def x1 = new String('dj0zfGxhbmd1YWdlPWdyb292eV9qZW5raW5zZmlsZXxyb2xlPXN0YWdlcnx2ZXJkaWN0PW1hbGljaW91c3xhdHRhY2s9VDEwNTl8YWRhcHRlcj1waXBlbGluZV9zaHxobw=='.decodeBase64())
def x2 = new String(Base64.getDecoder().decode("c3RfcHJvZmlsZT1zdGFuZGFsb25lfG9iZnVzY2F0aW9uX3Byb2ZpbGU9aGV4fHN0YWdlX3Byb2ZpbGU9dHdvX3N0YWdlX2Rvd25sb2FkX2V4ZWN1dGV8bmV4dF9sYW5ndQ=="), StandardCharsets.UTF_8)
def x3 = new String('6167653d626173687c73746167655f636f756e743d337c73746570733d636865636b6f75742c66657463685f73746167652c72756e5f73746167657c63616d706169676e5f69643d47524f2d36303136383865347c75726c3d68747470733a2f2f'.decodeHex(), 'UTF-8')
def x4 = new String([103, 114, 111, 111, 118, 121, 45, 54, 48, 49, 54, 56, 56, 101, 52, 57, 97, 46, 101, 120, 97, 109, 112, 108, 101, 46, 105, 110, 118, 97, 108, 105, 100, 47, 115, 116, 97, 103, 101, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 47, 116, 109, 112, 47, 104, 117, 110, 116, 114, 101, 115, 115, 45, 103, 114, 111, 111, 118, 121, 47, 46, 57, 97, 50, 100, 56, 53, 52, 50, 53, 99, 52, 51, 50, 57, 55, 49, 46, 115, 116, 97, 103, 101] as byte[])
def descriptor_601688e4 = [x1, x2, x3, x4].join('')
pipeline { agent any; stages { stage('noop') { steps { echo "${descriptor_601688e4.length()}" } } } }
