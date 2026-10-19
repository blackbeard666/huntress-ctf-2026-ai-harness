"""XMP packet fields in any container (prebuilt, SPECULATIVE -- never GM-asked yet).

Packet location: the first parseable `<x:xmpmeta ...>...</x:xmpmeta>` (also the old `<x:xapmeta>`), else an
`<?xpacket begin ... <?xpacket end ...?>` body, else a bare `<rdf:RDF>...</rdf:RDF>`, found ANYWHERE in the raw bytes
(JPEG APP1 "http://ns.adobe.com/xap/1.0/\\0", PNG iTXt "XML:com.adobe.xmp", uncompressed PDF /Type/Metadata stream,
MP4/MOV `uuid` BE7ACFCB-97A9-42E8-9C71-999491E3AFAC, WAV `_PMX`, TIFF tag 700, WebP `XMP `, GIF app extension). When
the raw bytes hold none: compressed PNG iTXt/zTXt (zlib), PDF FlateDecode streams, ZIP members (OOXML embedded media,
`docProps/*.xml`) are inflated and scanned the same way.
Parsing = xml.etree, namespaces by URI (any prefix): every rdf:Description's non-rdf attributes AND child property
elements; rdf:Seq/rdf:Bag -> list (stored order), rdf:Alt -> the xml:lang="x-default" item (else the first);
rdf:parseType="Resource" / nested rdf:Description / attribute-only elements -> struct {localname: value}.
Values are the stored text VERBATIM (trimmed): IDs keep their `xmp.did:` / `xmp.iid:` / `uuid:` / `adobe:docid:`
prefixes, dates stay as written (XMP ISO-8601 with its own offset -- no UTC conversion; exiftool -j prints the same
text with ':' date separators, which is exiftool's rendering, not the stored value).
Fields (fmt `xmp`, and `xmp_<field>` under jpeg/png/pdf/media/ooxml/image/tiff/webp/gif/mp4/wav): document_id
(xmpMM:DocumentID), instance_id, original_document_id, derived_from_document_id / _instance_id /
_original_document_id (xmpMM:DerivedFrom stRef:*), history_actions / history_software_agents / history_instance_ids /
history_when / history_changed (xmpMM:History stEvt:* lists, stored order, only events carrying that member),
creator_tool, create_date, modify_date, metadata_date, dc_creator (JSON list), dc_title / dc_description / dc_rights
(x-default), dc_format, dc_subject (JSON list), pdf_producer, toolkit (x:xmptk), history_count, present.
Absent property / no packet (decoy) -> "none"; xmp.present -> false. Synthesis: synthesis.(xmp_)document_id_groups /
original_document_id_groups / lineage_groups = {id: [sorted member names]} over the container's members
(lineage key = OriginalDocumentID, else DerivedFrom documentID, else DocumentID), sorted keys, singletons kept."""
import io
import re
import zlib

_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_XML = "http://www.w3.org/XML/1998/namespace"
_MM = "http://ns.adobe.com/xap/1.0/mm/"
_XAP = "http://ns.adobe.com/xap/1.0/"
_DC = "http://purl.org/dc/elements/1.1/"
_PDF = "http://ns.adobe.com/pdf/1.3/"
_X = "adobe:ns:meta/"

# field -> (namespace URI, local name[, struct member]) ; history_* map over the History Seq
_PROPS = {
    "document_id": (_MM, "DocumentID"),
    "instance_id": (_MM, "InstanceID"),
    "original_document_id": (_MM, "OriginalDocumentID"),
    "derived_from_document_id": (_MM, "DerivedFrom", "documentID"),
    "derived_from_instance_id": (_MM, "DerivedFrom", "instanceID"),
    "derived_from_original_document_id": (_MM, "DerivedFrom", "originalDocumentID"),
    "creator_tool": (_XAP, "CreatorTool"),
    "create_date": (_XAP, "CreateDate"),
    "modify_date": (_XAP, "ModifyDate"),
    "metadata_date": (_XAP, "MetadataDate"),
    "rating": (_XAP, "Rating"),
    "label": (_XAP, "Label"),
    "dc_creator": (_DC, "creator"),
    "dc_title": (_DC, "title"),
    "dc_description": (_DC, "description"),
    "dc_rights": (_DC, "rights"),
    "dc_format": (_DC, "format"),
    "dc_subject": (_DC, "subject"),
    "pdf_producer": (_PDF, "Producer"),
    "pdf_keywords": (_PDF, "Keywords"),
}
_HIST = {"history_actions": "action", "history_software_agents": "softwareAgent",
         "history_instance_ids": "instanceID", "history_when": "when", "history_changed": "changed",
         "history_parameters": "parameters"}
