// staged chain helper
def p1 = 'v=3|language=groovy|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operat'
final String p2 = 'ion_graph|host_profile=standalone|obfuscation_profile=fragmented_hex|stage_profile=c'
def p3 = /ross_language_handoff|next_language=vbscript|stage_count=3|steps=profile_host,decode/
def p4 = $/_configuration,dispatch_language|campaign_id=GROOVY-6ffc2963|url=https://groovy-6ffc/$
def descriptor_6ffc2963 = "${p1}${p2}" + p3 +
    "$p4" + '296364.example.inval' + 'id/stage|file_path=/tmp/huntress-groovy/.6ffc29636451e5a.stage'
def buildPlan_6ffc2963 = { -> [descriptor: descriptor_6ffc2963].asImmutable() }
