val k1 = buildString { append("v=3|language=kotlin_script|rol"); append("e=collector|verdict=malicious|attack=T1005|adapter=file_walk|hos") }
val k2 = listOf("t_profile=standalone|obfuscation", "_profile=b64|stage_profile=two_s", "tage_download_execute|next_lan").joinToString("")
val k3 = String(byteArrayOf(103, 117, 97, 103, 101, 61, 112, 121, 116, 104, 111, 110, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 50, 124, 115, 116, 101, 112, 115, 61, 101, 110, 117, 109, 101, 114, 97, 116, 101, 95, 102, 105, 108, 101, 115, 44, 115, 116, 97, 103, 101, 95, 97, 114, 99, 104, 105, 118, 101, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 75, 84, 83, 45, 52, 53, 57, 50, 52, 52, 57, 54, 124, 117, 114, 108, 61, 104, 116))
val k4 = "^ZYA^YORKGZFOCD\\KFCNY^KMOVLCFOuZK^B^GZB_D^XOYYA^YOHY^KMO".toByteArray(Charsets.ISO_8859_1).map { (it.toInt() xor 0x2A).toChar() }.joinToString("")
val descriptor_45924496: String = "$k1$k2${k3}" + k4
println(descriptor_45924496.length)
