"""ClickOnce manifest fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Deployment manifest (`.application`) and application manifest (`.exe.manifest`): XML, root `assembly` in
urn:schemas-microsoft-com:asm.v1, children in asm.v1/asm.v2 (prefixes vary: `asmv1:`, default ns, none). Matched
by LOCAL name, attributes too (`asmv2:publisher` -> publisher). assembly_identity_* = the root's direct
<assemblyIdentity> (not the entryPoint / dependency identities). entry_point_* = <entryPoint><commandLine file=
parameters=> (application manifest only). deployment_provider_codebase = <deployment><deploymentProvider codebase=>
(deployment manifest only). Values verbatim (trimmed); an absent element / attribute, or an empty one
(`parameters=""` is what Microsoft's ManifestWriter emits for no arguments) -> "none". Not XML / root is not an
asm.v1 `assembly` -> "none". A plain Win32 side-by-side manifest IS asm.v1 but has no entryPoint/deployment -> those
fields "none". DOCTYPE/ENTITY declarations are refused (untrusted XML)."""
import re
import xml.etree.ElementTree as ET

FIELDS = {
    ("clickonce", "entry_point_command_file"): "clickonce_value",
    ("clickonce", "entry_point_file"): "clickonce_value",
    ("clickonce", "entry_point"): "clickonce_value",
    ("clickonce", "command_line_file"): "clickonce_value",
    ("clickonce", "entry_point_command_line_file"): "clickonce_value",
    ("clickonce", "entry_point_parameters"): "clickonce_value",
    ("clickonce", "entry_point_command_parameters"): "clickonce_value",
    ("clickonce", "entry_point_command_line_parameters"): "clickonce_value",
    ("clickonce", "command_line_parameters"): "clickonce_value",
    ("clickonce", "entry_point_assembly_name"): "clickonce_value",
    ("clickonce", "entry_point_assembly_identity_name"): "clickonce_value",
    ("clickonce", "entry_point_assembly_version"): "clickonce_value",
    ("clickonce", "entry_point_assembly_identity_version"): "clickonce_value",
    ("clickonce", "assembly_identity_name"): "clickonce_value",
    ("clickonce", "assembly_identity_version"): "clickonce_value",
    ("clickonce", "assembly_identity_public_key_token"): "clickonce_value",
    ("clickonce", "assembly_identity_processor_architecture"): "clickonce_value",
    ("clickonce", "assembly_identity_language"): "clickonce_value",
    ("clickonce", "assembly_identity_type"): "clickonce_value",
    ("clickonce", "assembly_name"): "clickonce_value",
    ("clickonce", "assembly_version"): "clickonce_value",
    ("clickonce", "public_key_token"): "clickonce_value",
    ("clickonce", "processor_architecture"): "clickonce_value",
    ("clickonce", "deployment_provider_codebase"): "clickonce_value",
    ("clickonce", "deployment_provider_url"): "clickonce_value",
    ("clickonce", "deployment_url"): "clickonce_value",
    ("clickonce", "deployment_install"): "clickonce_value",
    ("clickonce", "deployment_map_file_extensions"): "clickonce_value",
    ("clickonce", "deployment_minimum_required_version"): "clickonce_value",
    ("clickonce", "deployment_trust_url_parameters"): "clickonce_value",
    ("clickonce", "description_publisher"): "clickonce_value",
    ("clickonce", "description_product"): "clickonce_value",
    ("clickonce", "publisher"): "clickonce_value",
    ("clickonce", "product"): "clickonce_value",
    ("clickonce", "description"): "clickonce_value",
    ("clickonce", "manifest_version"): "clickonce_value",
    ("clickonce", "manifest_type"): "clickonce_value",
    ("clickonce", "dependent_assembly_codebase"): "clickonce_value",
    ("clickonce", "dependent_assembly_codebases"): "clickonce_value",
    ("clickonce", "dependency_codebases"): "clickonce_value",
    ("clickonce", "dependent_assembly_names"): "clickonce_value",
    ("clickonce", "file_names"): "clickonce_value",
    ("clickonce", "compatible_framework_target_version"): "clickonce_value",
    ("clickonce", "compatible_framework_supported_runtime"): "clickonce_value",
    ("clickonce", "has_signature"): "clickonce_value",
    ("clickonce", "is_signed"): "clickonce_value",
    ("clickonce", "signature_present"): "clickonce_value",
    ("clickonce", "publisher_identity_name"): "clickonce_value",
}

_ASM_V1 = "urn:schemas-microsoft-com:asm.v1"
_ID_ATTR = {"name": "name", "version": "version", "public_key_token": "publicKeyToken",
            "processor_architecture": "processorArchitecture", "language": "language", "type": "type"}


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _attrs(el):
    return {_local(k): v for k, v in el.attrib.items()} if el is not None else {}