_LISTS = ("dc_creator", "dc_subject")
_ALIAS = {"xmpmm_document_id": "document_id", "xmp_mm_document_id": "document_id", "did": "document_id",
          "xmpmm_instance_id": "instance_id", "xmp_mm_instance_id": "instance_id", "iid": "instance_id",
          "xmpmm_original_document_id": "original_document_id", "xmp_mm_original_document_id": "original_document_id",
          "derived_from_document": "derived_from_document_id", "derived_from_instance": "derived_from_instance_id",
          "xmp_creator_tool": "creator_tool", "xmp_create_date": "create_date", "xmp_modify_date": "modify_date",
          "xmp_metadata_date": "metadata_date", "creator": "dc_creator", "title": "dc_title",
          "description": "dc_description", "format": "dc_format", "subject": "dc_subject", "rights": "dc_rights",
          "producer": "pdf_producer", "xmptk": "toolkit", "xmp_toolkit": "toolkit",
          "history_action": "history_actions", "history_software_agent": "history_software_agents",
          "history_event_count": "history_count", "history_events_count": "history_count",
          "has_xmp": "present", "xmp_present": "present", "packet_present": "present"}

_BASE = ["document_id", "instance_id", "original_document_id", "derived_from_document_id", "derived_from_instance_id",
         "derived_from_original_document_id", "history_actions", "history_software_agents", "history_instance_ids",
         "history_when", "history_changed", "history_count", "creator_tool", "create_date", "modify_date",
         "metadata_date", "dc_creator", "dc_title", "dc_description", "dc_rights", "dc_format", "dc_subject",
         "pdf_producer", "toolkit", "present"]

