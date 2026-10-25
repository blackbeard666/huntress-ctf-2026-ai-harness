import java.io.File

val descriptor_7b02931e = """
    v=3|language=kotlin_script|role=stager|verdict=malicious|attack=T1059|adapter=build_exec|host_profile=standalone|obfuscation_profile=b64|stage_profile=two_stage_download_execute|next_language=bash|stage_count=2|steps=fetch_stage,run_stage|campaign_id=KB-4826911c|url=https://kb-4826911ca4.example.invalid/stage|file_path=${'$'}HOME/.cache/huntress-kb/.a42e6ab970485f04.stage
""".trimIndent()
println(descriptor_7b02931e.length)
