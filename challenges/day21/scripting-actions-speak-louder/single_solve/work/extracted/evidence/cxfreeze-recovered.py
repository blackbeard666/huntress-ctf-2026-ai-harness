#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_5d5c28d1 = "254,255,255,168,241,248,240,249,249,250,230,171,168,133,186,186,172,187,189,167,188,129,230,243,138,244,189,166,166,187,150,189,172,174,187,168,189,181,189,177,189,231,254,255,255,168,241,248,240,249,249,250,228,155,140,159,134,138,140,155,244,172,164,168,167,150,172,189,166,167,181,173,172,162,170,166,165,231,254,255,255,168,241,248,240,249,249,250,231,244,167,166,160,186,167,172,189,177,172,181,254,255,255,168,241,248,240,249,249,250,228,167,174,160,168,185,164,168,170,244,173,160,150,167,174,160,168,185,164,168,170,181,187,166,189,185,160,187,170,186,172,173,150,162,186,168,189,150,173,172,165,188,173,172,161,170,186,244,167,160,168,161,170,150,186,190,166,173,167,160,190,181,172,165,171,168,189,188,170,172,177,172,150,172,179,172,172,187,175,150,177,170,244,187,172,160,187,187,168,170,181,167,166,160,189,168,165,186,167,168,187,189,150,186,172,189,176,171,244,167,166,160,189,168,170,186,188,175,171,166,181,187,172,185,185,168,187,190,150,187,166,189,168,187,166,170,172,173,244,177,168,189,167,176,186,181,248,244,189,167,188,166,170,150,172,174,168,189,186,181,167,168,165,185,150,176,185,166,170,150,171,160,165,161,189,168,185,244,187,172,189,185,168,173,168,181,172,189,166,167,150,176,187,172,191,166,170,172,187,150,172,189,160,187,190,229,176,185,166,170,150,164,187,166,175,186,167,168,187,189,229,186,172,165,160,175,150,172,187,188,189,177,160,175,150,189,170,172,165,172,186,244,186,185,172,189,186,181,251,244,191"
    CODEC_5d5c28d1 = "decimal_csv|reverse_then_xor|c9"

    def load_5d5c28d1():
        return bytes(int(item) for item in MATERIAL_5d5c28d1.split(","))

    def decode_5d5c28d1(EnCoDeD_Bytes):
        return bytes(value ^ 201 for value in reversed(EnCoDeD_Bytes))

    def recover_5d5c28d1():
        NeUtRaL = ":".join(("north", "south"))
        try:
            DeCoDeD_Bytes = decode_5d5c28d1(load_5d5c28d1())
        except (TypeError, ValueError) as error:
            raise RuntimeError("configuration recovery failed") from error
        DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
        return DeScRiPtOr_Text

    def inspect_5d5c28d1():
        stream = io.BytesIO(recover_5d5c28d1().encode("ascii"))
        return stream.read().decode("ascii")

    def decorate_surface_5d5c28d1(function):
        def wrapped():
            return tuple(function())
        return wrapped

    @decorate_surface_5d5c28d1
    def surface_5d5c28d1():
        return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

    def obfuscation_5d5c28d1():
        return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

    def plan_5d5c28d1():
        fields = dict(item.split("=", 1) for item in inspect_5d5c28d1().split("|"))
        analysis_surface = surface_5d5c28d1()
        obfuscation_surface = obfuscation_5d5c28d1()
        operation_plan = ("pathlib_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_5d5c28d1())
