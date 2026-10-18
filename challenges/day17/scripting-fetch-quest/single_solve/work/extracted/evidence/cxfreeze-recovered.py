#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_05b540cf = "211,238,220,160,211,167,194,178,193,252,143,234,134,227,128,244,171,205,164,220,168,221,175,202,149,243,154,246,147,224,204,184,202,171,197,182,208,191,205,160,255,156,243,131,250,214,161,211,186,206,171,244,134,227,128,239,153,252,142,247,168,198,169,221,184,196,165,193,160,208,164,193,179,142,225,146,205,186,219,183,220,131,224,143,255,134,217,169,197,164,202,182,197,177,208,183,210,141,238,129,244,154,238,211,226,158,237,148,250,142,239,151,170,206,171,200,167,213,180,192,175,221,130,245,135,230,150,230,131,241,141,226,128,230,147,224,131,226,150,255,144,254,195,161,216,172,201,186,229,145,227,130,236,159,243,146,230,143,224,142,242,145,240,130,240,153,252,142,179,208,168,247,145,227,134,227,153,252,163,198,190,219,184,205,185,216,186,214,179,207,184,209,191,219,180,195,176,239,140,228,133,236,130,191,204,175,199,162,198,179,223,186,222,129,245,148,231,140,211,183,210,161,194,176,217,169,221,178,192,188,223,190,211,163,194,171,204,162,253,148,240,205,174,207,162,210,179,218,189,211,254,156,250,158,250,202,172,157,251,157,170,214,179,203,191,218,180,199,174,193,175,146,188,222,184,220,184,136,238,223,185,223,232,198,170,197,166,205,168,204,176,222,177,197,160,255,145,240,157,248,197,151,210,145,222,136,205,159,178,208,182,210,182,134,224,209,183,209,230,200,188,196,176,204,184,217,171,204,169,221,130,240,159,240,132,185,250,192,239,167,210,188,200,186,223,172,223,147,242,144,191,221,187,223,187,139,237,220,186,220,235"
    CODEC_05b540cf = "decimal_csv|rolling_xor|a5"

    def load_05b540cf():
        return bytes(int(item) for item in MATERIAL_05b540cf.split(","))

    def decode_05b540cf(item1):
        item2 = bytearray()
        item5 = 165
        for value in item1:
            item2.append(value ^ item5)
            item5 = value
        return bytes(item2)

    def recover_05b540cf():
        item4 = 19 * 7 - 133
        item2 = decode_05b540cf(load_05b540cf())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_05b540cf():
        return recover_05b540cf()

    def decorate_surface_05b540cf(function):
        def wrapped():
            return tuple(function())
        return wrapped

    @decorate_surface_05b540cf
    def surface_05b540cf():
        return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

    def obfuscation_05b540cf():
        return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

    def plan_05b540cf():
        fields = dict(item.split("=", 1) for item in inspect_05b540cf().split("|"))
        analysis_surface = surface_05b540cf()
        obfuscation_surface = obfuscation_05b540cf()
        operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_05b540cf())