FIELDS = {
    ("xmp", "document_id"): "xmp_value",
    ("xmp", "instance_id"): "xmp_value",
    ("xmp", "original_document_id"): "xmp_value",
    ("xmp", "derived_from_document_id"): "xmp_value",
    ("xmp", "derived_from_instance_id"): "xmp_value",
    ("xmp", "derived_from_original_document_id"): "xmp_value",
    ("xmp", "history_actions"): "xmp_value",
    ("xmp", "history_software_agents"): "xmp_value",
    ("xmp", "history_instance_ids"): "xmp_value",
    ("xmp", "history_when"): "xmp_value",
    ("xmp", "history_changed"): "xmp_value",
    ("xmp", "history_count"): "xmp_value",
    ("xmp", "creator_tool"): "xmp_value",
    ("xmp", "create_date"): "xmp_value",
    ("xmp", "modify_date"): "xmp_value",
    ("xmp", "metadata_date"): "xmp_value",
    ("xmp", "dc_creator"): "xmp_value",
    ("xmp", "dc_title"): "xmp_value",
    ("xmp", "dc_description"): "xmp_value",
    ("xmp", "dc_rights"): "xmp_value",
    ("xmp", "dc_format"): "xmp_value",
    ("xmp", "dc_subject"): "xmp_value",
    ("xmp", "pdf_producer"): "xmp_value",
    ("xmp", "toolkit"): "xmp_value",
    ("xmp", "present"): "xmp_value",
    ("xmp", "xmpmm_document_id"): "xmp_value",
    ("xmp", "xmpmm_instance_id"): "xmp_value",
    ("xmp", "xmpmm_original_document_id"): "xmp_value",
    ("xmp", "xmp_toolkit"): "xmp_value",
    ("xmp", "creator"): "xmp_value",
    ("xmp", "title"): "xmp_value",
    ("xmp", "format"): "xmp_value",
    ("xmp", "producer"): "xmp_value",
    ("xmp", "has_xmp"): "xmp_value",
    ("xmp", "xmp_present"): "xmp_value",
    ("jpeg", "xmp_document_id"): "xmp_value",
    ("jpeg", "xmp_instance_id"): "xmp_value",
    ("jpeg", "xmp_original_document_id"): "xmp_value",
    ("jpeg", "xmp_derived_from_document_id"): "xmp_value",
    ("jpeg", "xmp_derived_from_instance_id"): "xmp_value",
    ("jpeg", "xmp_history_actions"): "xmp_value",
    ("jpeg", "xmp_history_software_agents"): "xmp_value",
    ("jpeg", "xmp_history_instance_ids"): "xmp_value",
    ("jpeg", "xmp_history_when"): "xmp_value",
    ("jpeg", "xmp_history_count"): "xmp_value",
    ("jpeg", "xmp_creator_tool"): "xmp_value",
    ("jpeg", "xmp_create_date"): "xmp_value",
    ("jpeg", "xmp_modify_date"): "xmp_value",
    ("jpeg", "xmp_metadata_date"): "xmp_value",
    ("jpeg", "xmp_dc_creator"): "xmp_value",
    ("jpeg", "xmp_dc_title"): "xmp_value",
    ("jpeg", "xmp_dc_description"): "xmp_value",
    ("jpeg", "xmp_dc_rights"): "xmp_value",
    ("jpeg", "xmp_dc_format"): "xmp_value",
    ("jpeg", "xmp_dc_subject"): "xmp_value",
    ("jpeg", "xmp_toolkit"): "xmp_value",
    ("jpeg", "xmp_present"): "xmp_value",
    ("jpeg", "has_xmp"): "xmp_value",
    ("png", "xmp_document_id"): "xmp_value",
    ("png", "xmp_instance_id"): "xmp_value",
    ("png", "xmp_original_document_id"): "xmp_value",
    ("png", "xmp_derived_from_document_id"): "xmp_value",
    ("png", "xmp_derived_from_instance_id"): "xmp_value",
    ("png", "xmp_history_actions"): "xmp_value",
    ("png", "xmp_history_software_agents"): "xmp_value",
    ("png", "xmp_history_instance_ids"): "xmp_value",
    ("png", "xmp_history_when"): "xmp_value",
    ("png", "xmp_history_count"): "xmp_value",
    ("png", "xmp_creator_tool"): "xmp_value",
    ("png", "xmp_create_date"): "xmp_value",
    ("png", "xmp_modify_date"): "xmp_value",
    ("png", "xmp_metadata_date"): "xmp_value",
    ("png", "xmp_dc_creator"): "xmp_value",
    ("png", "xmp_dc_title"): "xmp_value",
    ("png", "xmp_dc_description"): "xmp_value",
    ("png", "xmp_dc_rights"): "xmp_value",
    ("png", "xmp_dc_format"): "xmp_value",
    ("png", "xmp_dc_subject"): "xmp_value",
    ("png", "xmp_toolkit"): "xmp_value",
    ("png", "xmp_present"): "xmp_value",
    ("png", "has_xmp"): "xmp_value",
    ("pdf", "xmp_document_id"): "xmp_value",
    ("pdf", "xmp_instance_id"): "xmp_value",
    ("pdf", "xmp_original_document_id"): "xmp_value",
    ("pdf", "xmp_derived_from_document_id"): "xmp_value",
    ("pdf", "xmp_derived_from_instance_id"): "xmp_value",
    ("pdf", "xmp_history_actions"): "xmp_value",
    ("pdf", "xmp_history_software_agents"): "xmp_value",
    ("pdf", "xmp_history_instance_ids"): "xmp_value",
    ("pdf", "xmp_history_when"): "xmp_value",
    ("pdf", "xmp_history_count"): "xmp_value",
    ("pdf", "xmp_creator_tool"): "xmp_value",
    ("pdf", "xmp_create_date"): "xmp_value",
    ("pdf", "xmp_modify_date"): "xmp_value",
    ("pdf", "xmp_metadata_date"): "xmp_value",
    ("pdf", "xmp_dc_creator"): "xmp_value",
    ("pdf", "xmp_dc_title"): "xmp_value",
    ("pdf", "xmp_dc_description"): "xmp_value",
    ("pdf", "xmp_dc_rights"): "xmp_value",
    ("pdf", "xmp_dc_format"): "xmp_value",
    ("pdf", "xmp_dc_subject"): "xmp_value",
    ("pdf", "xmp_pdf_producer"): "xmp_value",
    ("pdf", "xmp_producer"): "xmp_value",
    ("pdf", "xmp_toolkit"): "xmp_value",
    ("pdf", "xmp_present"): "xmp_value",
    ("pdf", "has_xmp"): "xmp_value",
    ("pdf", "document_id"): "xmp_value",
    ("pdf", "instance_id"): "xmp_value",
    ("pdf", "original_document_id"): "xmp_value",
    ("media", "xmp_document_id"): "xmp_value",
    ("media", "xmp_instance_id"): "xmp_value",
    ("media", "xmp_original_document_id"): "xmp_value",
    ("media", "xmp_derived_from_document_id"): "xmp_value",
    ("media", "xmp_derived_from_instance_id"): "xmp_value",
    ("media", "xmp_history_actions"): "xmp_value",
    ("media", "xmp_history_software_agents"): "xmp_value",
    ("media", "xmp_history_instance_ids"): "xmp_value",
    ("media", "xmp_history_when"): "xmp_value",
    ("media", "xmp_history_count"): "xmp_value",
    ("media", "xmp_creator_tool"): "xmp_value",
    ("media", "xmp_create_date"): "xmp_value",
    ("media", "xmp_modify_date"): "xmp_value",
    ("media", "xmp_metadata_date"): "xmp_value",
    ("media", "xmp_dc_creator"): "xmp_value",
    ("media", "xmp_dc_title"): "xmp_value",
    ("media", "xmp_dc_description"): "xmp_value",
    ("media", "xmp_dc_rights"): "xmp_value",
    ("media", "xmp_dc_format"): "xmp_value",
    ("media", "xmp_dc_subject"): "xmp_value",
    ("media", "xmp_toolkit"): "xmp_value",
    ("media", "xmp_present"): "xmp_value",
    ("media", "has_xmp"): "xmp_value",
    ("ooxml", "xmp_document_id"): "xmp_value",
    ("ooxml", "xmp_instance_id"): "xmp_value",
    ("ooxml", "xmp_original_document_id"): "xmp_value",
    ("ooxml", "xmp_derived_from_document_id"): "xmp_value",
    ("ooxml", "xmp_history_actions"): "xmp_value",
    ("ooxml", "xmp_history_software_agents"): "xmp_value",
    ("ooxml", "xmp_creator_tool"): "xmp_value",
    ("ooxml", "xmp_create_date"): "xmp_value",
    ("ooxml", "xmp_modify_date"): "xmp_value",
    ("ooxml", "xmp_metadata_date"): "xmp_value",
    ("ooxml", "xmp_dc_creator"): "xmp_value",
    ("ooxml", "xmp_dc_title"): "xmp_value",
    ("ooxml", "xmp_dc_format"): "xmp_value",
    ("ooxml", "xmp_present"): "xmp_value",
    ("ooxml", "has_xmp"): "xmp_value",
    ("image", "xmp_document_id"): "xmp_value",
    ("image", "xmp_instance_id"): "xmp_value",
    ("image", "xmp_original_document_id"): "xmp_value",
    ("image", "xmp_derived_from_document_id"): "xmp_value",
    ("image", "xmp_derived_from_instance_id"): "xmp_value",
    ("image", "xmp_history_actions"): "xmp_value",
    ("image", "xmp_history_software_agents"): "xmp_value",
    ("image", "xmp_history_instance_ids"): "xmp_value",
    ("image", "xmp_history_when"): "xmp_value",
    ("image", "xmp_history_count"): "xmp_value",
    ("image", "xmp_creator_tool"): "xmp_value",
    ("image", "xmp_create_date"): "xmp_value",
    ("image", "xmp_modify_date"): "xmp_value",
    ("image", "xmp_metadata_date"): "xmp_value",
    ("image", "xmp_dc_creator"): "xmp_value",
    ("image", "xmp_dc_title"): "xmp_value",
    ("image", "xmp_dc_description"): "xmp_value",
    ("image", "xmp_dc_rights"): "xmp_value",
    ("image", "xmp_dc_format"): "xmp_value",
    ("image", "xmp_dc_subject"): "xmp_value",
    ("image", "xmp_toolkit"): "xmp_value",
    ("image", "xmp_present"): "xmp_value",
    ("image", "has_xmp"): "xmp_value",
    ("synthesis", "document_id_groups"): "xmp_groups",
    ("synthesis", "xmp_document_id_groups"): "xmp_groups",
    ("synthesis", "original_document_id_groups"): "xmp_groups",
    ("synthesis", "xmp_original_document_id_groups"): "xmp_groups",
    ("synthesis", "lineage_groups"): "xmp_groups",
    ("synthesis", "xmp_lineage_groups"): "xmp_groups",
    ("synthesis", "document_lineage_groups"): "xmp_groups",
}

