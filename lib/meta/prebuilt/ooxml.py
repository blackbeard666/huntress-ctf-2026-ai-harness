"""OOXML (.docx/.xlsx/.pptx and macro/template siblings) package properties (prebuilt, SPECULATIVE -- never GM-asked).

An OOXML file is an OPC zip package (ECMA-376 Part 2). Parts read here:
  core.xml  (core-properties, usually docProps/core.xml; located through _rels/.rels relationship type
             ".../metadata/core-properties", falling back to the conventional name): dc:creator, cp:lastModifiedBy,
             dcterms:created, dcterms:modified, dc:title, dc:subject, dc:description, cp:keywords, cp:category,
             cp:revision, cp:lastPrinted, cp:contentStatus, dc:language, dc:identifier, cp:version.
  app.xml   (extended-properties, usually docProps/app.xml): Application, AppVersion, Company, Manager, Template,
             TotalTime, Pages, Words, Characters, Lines, Paragraphs, Slides, Notes, DocSecurity, HyperlinkBase, ...
  [Content_Types].xml: content_types_count = number of <Default> + <Override> entries (every content-type mapping,
             stored order irrelevant); *_default_count / *_override_count split it.
Values are the element text exactly as stored (trimmed). Timestamps: dcterms:created/modified are W3CDTF TEXT in the
part (Office writes "YYYY-MM-DDTHH:MM:SSZ", already ISO-8601 UTC) -> returned verbatim, no epoch conversion (exiftool
reformats them as "YYYY:MM:DD HH:MM:SSZ"; the stored form is the natural ISO spelling). app.xml numbers stay as stored.
Not a zip / no [Content_Types].xml (not an OPC package) -> "none"; element absent or empty -> "none".

Package-structure siblings of the GM-verified D15 ooxml.external_relationship_targets (same walk: EVERY *.rels part):
  custom_properties   docProps/custom.xml (custom-properties rel, else the conventional name): {name: value} as
                      compact JSON, keys SORTED (D15 law for gathered sets); the value is the vt:* child's stored
                      TEXT ("42", "true", "2026-10-01T00:00:00Z" -- no retyping). custom_property_names = sorted
                      names, custom_property_count = int, custom_property_<name> = one value (name matched
                      case-insensitively, non-alphanumerics folded to "_").
  attached_template_target   Target of the .../relationships/attachedTemplate relationship (word/_rels/
                      settings.xml.rels; remote-template injection points it at an http(s)/UNC URL), verbatim.
  internal_relationship_targets   every Relationship WITHOUT TargetMode="External", sorted (duplicates kept).
  relationship_types  distinct Type URIs across all rels parts, sorted.
  hyperlink_count     relationships whose Type ends "/hyperlink" (internal or external), int.
  embedded_object_names   zip members under an "embeddings/" folder (full part names, sorted).
  main_part_content_type  content type of the package officeDocument relationship target from [Content_Types].xml
                      (Override by PartName, else Default by extension), verbatim.
Absent part / relationship -> "none"; empty gathered set -> "[]" (a count -> 0)."""
import io
import re
import zipfile
import xml.etree.ElementTree as ET

_CORE = {"creator": "creator", "last_modified_by": "lastModifiedBy", "created": "created", "modified": "modified",
         "title": "title", "subject": "subject", "description": "description", "keywords": "keywords",
         "category": "category", "revision": "revision", "last_printed": "lastPrinted",
         "content_status": "contentStatus", "language": "language", "identifier": "identifier", "version": "version"}
_CORE_ALIAS = {"author": "creator", "last_saved_by": "last_modified_by", "last_author": "last_modified_by",
               "create_date": "created", "created_time": "created", "creation_time": "created",
               "modify_date": "modified", "modified_time": "modified", "last_modified": "modified",
               "comments": "description"}
