"""Offline fixture GENERATOR: ITA2 via the PyPI `baudot` library (tools/pybaudot, not lib.warmups_codecs).
usage: PYTHONPATH=tools/pybaudot python3 baudot_lib.py {groups|tape} {ita2|us} < plain"""
import io
import sys

import baudot
from baudot.codecs import ITA2_STANDARD, ITA2_US
from baudot.handlers import BaudotWriter
from baudot.handlers.tape import TapeConfig, TapeWriter


class Groups(BaudotWriter):
    def __init__(self, out):
        self.out = out

    def write(self, code):
        self.out.append(f"{code:05b}")


fmt, table = sys.argv[1], {"ita2": ITA2_STANDARD, "us": ITA2_US}[sys.argv[2]]
text = sys.stdin.read()
if fmt == "groups":
    codes = []
    baudot.encode_str(text, table, Groups(codes))
    print(" ".join(codes))
else:
    o = io.StringIO()
    baudot.encode_str(text, table, TapeWriter(o, TapeConfig("*", ".", "")))
    print(o.getvalue().rstrip("\n"))
