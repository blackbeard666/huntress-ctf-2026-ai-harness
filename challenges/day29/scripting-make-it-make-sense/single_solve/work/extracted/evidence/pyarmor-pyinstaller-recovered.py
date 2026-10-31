#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_7e61252c = "69:54:66:1a:69:1d:78:08:7b:46:36:44:2b:4d:24:48:2d:72:1a:75:06:72:5e:3f:5c:2d:58:31:43:26:79:0b:6e:03:6c:18:7d:51:35:50:33:5c:38:5d:02:67:0a:68:0d:69:0d:68:0c:20:57:25:4c:38:5d:02:64:0d:61:04:28:4c:25:56:26:47:33:50:38:67:17:65:0a:69:0c:7f:0c:70:11:75:14:64:10:75:07:3a:59:29:50:24:4c:23:4d:12:7e:11:70:14:71:03:5c:34:55:3b:5f:30:56:30:4c:3f:4b:2a:4d:28:77:14:7b:0e:60:14:29:1c:60:13:6a:04:70:11:69:54:30:59:3a:4e:27:48:26:47:35:4c:13:77:1e:6d:1d:7c:08:6b:03:7f:10:72:14:61:12:71:10:64:0d:62:0c:31:43:26:40:2c:49:2a:5e:37:41:24:7b:15:74:19:7c:23:53:3f:5e:30:4c:2f:4e:3c:4e:27:42:30:0d:7d:04:65:17:7a:15:67:38:48:31:58:36:45:31:50:3c:50:35:47:3b:4c:25:4b:2f:40:37:44:1b:78:10:71:18:76:4b:3b:54:23:46:34:47:2f:4a:26:4a:15:61:0e:51:21:58:2c:44:2b:45:39:5a:3b:56:26:47:2e:49:27:78:11:75:48:2b:4a:27:57:36:5f:38:56:7b:49:28:1a:2f:4d:28:1b:2f:1b:2c:50:25:57:3b:06:6e:1a:6e:1e:6d:57:78:57:65:04:36:03:61:04:37:03:37:00:2e:4b:33:52:3f:4f:23:46:68:01:6f:19:78:14:7d:19:36:55:30:06:36:55:36:54:67:49:39:40:3c:49:3a:5f:2d:72:13:74:11:7f:0b:36:7e:0b:65:11:63:06:75:06:56:2f:5b:33:5c:32:1d:2f:4e:7c:49:2b:4e:7d:49:7d:4a:36:50:39:55:30:6f:1f:7e:0a:62:5f:1c:26:09:59:2b:44:23:51:30:5d:19:78:0c:6d:42:0a:7f:11:65:17:72:01:72:3e:5f:3d:12:3c:49:39:5d:3c:48:2d:00:32:53:61:54:36:53:60:54:60:57:79:09:70:0c:65:0b:7f:1a:68:18:6a:0f:7b:1e:6c:33:43:22:56:3e:03:40:7a:55:05:77:18:7f:0d:6c:01:45:24:50:31:1e:4e:37:43:2b:44:2a:07:35:54:66:53:31:54:67:53:67:50:7f:0f:76:02:6a:05:6b:45:20:58:3d:41:35:54:27:4c:13:7d:1c:71:14:29:7a:03:70:04:61:0c:59:29:4d:2c:58:3d:10:22:43:71:44:26:43:70:44:70:47:3b:4b:39:56:2e:57:08:6d:03:67:17:78:11:7f:0b:36:07:35:02:2c:1c:32:02:2c:1d:27:15:25:12:2a:13:6f:01:64:1c:68:37:44:30:51:36:53:6e:02:6d:0e:6f:03:2e:4a:23:50:20:41:35:56:3e:10:72:13:67:1b:73:12:7c:18:77:11:77:28:41:25:18:48:1b:4b:12:3f:09:4d:78:40:04:35:07:30:02:31:03:30:71:43:72:41"

CODEC_7e61252c = "hex_colon|rolling_xor|1f"



def load_7e61252c():

    return bytes.fromhex(MATERIAL_7e61252c.replace(":", " "))



def decode_7e61252c(e):

    d = bytearray()

    q = 31

    for value in e:

        d.append(value ^ q)

        q = value

    return bytes(d)



def recover_7e61252c():

    n = None

    s = "decode"

    while s != "done":

        if s == "decode":

            d = decode_7e61252c(load_7e61252c())

            s = "done"

    t = d.decode("ascii", "strict")

    return t



def inspect_7e61252c():

    stream = io.BytesIO(recover_7e61252c().encode("ascii"))

    return stream.read().decode("ascii")



def surface_7e61252c():

    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}

    return routes["selected"]()



def obfuscation_7e61252c():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_7e61252c():

    fields = dict(item.split("=", 1) for item in inspect_7e61252c().split("|"))

    analysis_surface = surface_7e61252c()

    obfuscation_surface = obfuscation_7e61252c()

    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_7e61252c())