_APP = {"application": "Application", "app_version": "AppVersion", "company": "Company", "manager": "Manager",
        "template": "Template", "total_time": "TotalTime", "pages": "Pages", "words": "Words",
        "characters": "Characters", "characters_with_spaces": "CharactersWithSpaces", "lines": "Lines",
        "paragraphs": "Paragraphs", "slides": "Slides", "notes": "Notes", "hidden_slides": "HiddenSlides",
        "doc_security": "DocSecurity", "hyperlink_base": "HyperlinkBase", "presentation_format": "PresentationFormat"}

FIELDS = {
    ("ooxml", "core_creator"): "core_value",
    ("ooxml", "creator"): "core_value",
    ("ooxml", "core_author"): "core_value",
    ("ooxml", "core_last_modified_by"): "core_value",
    ("ooxml", "last_modified_by"): "core_value",
    ("ooxml", "core_last_saved_by"): "core_value",
    ("ooxml", "core_created"): "core_value",
    ("ooxml", "created"): "core_value",
    ("ooxml", "core_created_utc"): "core_value",
    ("ooxml", "core_modified"): "core_value",
    ("ooxml", "modified"): "core_value",
    ("ooxml", "core_modified_utc"): "core_value",
    ("ooxml", "core_title"): "core_value",
    ("ooxml", "title"): "core_value",
    ("ooxml", "core_subject"): "core_value",
    ("ooxml", "core_description"): "core_value",
    ("ooxml", "core_keywords"): "core_value",
    ("ooxml", "core_category"): "core_value",
    ("ooxml", "core_revision"): "core_value",
    ("ooxml", "core_last_printed"): "core_value",
    ("ooxml", "core_content_status"): "core_value",
    ("ooxml", "core_language"): "core_value",
    ("ooxml", "core_identifier"): "core_value",
    ("ooxml", "core_version"): "core_value",
    ("ooxml", "app_application"): "app_value",
    ("ooxml", "application"): "app_value",
    ("ooxml", "app_app_version"): "app_value",
    ("ooxml", "app_version"): "app_value",
    ("ooxml", "app_company"): "app_value",
    ("ooxml", "company"): "app_value",
    ("ooxml", "app_manager"): "app_value",
    ("ooxml", "app_template"): "app_value",
    ("ooxml", "app_total_time"): "app_value",
    ("ooxml", "app_pages"): "app_value",
    ("ooxml", "app_words"): "app_value",
    ("ooxml", "app_characters"): "app_value",
    ("ooxml", "app_lines"): "app_value",
    ("ooxml", "app_paragraphs"): "app_value",
    ("ooxml", "app_slides"): "app_value",
    ("ooxml", "app_notes"): "app_value",
    ("ooxml", "app_doc_security"): "app_value",
    ("ooxml", "app_hyperlink_base"): "app_value",
    ("ooxml", "content_types_count"): "content_types",
    ("ooxml", "content_types_entry_count"): "content_types",
    ("ooxml", "content_types_default_count"): "content_types",
    ("ooxml", "content_types_override_count"): "content_types",
    ("ooxml", "custom_properties"): "custom_properties",
    ("ooxml", "custom_props"): "custom_properties",
    ("ooxml", "custom_document_properties"): "custom_properties",
    ("ooxml", "custom_property_names"): "custom_properties",
    ("ooxml", "custom_property_count"): "custom_properties",
    ("ooxml", "custom_properties_count"): "custom_properties",
    ("ooxml", "custom_property_*"): "custom_properties",
    ("ooxml", "attached_template_target"): "attached_template_target",
    ("ooxml", "attached_template"): "attached_template_target",
    ("ooxml", "attached_template_url"): "attached_template_target",
    ("ooxml", "remote_template_target"): "attached_template_target",
    ("ooxml", "template_target"): "attached_template_target",
    ("ooxml", "internal_relationship_targets"): "relationships",
    ("ooxml", "internal_relationship_count"): "relationships",
    ("ooxml", "external_relationship_count"): "relationships",
    ("ooxml", "relationship_count"): "relationships",
    ("ooxml", "relationship_types"): "relationships",
    ("ooxml", "hyperlink_count"): "relationships",
    ("ooxml", "hyperlink_relationship_count"): "relationships",
    ("ooxml", "embedded_object_names"): "embedded_objects",
    ("ooxml", "embedding_names"): "embedded_objects",
    ("ooxml", "embedded_part_names"): "embedded_objects",
    ("ooxml", "embedded_object_count"): "embedded_objects",
    ("ooxml", "embedding_count"): "embedded_objects",
    ("ooxml", "main_part_content_type"): "main_part_content_type",
    ("ooxml", "main_document_content_type"): "main_part_content_type",
    ("ooxml", "office_document_content_type"): "main_part_content_type",
    ("ooxml", "main_part_name"): "main_part_content_type",
}

