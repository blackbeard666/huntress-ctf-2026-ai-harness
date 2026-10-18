"""Windows Library (.library-ms) and Search Connector (.searchConnector-ms) fields (prebuilt, SPECULATIVE).

.library-ms: <libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library"> with name, ownerSID,
version, isLibraryPinned, iconReference, templateInfo/folderType, searchConnectorDescriptionList/
searchConnectorDescription[] (isDefaultSaveLocation, simpleLocation/url, simpleLocation/serialized).
.searchConnector-ms: root <searchConnectorDescription xmlns=".../2009/searchConnector"> with description,
isSearchOnlyItem, includeInStartMenuScope, iconReference, templateInfo/folderType, simpleLocation/url.
Phishing use: simpleLocation/url = \\\\attacker\\share or https://host/webdav (WebDAV/NTLM lure).
Elements matched by LOCAL name (any namespace / prefix). Values: element text verbatim, whitespace-trimmed
(folderType GUID keeps its stored braces/case -> plain string, not re-spelled). location_urls = every simpleLocation/url
in document order (JSON list); location_url = the first. Booleans (is_library_pinned, is_default_save_location,
is_search_only_item, include_in_start_menu_scope): "true"/"1" -> true, "false"/"0" -> false; absent -> "none".
version = <version> element text (the library's change counter), not the XML declaration version.
Not a libraryDescription / searchConnectorDescription document -> "none"; DOCTYPE/ENTITY -> None (never expanded);
malformed XML -> None. Fmt spellings library_ms / library / searchconnector."""
import re
import xml.etree.ElementTree as ET

_CORE = ("location_urls", "location_url", "is_library_pinned", "folder_type", "owner_sid", "version")
_ALL = _CORE + ("simple_location_urls", "simple_location_url", "url", "urls", "location_count", "name",
                "library_name", "description", "icon_reference", "is_default_save_location", "is_search_only_item",
                "include_in_start_menu_scope", "template_folder_type", "library_pinned",
                "search_connector_count", "root_element")

FIELDS = {
    ("library_ms", "location_urls"): "library_value",
    ("library_ms", "location_url"): "library_value",
    ("library_ms", "is_library_pinned"): "library_value",
    ("library_ms", "folder_type"): "library_value",
    ("library_ms", "owner_sid"): "library_value",
    ("library_ms", "version"): "library_value",
    ("library_ms", "simple_location_urls"): "library_value",
    ("library_ms", "simple_location_url"): "library_value",
    ("library_ms", "url"): "library_value",
    ("library_ms", "urls"): "library_value",
    ("library_ms", "location_count"): "library_value",
    ("library_ms", "name"): "library_value",
    ("library_ms", "library_name"): "library_value",
    ("library_ms", "description"): "library_value",
    ("library_ms", "icon_reference"): "library_value",
    ("library_ms", "is_default_save_location"): "library_value",
    ("library_ms", "is_search_only_item"): "library_value",
    ("library_ms", "include_in_start_menu_scope"): "library_value",
    ("library_ms", "template_folder_type"): "library_value",
    ("library_ms", "library_pinned"): "library_value",
    ("library_ms", "search_connector_count"): "library_value",
    ("library_ms", "root_element"): "library_value",
    ("library", "location_urls"): "library_value",
    ("library", "location_url"): "library_value",
    ("library", "is_library_pinned"): "library_value",
    ("library", "folder_type"): "library_value",
    ("library", "owner_sid"): "library_value",
    ("library", "version"): "library_value",
    ("library", "simple_location_urls"): "library_value",
    ("library", "url"): "library_value",
    ("library", "urls"): "library_value",
    ("library", "location_count"): "library_value",
    ("library", "name"): "library_value",
    ("library", "icon_reference"): "library_value",
    ("library", "is_default_save_location"): "library_value",
    ("library", "search_connector_count"): "library_value",
    ("searchconnector", "location_urls"): "library_value",
    ("searchconnector", "location_url"): "library_value",
    ("searchconnector", "simple_location_url"): "library_value",
    ("searchconnector", "url"): "library_value",
    ("searchconnector", "folder_type"): "library_value",
    ("searchconnector", "description"): "library_value",
    ("searchconnector", "icon_reference"): "library_value",
    ("searchconnector", "is_search_only_item"): "library_value",
    ("searchconnector", "include_in_start_menu_scope"): "library_value",
}

