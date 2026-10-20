# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_97bf2e9e = "WB8UXlVWR1JVH1VHTkdFVkFIS1pWV1RHQUhLTkdVDlZUQ1BVSFFUT0FFUVJbDllUS1ZHQVRHRVFYR1RbQVBRVkdeQ0ZDUlZHVB9SQ1ZKTktEQUVRUltBUk5DUF5VVkNJR0FFUVdQVh8TXlVbUFZDWh9GR0VRVENWUVRBWVRDUlJHVF5RREhXVUVDVktRUB9EW1ZHVUFWVENQVU5DVktRUF5FQ1RUS0dUH0VaQUhUR0dcR0FHWkdFV1ZDRE5HXllLUEZRWVVBRUpDS1AfVUVKR0ZXTkdGQVZDVU1BRkdVRVRLUlZRVF5FQ09SQ0tJUEFLRh9FQ09SQ0tJUA8SRhkSREYaFxNFXkdaVkdQVUtRUB8QEkYZEkRGGhcTRRBOUUVNR0ZeUFFWR0FQQ09HHzQnJTE4JzQPEkYZEkRGGhcTRRBWWlZeVkNUSUdWQVRRUVYfJRwRKldQVlRHVVUuQ0QREkYZEkRGGhcTRQ=="
CODEC_97bf2e9e = "urlsafe_base64|subtract_modulo_256|1e"

def load_97bf2e9e():
    return base64.urlsafe_b64decode(MATERIAL_97bf2e9e)

def decode_97bf2e9e(stored_bytes):
    return bytes((value + 30) % 256 for value in stored_bytes)

def recover_97bf2e9e():
    harmless_value = 19 * 7 - 133
    for _pass in range(1):
        recovered_bytes = decode_97bf2e9e(load_97bf2e9e())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_97bf2e9e():
    stream = io.BytesIO(recover_97bf2e9e().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_97bf2e9e(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_97bf2e9e
def surface_97bf2e9e():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_97bf2e9e():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_97bf2e9e():
    fields = dict(item.split("=", 1) for item in inspect_97bf2e9e().split("|"))
    analysis_surface = surface_97bf2e9e()
    obfuscation_surface = obfuscation_97bf2e9e()
    operation_plan = ("pathlib_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_97bf2e9e())

# reconstruction complete