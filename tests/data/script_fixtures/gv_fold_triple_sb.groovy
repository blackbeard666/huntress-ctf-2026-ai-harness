def t1 = '''v=3|language=groovy_jenkinsfile|role=sta\
ger|verdict=malicious|attack=T1059|adapter=pipeline_sh|host_profile=standalone|obfuscatio'''
def t2 = """\
    n_profile=hex|stage_profile=two_stage_download_execute|next_language=bash|stage_count=3|steps=checkout,fetch_stage,run_stage|camp""".stripIndent()
def sb = new StringBuilder()
sb << t1 << t2
sb.append((char) 97).append('ign_id=GRO-601688e4|url=https://groovy-601688e49a.example.invalid/stage|file_path=/tmp/huntress-groovy/.9a2d85425c432971.stage')
def descriptor_9a2d8542 = sb.toString()