_REL_CORE = re.compile(r"/metadata/core-properties$")
_REL_APP = re.compile(r"/officeDocument/2006/relationships/extended-properties$")
_REL_CUSTOM = re.compile(r"/officeDocument/2006/relationships/custom-properties$")
_REL_MAIN = re.compile(r"/relationships/officeDocument$")
_MAX_PART = 4 << 20


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _package(b):
    """(ZipFile, {lowercased name: real name}) of an OPC package, or None (not a zip / no [Content_Types].xml)."""
    if not b or bytes(b[:2]) != b"PK":
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(bytes(b)))
        names = {n.lower(): n for n in z.namelist()}
    except Exception:  # noqa: BLE001
        return None
    if "[content_types].xml" not in names:
        return None
    return z, names


def _xml(pkg, name):
    z, names = pkg
    real = names.get(name.lstrip("/").lower())
    if real is None:
        return None
    try:
        info = z.getinfo(real)
        if info.file_size > _MAX_PART:
            return None
        raw = z.read(real)
        if b"<!ENTITY" in raw:      # no DTD expansion games
            return None
        return ET.fromstring(raw)
    except Exception:  # noqa: BLE001
        return None


def _part_by_rel(pkg, rx, default):
    """Target of the package-level relationship whose Type matches rx (else the conventional part name)."""
    rels = _xml(pkg, "_rels/.rels")
    if rels is not None:
        for r in rels.iter():
            if _local(r.tag) == "Relationship" and rx.search(r.get("Type") or "") and r.get("Target"):
                t = r.get("Target").lstrip("/")
                if t.lower() in pkg[1]:
                    return t
    return default


def _child_text(root, local):
    if root is None:
        return "none"
    for el in root:
        if _local(el.tag) == local:
            v = "".join(el.itertext()).strip()
            return v if v else "none"
    return "none"


def _base(field, prefix):
    f = re.sub(r"_utc$", "", field or "")
    return f[len(prefix):] if f.startswith(prefix) else f


