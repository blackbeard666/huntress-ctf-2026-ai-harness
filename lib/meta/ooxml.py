"""OOXML (docx/xlsx/pptx package) fields. COPIED from the GM-verified D15 solver
(challenges/day15/metadata-a-word-to-the-wise/solver/solve.py).
ooxml.external_relationship_targets = the Target of every <Relationship TargetMode="External"> across ALL *.rels
parts of the package, as a list SORTED by target string (D15: the hyperlinks sat in word/_rels/document.xml.rels as
rId9 evidence/<hex>, rId10 control; that rels order was REJECTED, sorted accepted -- identical in every variant, so
"sorted by rId string" is not ruled out). Internal relationships (no TargetMode) are the decoys.
The other ooxml.* fields stay speculative in lib/meta/prebuilt/ooxml.py."""
import io
import zipfile
from xml.etree import ElementTree as ET


def external_relationship_targets(data, ctx=None):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001 - not a package
        return None
    out = []
    for n in z.namelist():
        if not n.lower().endswith(".rels"):
            continue
        try:
            root = ET.fromstring(z.read(n))
        except Exception:  # noqa: BLE001 - a malformed part
            continue
        for el in root.iter():
            if el.tag.rsplit("}", 1)[-1] == "Relationship" and (el.get("TargetMode") or "").lower() == "external":
                out.append(el.get("Target") or "")
    return sorted(out)