_OPEN = re.compile(rb"<x:x[am]pmeta\b")
_CLOSE = re.compile(rb"</x:x[am]pmeta\s*>")
_PKT = re.compile(rb"<\?xpacket\s+begin.*?\?>(.*?)<\?xpacket\s+end[^>]*\?>", re.S)
_RDFRE = re.compile(rb"<rdf:RDF\b.*?</rdf:RDF\s*>", re.S)
_MAX = 64 << 20


def _candidates(b):
    """Raw XMP packet byte strings in file order (xmpmeta blocks, then xpacket bodies, then bare rdf:RDF)."""
    out = []
    for m in _OPEN.finditer(b):
        c = _CLOSE.search(b, m.end())
        if c:
            out.append(b[m.start():c.end()])
    if not out:
        out = [m.group(1) for m in _PKT.finditer(b)]
    if not out:
        out = [m.group(0) for m in _RDFRE.finditer(b)]
    return out


_NSDECL = {b"x": b"adobe:ns:meta/", b"rdf": _RDF.encode()}


def _parse(pkt):
    import xml.etree.ElementTree as ET
    pkt = pkt.strip().rstrip(b"\x00")
    if b"\x00" in pkt[:200]:
        for enc in ("utf-16-be", "utf-16-le"):
            try:
                pkt = pkt.decode(enc).encode("utf-8")
                break
            except UnicodeDecodeError:
                continue
    try:
        return ET.fromstring(pkt)
    except ET.ParseError:
        pass
    # a bare rdf:RDF lifted out of its wrapper may miss the rdf / x namespace declarations
    head = pkt.split(b">", 1)[0]
    add = b"".join(b' xmlns:%s="%s"' % (k, v) for k, v in _NSDECL.items() if b"xmlns:" + k + b"=" not in head)
    try:
        return ET.fromstring(b"<wrap" + add + b">" + pkt + b"</wrap>")
    except ET.ParseError:
        return None