def core_value(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        k = _base(ctx.get("field"), "core_")
        k = _CORE_ALIAS.get(k, k)
        if k not in _CORE:
            return None
        root = _xml(pkg, _part_by_rel(pkg, _REL_CORE, "docProps/core.xml"))
        return _child_text(root, _CORE[k])
    except Exception:  # noqa: BLE001
        return None


def app_value(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        k = _base(ctx.get("field"), "app_")
        if k not in _APP:
            return None
        root = _xml(pkg, _part_by_rel(pkg, _REL_APP, "docProps/app.xml"))
        return _child_text(root, _APP[k])
    except Exception:  # noqa: BLE001
        return None


def content_types(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        root = _xml(pkg, "[Content_Types].xml")
        if root is None:
            return None
        tags = [_local(el.tag) for el in root]
        field = ctx.get("field") or ""
        if field.endswith("_default_count"):
            return tags.count("Default")
        if field.endswith("_override_count"):
            return tags.count("Override")
        return tags.count("Default") + tags.count("Override")
    except Exception:  # noqa: BLE001
        return None


def _rels(pkg):
    """[(rels part name, Relationship element)] over every *.rels part, zip order."""
    z, _names = pkg
    out = []
    for n in z.namelist():
        if n.lower().endswith(".rels"):
            root = _xml(pkg, n)
            if root is not None:
                out += [(n, el) for el in root.iter() if _local(el.tag) == "Relationship"]
    return out


def _fold(s):
    return re.sub(r"[^0-9a-z]+", "_", (s or "").lower()).strip("_")


def custom_properties(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        field = ctx.get("field") or ""
        root = _xml(pkg, _part_by_rel(pkg, _REL_CUSTOM, "docProps/custom.xml"))
        props = {}
        if root is not None:
            for el in root:
                if _local(el.tag) == "property" and el.get("name") is not None:
                    v = next(iter(el), None)
                    props.setdefault(el.get("name"), "".join(v.itertext()).strip() if v is not None else "")
        if field.endswith("_count"):
            return len(props) if root is not None else "none"
        if field == "custom_property_names":
            return sorted(props) if root is not None else "none"
        if ctx.get("param") is not None:
            want = _fold(ctx.get("param"))
            hit = [v for k, v in props.items() if _fold(k) == want]
            return (hit[0] or "none") if hit else "none"
        if root is None:
            return "none"
        return {k: props[k] for k in sorted(props)}
    except Exception:  # noqa: BLE001
        return None


def attached_template_target(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        for _n, el in _rels(pkg):
            if (el.get("Type") or "").endswith("/attachedTemplate") and el.get("Target"):
                return el.get("Target").strip()
        return "none"
    except Exception:  # noqa: BLE001
        return None


def relationships(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        rels = [el for _n, el in _rels(pkg)]
        ext = [el for el in rels if (el.get("TargetMode") or "").lower() == "external"]
        internal = [el for el in rels if (el.get("TargetMode") or "").lower() != "external"]
        field = ctx.get("field") or ""
        if field == "internal_relationship_targets":
            return sorted(el.get("Target") or "" for el in internal)
        if field == "internal_relationship_count":
            return len(internal)
        if field == "external_relationship_count":
            return len(ext)
        if field == "relationship_count":
            return len(rels)
        if field == "relationship_types":
            return sorted({el.get("Type") or "" for el in rels} - {""})
        if field.startswith("hyperlink"):
            return sum(1 for el in rels if (el.get("Type") or "").endswith("/hyperlink"))
        return None
    except Exception:  # noqa: BLE001
        return None


def embedded_objects(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        names = sorted(n for n in pkg[0].namelist() if n.lower().split("/")[-2:-1] == ["embeddings"])
        return len(names) if (ctx.get("field") or "").endswith("_count") else names
    except Exception:  # noqa: BLE001
        return None


def main_part_content_type(data, ctx):
    if data is None:
        return None
    try:
        pkg = _package(data)
        if pkg is None:
            return "none"
        part = None
        rels = _xml(pkg, "_rels/.rels")
        if rels is not None:
            for r in rels.iter():
                if _local(r.tag) == "Relationship" and _REL_MAIN.search(r.get("Type") or "") and r.get("Target"):
                    part = "/" + r.get("Target").strip().lstrip("/")
                    break
        if part is None:
            return "none"
        if (ctx.get("field") or "") == "main_part_name":
            return part
        ct = _xml(pkg, "[Content_Types].xml")
        if ct is None:
            return None
        default = None
        ext = part.rsplit(".", 1)[-1].lower() if "." in part.rsplit("/", 1)[-1] else None
        for el in ct:
            if _local(el.tag) == "Override" and (el.get("PartName") or "").lower() == part.lower():
                return el.get("ContentType") or "none"
            if _local(el.tag) == "Default" and ext and (el.get("Extension") or "").lower() == ext:
                default = el.get("ContentType")
        return default or "none"
    except Exception:  # noqa: BLE001
        return None