_ALIASES = {"simple_location_urls": "location_urls", "urls": "location_urls", "simple_location_url": "location_url",
            "url": "location_url", "library_name": "name", "template_folder_type": "folder_type",
            "library_pinned": "is_library_pinned"}
_TEXT = {"owner_sid": "ownerSID", "version": "version", "name": "name", "description": "description",
         "icon_reference": "iconReference"}
_BOOL = {"is_library_pinned": "isLibraryPinned", "is_default_save_location": "isDefaultSaveLocation",
         "is_search_only_item": "isSearchOnlyItem", "include_in_start_menu_scope": "includeInStartMenuScope"}
_ROOTS = ("libraryDescription", "searchConnectorDescription")


def _decode(b):
    if b[:2] == b"\xff\xfe":
        return b[2:].decode("utf-16-le", "replace")
    if b[:2] == b"\xfe\xff":
        return b[2:].decode("utf-16-be", "replace")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8", "replace")
    if len(b) >= 4 and b[1] == 0 and b[3] == 0 and b[0] != 0:
        return b.decode("utf-16-le", "replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def _ln(tag):
    return tag.rsplit("}", 1)[-1].rsplit(":", 1)[-1] if isinstance(tag, str) else ""


def _kids(el, name=None):
    return [c for c in list(el) if isinstance(c.tag, str) and (name is None or _ln(c.tag) == name)]


def _txt(el):
    if el is None or el.text is None:
        return None
    return el.text.strip() or None


def _connectors(root):
    """The searchConnectorDescription elements: the root itself (.searchConnector-ms) or the library's list."""
    if _ln(root.tag) == "searchConnectorDescription":
        return [root]
    return [c for lst in _kids(root, "searchConnectorDescriptionList") for c in _kids(lst, "searchConnectorDescription")]


def _from_tree(root, key):
    conns = _connectors(root)
    if key in ("location_urls", "location_url", "location_count"):
        urls = [u for c in conns for loc in _kids(c, "simpleLocation") for u in (_txt(x) for x in _kids(loc, "url"))
                if u is not None]
        if key == "location_count":
            return len(urls)
        return (urls or None) if key == "location_urls" else (urls[0] if urls else None)
    if key == "search_connector_count":
        return len(conns)
    if key == "root_element":
        return _ln(root.tag)
    if key == "folder_type":
        t = _kids(root, "templateInfo")
        return _txt(_kids(t[0], "folderType")[0]) if t and _kids(t[0], "folderType") else None
    if key in _TEXT:
        k = _kids(root, _TEXT[key])
        return _txt(k[0]) if k else None
    if key in _BOOL:
        name = _BOOL[key]
        k = _kids(root, name) or [e for c in conns for e in _kids(c, name)]
        s = (_txt(k[0]) or "").lower() if k else ""
        return True if s in ("true", "1") else False if s in ("false", "0") else None
    return None


def library_value(data, ctx):
    """library_ms.<field>: a value of a .library-ms / .searchConnector-ms ("none" = absent, None = cannot answer)."""
    try:
        if not data:
            return None if data is None else "none"
        field = ctx.get("field") or ""
        key = _ALIASES.get(field, field)
        if key not in _ALL:
            return None
        text = _decode(bytes(data[:4 << 20])).lstrip("﻿\x00 \t\r\n")
        if re.search(r"<!(?:DOCTYPE|ENTITY)", text, re.I):
            return None
        if not text.startswith("<"):
            return "none"
        body = re.sub(r"^<\?xml[^>]*\?>", "", text).strip()
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return "none" if not re.search(r"<(?:[\w.-]+:)?(?:%s)[\s>]" % "|".join(_ROOTS), body[:4096]) else None
        if _ln(root.tag) not in _ROOTS:
            return "none"
        v = _from_tree(root, key)
        return "none" if v is None else v
    except Exception:  # noqa: BLE001 -- bytes in, value out; never raise past the extractor
        return None