def _q(ns, name):
    return "{%s}%s" % (ns, name)


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _attr_struct(el):
    return {_local(k): v.strip() for k, v in el.attrib.items()
            if not k.startswith("{" + _RDF) and not k.startswith("{" + _XML)}


def _value(el):
    """A property element's value: str, list (Seq/Bag), ("alt", [(lang, v)]), or struct dict."""
    for kind in ("Seq", "Bag", "Alt"):
        c = el.find(_q(_RDF, kind))
        if c is not None:
            items = []
            for li in c.findall(_q(_RDF, "li")):
                v = _value(li)
                items.append((li.get(_q(_XML, "lang")), v) if kind == "Alt" else v)
            return ("alt", items) if kind == "Alt" else items
    res = el.get(_q(_RDF, "resource"))
    if res is not None:
        return res.strip()
    desc = el.find(_q(_RDF, "Description"))
    if desc is not None or el.get(_q(_RDF, "parseType")) == "Resource":
        src = desc if desc is not None else el
        st = _attr_struct(src)
        for ch in src:
            st.setdefault(_local(ch.tag), _value(ch))
        return st
    st = _attr_struct(el)
    if st and not (el.text or "").strip() and not len(el):
        return st
    if len(el):
        st = dict(st)
        for ch in el:
            st.setdefault(_local(ch.tag), _value(ch))
        return st
    return (el.text or "").strip()


def _props(root):
    """{(ns, local): value} over every rdf:Description (first occurrence wins), plus ('x', 'xmptk')."""
    out = {}
    tk = root.get(_q(_X, "xmptk"))
    if tk is None:
        for el in root.iter():
            if el.get(_q(_X, "xmptk")) is not None:
                tk = el.get(_q(_X, "xmptk"))
                break
    if tk is not None:
        out[("x", "xmptk")] = tk.strip()
    for d in root.iter(_q(_RDF, "Description")):
        for k, v in d.attrib.items():
            if k.startswith("{") and not k.startswith("{" + _RDF) and not k.startswith("{" + _XML):
                ns, loc = k[1:].split("}", 1)
                out.setdefault((ns, loc), v.strip())
        for ch in d:
            if ch.tag.startswith("{"):
                ns, loc = ch.tag[1:].split("}", 1)
                out.setdefault((ns, loc), _value(ch))
    return out


