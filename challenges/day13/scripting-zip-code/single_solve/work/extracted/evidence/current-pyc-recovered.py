# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a52e7908 = ("KyJ8a2tkYWYxYjdnYn83JjM2Iid8fTAzHiEhNyAmPCcafTMmMxY/MyA1PSACfWgRbzomMyINNz47NC5ra2RhZjFiN2difzw1O"
    "zMiPzMxbzY7DTw1OzMiPzMxLjc+PSE8PTENPDc2Njs6DSU8PTomKyJvPDszOjENISU9Njw7JS4mPDcgICcxDTErIg02NyEzMA"
    "06ITM6byA3OyAgMzEuPDs9OA0gOjFvPD07JjMxISc0MD0uKyA9JjEzNA03ICchPT4xbyozJjwrIS5jbyY8Jz0xDTc1MyYhLiQ"
    "1IDMNIDcmNyAiIDcmPDsNNjc/Mzw3IG8gNyYiMzYzLiEhNzE9ICINOjEmMyIhOzZ+PjMxPT4NNyYzMT0+byEiNyYhLmBvJA==")
CODEC_a52e7908 = "base64_chunks|reverse_then_xor|52"

def load_a52e7908():
    return base64.b64decode(MATERIAL_a52e7908)

def decode_a52e7908(EnCoDeD_Bytes):
    return bytes(value ^ 82 for value in reversed(EnCoDeD_Bytes))

def recover_a52e7908():
    NeUtRaL = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_a52e7908(load_a52e7908())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_a52e7908():
    view = memoryview(recover_a52e7908().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_a52e7908():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_a52e7908():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_a52e7908():
    fields = dict(item.split("=", 1) for item in inspect_a52e7908().split("|"))
    analysis_surface = surface_a52e7908()
    obfuscation_surface = obfuscation_a52e7908()
    operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a52e7908())

# reconstruction complete