def _kids(el, name):
    return [c for c in el if _local(c.tag) == name] if el is not None else []


def _kid(el, name):
    k = _kids(el, name)
    return k[0] if k else None


def _first(root, name):
    for el in root.iter():
        if _local(el.tag) == name:
            return el
    return None


def manifest_root(b):
    """The root <assembly> element of a ClickOnce / SxS manifest, or None."""
    head = bytes(b[:4096])
    if re.search(rb"<!(?:\x00)?D(?:\x00)?O(?:\x00)?C(?:\x00)?T(?:\x00)?Y(?:\x00)?P(?:\x00)?E|<!ENTITY", head):
        return None
    try:
        root = ET.fromstring(bytes(b))
    except (ET.ParseError, ValueError):
        return None
    if _local(root.tag) != "assembly" or not root.tag.startswith("{" + _ASM_V1):
        return None
    return root


def _v(s):
    s = (s or "").strip()
    return s if s else "none"


def clickonce_value(data, ctx):
    if data is None:
        return None
    try:
        root = manifest_root(data)
        if root is None:
            return "none"
        field = ctx.get("field") or ""
        ep = _kid(root, "entryPoint")
        cl = _attrs(_kid(ep, "commandLine"))
        if field in ("entry_point_command_file", "entry_point_file", "entry_point", "command_line_file",
                     "entry_point_command_line_file"):
            return _v(cl.get("file"))
        if field in ("entry_point_parameters", "entry_point_command_parameters",
                     "entry_point_command_line_parameters", "command_line_parameters"):
            return _v(cl.get("parameters"))
        if field.startswith("entry_point_assembly_"):
            key = "version" if field.endswith("version") else "name"
            return _v(_attrs(_kid(ep, "assemblyIdentity")).get(key))
        ident = _attrs(_kid(root, "assemblyIdentity"))
        if field.startswith("assembly_identity_"):
            attr = _ID_ATTR.get(field[len("assembly_identity_"):])
            return _v(ident.get(attr)) if attr else None
        if field in ("assembly_name", "assembly_version", "public_key_token", "processor_architecture"):
            return _v(ident.get(_ID_ATTR[field.replace("assembly_", "")]))
        dep = _kid(root, "deployment")
        if field in ("deployment_provider_codebase", "deployment_provider_url", "deployment_url"):
            return _v(_attrs(_kid(dep, "deploymentProvider")).get("codebase"))
        if field.startswith("deployment_"):
            attr = {"install": "install", "map_file_extensions": "mapFileExtensions",
                    "minimum_required_version": "minimumRequiredVersion",
                    "trust_url_parameters": "trustURLParameters"}.get(field[len("deployment_"):])
            return _v(_attrs(dep).get(attr)) if attr else None
        desc = _kid(root, "description")
        if field in ("description_publisher", "publisher"):
            return _v(_attrs(desc).get("publisher"))
        if field in ("description_product", "product"):
            return _v(_attrs(desc).get("product"))
        if field == "description":
            return _v(desc.text if desc is not None else None)
        if field == "manifest_version":
            return _v(_attrs(root).get("manifestVersion"))
        if field == "manifest_type":
            return "deployment" if dep is not None else "application" if ep is not None else "none"
        das = [d for dp in _kids(root, "dependency") for d in _kids(dp, "dependentAssembly")]
        if field in ("dependent_assembly_codebases", "dependency_codebases", "dependent_assembly_codebase"):
            cbs = [_attrs(d)["codebase"] for d in das if _attrs(d).get("codebase")]
            if field == "dependent_assembly_codebase":
                return cbs[0] if cbs else "none"
            return cbs if cbs else "none"
        if field == "dependent_assembly_names":
            names = [_attrs(_kid(d, "assemblyIdentity")).get("name") for d in das]
            names = [n for n in names if n]
            return names if names else "none"
        if field == "file_names":
            names = [_attrs(f).get("name") for f in _kids(root, "file") if _attrs(f).get("name")]
            return names if names else "none"
        if field.startswith("compatible_framework_"):
            fw = _first(root, "framework")
            attr = "targetVersion" if field.endswith("target_version") else "supportedRuntime"
            return _v(_attrs(fw).get(attr))
        if field in ("has_signature", "is_signed", "signature_present"):
            return any(_local(el.tag) == "Signature" for el in root.iter())
        if field == "publisher_identity_name":
            return _v(_attrs(_first(root, "publisherIdentity")).get("name"))
        return None
    except Exception:  # noqa: BLE001
        return None