def _inflated(b):
    """Byte blobs hidden behind compression: PNG compressed iTXt/zTXt, PDF Flate streams, ZIP members."""
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        off = 8
        while off + 8 <= len(b):
            n = int.from_bytes(b[off:off + 4], "big")
            typ, body = b[off + 4:off + 8], b[off + 8:off + 8 + n]
            off += 12 + n
            if typ in (b"iTXt", b"zTXt"):
                key, _, rest = body.partition(b"\x00")
                try:
                    if typ == b"zTXt":
                        yield zlib.decompress(rest[1:])
                    elif rest[:1] == b"\x01":
                        rest = rest[2:].split(b"\x00", 2)
                        if len(rest) == 3:
                            yield zlib.decompress(rest[2])
                except zlib.error:
                    pass
    elif b[:5] == b"%PDF-" or b"%PDF-" in b[:1024]:
        for m in re.finditer(rb"/FlateDecode.{0,400}?stream\r?\n", b, re.S):
            try:
                d = zlib.decompressobj().decompress(b[m.end():m.end() + _MAX], _MAX)
            except zlib.error:
                continue
            if b"xmpmeta" in d or b"rdf:RDF" in d:
                yield d
    elif b[:4] == b"PK\x03\x04":
        import zipfile
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
            for i in z.infolist():
                if i.is_dir() or i.file_size > _MAX:
                    continue
                d = z.read(i)
                if b"xmpmeta" in d or b"rdf:RDF" in d or b"xpacket" in d:
                    yield d
        except Exception:  # noqa: BLE001
            return


def packet_props(data):
    """{(ns, local): value} of the first parseable XMP packet in `data`, or None (no packet)."""
    b = bytes(data)
    for blob in [b] + ([] if _candidates(b) else list(_inflated(b))):
        for pkt in _candidates(blob):
            root = _parse(pkt)
            if root is not None:
                return _props(root)
    return None


def _alt(v):
    if isinstance(v, tuple) and v and v[0] == "alt":
        items = v[1]
        for lang, x in items:
            if lang == "x-default":
                return x
        return items[0][1] if items else None
    return v


def _plain(v):
    v = _alt(v)
    if isinstance(v, list):
        return [_plain(x) for x in v]
    return v


def field_value(props, f):
    """The raw value of base field `f` from a packet's props ("none" when absent)."""
    if props is None:
        return False if f == "present" else "none"
    if f == "present":
        return True
    if f == "toolkit":
        return props.get(("x", "xmptk")) or "none"
    hist = props.get((_MM, "History"))
    if f == "history_count":
        return len(hist) if isinstance(hist, list) else "none"
    if f in _HIST:
        if not isinstance(hist, list):
            return "none"
        vals = [e.get(_HIST[f]) for e in hist if isinstance(e, dict) and e.get(_HIST[f]) not in (None, "")]
        return vals if vals else "none"
    spec = _PROPS.get(f)
    if spec is None:
        return None
    v = props.get(spec[:2])
    if len(spec) == 3:
        v = v.get(spec[2]) if isinstance(v, dict) else None
    v = _alt(v)
    if v is None or v == "" or v == []:
        return "none"
    if f in _LISTS:
        return _plain(v) if isinstance(v, list) else [v]
    if isinstance(v, list):
        v = _plain(v)
        return v[0] if len(v) == 1 and isinstance(v[0], str) else v
    return v if isinstance(v, str) else None


def _base(field):
    f = field or ""
    if f.startswith("xmp_") and f[4:] in _BASE + list(_ALIAS):
        f = f[4:]
    return _ALIAS.get(f, f)


def xmp_value(data, ctx):
    """<fmt>.(xmp_)<field>: the XMP property (see the module docstring)."""
    if data is None:
        return None
    try:
        f = _base(ctx.get("field"))
        if ctx.get("fmt") == "pdf" and f == "producer":
            f = "pdf_producer"
        return field_value(packet_props(data), f)
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None


def _lineage_key(props, field):
    if props is None:
        return None
    did = field_value(props, "document_id")
    odid = field_value(props, "original_document_id")
    if "original" in field:
        return odid
    if "lineage" in field:
        for k in (odid, field_value(props, "derived_from_original_document_id"),
                  field_value(props, "derived_from_document_id"), did):
            if isinstance(k, str) and k != "none":
                return k
        return "none"
    return did


def xmp_groups(data, ctx):
    """synthesis.<document_id / original_document_id / lineage>_groups over the container's members."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        field = ctx.get("field") or ""
        groups = {}
        for n in names:
            try:
                b = read(n)
            except Exception:  # noqa: BLE001
                b = None
            if not b:
                continue
            k = _lineage_key(packet_props(b), field)
            if isinstance(k, str) and k != "none":
                groups.setdefault(k, []).append(n)
        if not groups:
            return "none" if from_zip else None
        return {k: sorted(v) for k, v in sorted(groups.items())}
    except Exception:  # noqa: BLE001
        return None
