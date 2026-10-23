"""Standalone iOS provisioning profiles, entitlements plists and app-extension (.appex) Info.plists (prebuilt,
SPECULATIVE -- never GM-asked). Companion of prebuilt ipa.py (which owns `mobileprovision.<most fields>` and
`ipa.provision_*`): this module only adds the keys ipa.py does not register (no duplicate keys), self-contained.

Format tokens:
  mobileprovision   extras: developer_certificate_sha1s/_sha256s/_subject_cns/_serial_numbers_hex, *_date_utc, signer
  provisioningprofile / provision   every profile field (GM fmt tokens match [a-z][a-z0-9]*, so no `provisioning_profile`)
  ipa / ios         provision_/mobileprovision_ developer_certificate_sha1s/_sha256s/_subject_cns, entitlement_count
  entitlements / entitlement   an .entitlements / .xcent plist (XML or bplist), or a profile's Entitlements dict
  appex             an app-extension Info.plist (NSExtension dict), or a zip/.ipa holding */PlugIns/*.appex/Info.plist

Profile layout: CMS SignedData DER (RFC 5652, signer "Apple iPhone OS Provisioning Profile Signing") whose eContent
is an XML plist stored contiguously, so `<?xml`..`</plist>` is sliced out and plistlib-parsed (no CMS walk needed).
DeveloperCertificates = array of <data> (base64 DER X.509): sha1s/sha256s = lowercase hex digest of each DER, stored
order (compact JSON list); subject_cns via cryptography. Dates: plist <date> is stored as ISO-8601 UTC
"YYYY-MM-DDTHH:MM:SSZ" -- rendered back in exactly that form. entitlement_keys: SORTED (the coverage target says
sorted; Xcode writes them sorted anyway). provisioned_devices: stored order. provisions_all_devices: absent -> false
(only enterprise profiles carry it). Absent key / wrong format -> "none"; no input -> None."""
import hashlib
import io
import json
import plistlib
import posixpath
import re
import zipfile

FIELDS = {
    ('provisioningprofile', 'team_identifier'): 'profile_value',
    ('provisioningprofile', 'team_id'): 'profile_value',
    ('provisioningprofile', 'team_identifiers'): 'profile_value',
    ('provisioningprofile', 'team_name'): 'profile_value',
    ('provisioningprofile', 'app_id_name'): 'profile_value',
    ('provisioningprofile', 'application_identifier'): 'profile_value',
    ('provisioningprofile', 'app_id'): 'profile_value',
    ('provisioningprofile', 'uuid'): 'profile_value',
    ('provisioningprofile', 'name'): 'profile_value',
    ('provisioningprofile', 'creation_date'): 'profile_value',
    ('provisioningprofile', 'creation_date_utc'): 'profile_value',
    ('provisioningprofile', 'expiration_date'): 'profile_value',
    ('provisioningprofile', 'expiration_date_utc'): 'profile_value',
    ('provisioningprofile', 'creation_utc'): 'profile_value',
    ('provisioningprofile', 'expiration_utc'): 'profile_value',
    ('provisioningprofile', 'platform'): 'profile_value',
    ('provisioningprofile', 'version'): 'profile_value',
    ('provisioningprofile', 'time_to_live'): 'profile_value',
    ('provisioningprofile', 'is_xcode_managed'): 'profile_value',
    ('provisioningprofile', 'provisions_all_devices'): 'profile_value',
    ('provisioningprofile', 'provisioned_device_count'): 'profile_value',
    ('provisioningprofile', 'device_count'): 'profile_value',
    ('provisioningprofile', 'provisioned_devices'): 'profile_value',
    ('provisioningprofile', 'entitlement_keys'): 'profile_value',
    ('provisioningprofile', 'entitlement_count'): 'profile_value',
    ('provisioningprofile', 'get_task_allow'): 'profile_value',
    ('provisioningprofile', 'aps_environment'): 'profile_value',
    ('provisioningprofile', 'keychain_access_groups'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_count'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_sha1s'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_sha256s'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_subject_cns'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_serial_numbers_hex'): 'profile_value',
    ('provisioningprofile', 'signer_common_name'): 'profile_value',
    ('provisioningprofile', 'is_expired_at_creation'): 'profile_value',
    ('provisioningprofile', 'developer_certificate_fingerprints_sha1'): 'profile_value',
    ('provisioningprofile', 'certificate_sha1s'): 'profile_value',
    ('provisioningprofile', 'signer_cn'): 'profile_value',
    ('provision', 'team_identifier'): 'profile_value',
    ('provision', 'team_id'): 'profile_value',
    ('provision', 'team_identifiers'): 'profile_value',
    ('provision', 'team_name'): 'profile_value',
    ('provision', 'app_id_name'): 'profile_value',
    ('provision', 'application_identifier'): 'profile_value',
    ('provision', 'app_id'): 'profile_value',
    ('provision', 'uuid'): 'profile_value',
    ('provision', 'name'): 'profile_value',
    ('provision', 'creation_date'): 'profile_value',
    ('provision', 'creation_date_utc'): 'profile_value',
    ('provision', 'expiration_date'): 'profile_value',
    ('provision', 'expiration_date_utc'): 'profile_value',
    ('provision', 'creation_utc'): 'profile_value',
    ('provision', 'expiration_utc'): 'profile_value',
    ('provision', 'platform'): 'profile_value',
    ('provision', 'version'): 'profile_value',
    ('provision', 'time_to_live'): 'profile_value',
    ('provision', 'is_xcode_managed'): 'profile_value',
    ('provision', 'provisions_all_devices'): 'profile_value',
    ('provision', 'provisioned_device_count'): 'profile_value',
    ('provision', 'device_count'): 'profile_value',
    ('provision', 'provisioned_devices'): 'profile_value',
    ('provision', 'entitlement_keys'): 'profile_value',
    ('provision', 'entitlement_count'): 'profile_value',
    ('provision', 'get_task_allow'): 'profile_value',
    ('provision', 'aps_environment'): 'profile_value',
    ('provision', 'keychain_access_groups'): 'profile_value',
    ('provision', 'developer_certificate_count'): 'profile_value',
    ('provision', 'developer_certificate_sha1s'): 'profile_value',
    ('provision', 'developer_certificate_sha256s'): 'profile_value',
    ('provision', 'developer_certificate_subject_cns'): 'profile_value',
    ('provision', 'developer_certificate_serial_numbers_hex'): 'profile_value',
    ('provision', 'signer_common_name'): 'profile_value',
    ('provision', 'is_expired_at_creation'): 'profile_value',
    ('provision', 'developer_certificate_fingerprints_sha1'): 'profile_value',
    ('provision', 'certificate_sha1s'): 'profile_value',
    ('provision', 'signer_cn'): 'profile_value',
    ('mobileprovision', 'creation_date_utc'): 'profile_value',
    ('mobileprovision', 'expiration_date_utc'): 'profile_value',
    ('mobileprovision', 'entitlement_count'): 'profile_value',
    ('mobileprovision', 'developer_certificate_sha1s'): 'profile_value',
    ('mobileprovision', 'developer_certificate_sha256s'): 'profile_value',
    ('mobileprovision', 'developer_certificate_subject_cns'): 'profile_value',
    ('mobileprovision', 'developer_certificate_serial_numbers_hex'): 'profile_value',
    ('mobileprovision', 'developer_certificate_fingerprints_sha1'): 'profile_value',
    ('mobileprovision', 'certificate_sha1s'): 'profile_value',
    ('mobileprovision', 'signer_common_name'): 'profile_value',
    ('mobileprovision', 'signer_cn'): 'profile_value',
    ('ipa', 'provision_developer_certificate_sha1s'): 'ipa_profile_value',
    ('ipa', 'provision_developer_certificate_sha256s'): 'ipa_profile_value',
    ('ipa', 'provision_developer_certificate_subject_cns'): 'ipa_profile_value',
    ('ipa', 'provision_entitlement_count'): 'ipa_profile_value',
    ('ipa', 'mobileprovision_developer_certificate_sha1s'): 'ipa_profile_value',
    ('ipa', 'mobileprovision_developer_certificate_sha256s'): 'ipa_profile_value',
    ('ipa', 'mobileprovision_developer_certificate_subject_cns'): 'ipa_profile_value',
    ('ipa', 'mobileprovision_entitlement_count'): 'ipa_profile_value',
    ('ios', 'provision_developer_certificate_sha1s'): 'ipa_profile_value',
    ('ios', 'provision_developer_certificate_sha256s'): 'ipa_profile_value',
    ('ios', 'provision_developer_certificate_subject_cns'): 'ipa_profile_value',
    ('ios', 'provision_entitlement_count'): 'ipa_profile_value',
    ('ios', 'mobileprovision_developer_certificate_sha1s'): 'ipa_profile_value',
    ('ios', 'mobileprovision_developer_certificate_sha256s'): 'ipa_profile_value',
    ('ios', 'mobileprovision_developer_certificate_subject_cns'): 'ipa_profile_value',
    ('ios', 'mobileprovision_entitlement_count'): 'ipa_profile_value',
    ('entitlements', 'entitlement_keys'): 'entitlements_value',
    ('entitlements', 'keys'): 'entitlements_value',
    ('entitlements', 'key_count'): 'entitlements_value',
    ('entitlements', 'entitlement_count'): 'entitlements_value',
    ('entitlements', 'application_identifier'): 'entitlements_value',
    ('entitlements', 'app_id'): 'entitlements_value',
    ('entitlements', 'team_identifier'): 'entitlements_value',
    ('entitlements', 'get_task_allow'): 'entitlements_value',
    ('entitlements', 'aps_environment'): 'entitlements_value',
    ('entitlements', 'keychain_access_groups'): 'entitlements_value',
    ('entitlements', 'application_groups'): 'entitlements_value',
    ('entitlements', 'app_groups'): 'entitlements_value',
    ('entitlements', 'associated_domains'): 'entitlements_value',
    ('entitlements', 'icloud_container_identifiers'): 'entitlements_value',
    ('entitlements', 'sandbox_enabled'): 'entitlements_value',
    ('entitlements', 'app_sandbox'): 'entitlements_value',
    ('entitlements', 'value_*'): 'entitlements_value',
    ('entitlement', 'entitlement_keys'): 'entitlements_value',
    ('entitlement', 'keys'): 'entitlements_value',
    ('entitlement', 'key_count'): 'entitlements_value',
    ('entitlement', 'entitlement_count'): 'entitlements_value',
    ('entitlement', 'application_identifier'): 'entitlements_value',
    ('entitlement', 'app_id'): 'entitlements_value',
    ('entitlement', 'team_identifier'): 'entitlements_value',
    ('entitlement', 'get_task_allow'): 'entitlements_value',
    ('entitlement', 'aps_environment'): 'entitlements_value',
    ('entitlement', 'keychain_access_groups'): 'entitlements_value',
    ('entitlement', 'application_groups'): 'entitlements_value',
    ('entitlement', 'app_groups'): 'entitlements_value',
    ('entitlement', 'associated_domains'): 'entitlements_value',
    ('entitlement', 'icloud_container_identifiers'): 'entitlements_value',
    ('entitlement', 'sandbox_enabled'): 'entitlements_value',
    ('entitlement', 'app_sandbox'): 'entitlements_value',
    ('entitlement', 'value_*'): 'entitlements_value',
    ('appex', 'ns_extension_point_identifier'): 'appex_value',
    ('appex', 'extension_point_identifier'): 'appex_value',
    ('appex', 'extension_point'): 'appex_value',
    ('appex', 'ns_extension_principal_class'): 'appex_value',
    ('appex', 'principal_class'): 'appex_value',
    ('appex', 'ns_extension_main_storyboard'): 'appex_value',
    ('appex', 'ns_extension_attribute_keys'): 'appex_value',
    ('appex', 'extension_attribute_keys'): 'appex_value',
    ('appex', 'bundle_identifier'): 'appex_value',
    ('appex', 'cf_bundle_identifier'): 'appex_value',
    ('appex', 'bundle_executable'): 'appex_value',
    ('appex', 'cf_bundle_executable'): 'appex_value',
    ('appex', 'bundle_package_type'): 'appex_value',
    ('appex', 'cf_bundle_package_type'): 'appex_value',
    ('appex', 'bundle_short_version_string'): 'appex_value',
    ('appex', 'cf_bundle_short_version_string'): 'appex_value',
    ('appex', 'bundle_version'): 'appex_value',
    ('appex', 'cf_bundle_version'): 'appex_value',
    ('appex', 'bundle_display_name'): 'appex_value',
    ('appex', 'cf_bundle_display_name'): 'appex_value',
    ('appex', 'minimum_os_version'): 'appex_value',
    ('appex', 'appex_path'): 'appex_value',
    ('appex', 'appex_count'): 'appex_value',
    ('appex', 'appex_names'): 'appex_value',
    ('appex', 'value_*'): 'appex_value',
}


_PL = re.compile(rb"<\?xml.*?</plist>", re.S)
_PROFILE_KEYS = ("TeamIdentifier", "ExpirationDate", "UUID", "Entitlements", "DeveloperCertificates")


def _plist(b):
    if not b:
        return None
    s = bytes(b).lstrip(b"\xef\xbb\xbf \t\r\n")
    if not (s.startswith(b"bplist00") or s.startswith(b"<?xml") or s.startswith(b"<plist")
            or s.startswith(b"<!DOCTYPE plist")):
        return None
    try:
        v = plistlib.loads(s)
    except Exception:
        return None
    return v if isinstance(v, dict) else None


def _profile(b):
    """The plist dict of a mobileprovision (CMS DER with an embedded XML plist) or a bare profile plist, or None."""
    if not b:
        return None
    b = bytes(b)
    pl = None
    if b[:1] == b"\x30":                       # DER SEQUENCE: slice the eContent plist
        m = _PL.search(b)
        pl = _plist(m.group(0)) if m else None
    if pl is None:
        pl = _plist(b)
    if pl is None or not any(k in pl for k in _PROFILE_KEYS):
        return None
    return pl


def _zip_members(b):
    if not b or b[:2] != b"PK":
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(bytes(b)))
        return z, z.namelist()
    except Exception:
        return None


def _zip_profile(b):
    """A profile from an .ipa / zip: the shallowest *.mobileprovision member."""
    zm = _zip_members(b)
    if not zm:
        return None
    z, names = zm
    cands = sorted((n for n in names if n.lower().endswith(".mobileprovision") and ".appex/" not in n),
                   key=lambda n: (n.count("/"), n))
    for n in cands:
        try:
            p = _profile(z.read(n))
        except Exception:
            p = None
        if p is not None:
            return p
    return None


def _date(v):
    import datetime
    if isinstance(v, datetime.datetime):
        if v.tzinfo is not None:
            v = v.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")
    return v


def _out(v):
    """Raw plist value -> spell-ready raw value ("none" when absent)."""
    if v is None:
        return "none"
    if isinstance(v, (bool, int, list, dict)):
        return json.loads(json.dumps(v, default=_date)) if isinstance(v, (list, dict)) else v
    if isinstance(v, bytes):
        return v.hex()
    v = _date(v)
    return str(v).strip()


def _certs(p):
    c = p.get("DeveloperCertificates")
    return [bytes(x) for x in c if isinstance(x, (bytes, bytearray))] if isinstance(c, list) else None


def _cert_attr(der, what):
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        c = x509.load_der_x509_certificate(der)
    except Exception:
        return None
    if what == "serial":
        return "%x" % c.serial_number
    a = c.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    return a[0].value if a else None


def _signer_cn(b):
    """The CMS signer certificate's subject CN (the first certificate in SignedData.certificates matching a SignerInfo
    issuer/serial, else the first leaf), or None."""
    try:
        from asn1crypto import cms
        ci = cms.ContentInfo.load(bytes(b))
        sd = ci["content"]
        certs = [c.chosen for c in sd["certificates"] if c.name == "certificate"]
        for si in sd["signer_infos"]:
            sid = si["sid"]
            if sid.name == "issuer_and_serial_number":
                for c in certs:
                    if (c.serial_number == sid.chosen["serial_number"].native
                            and c.issuer == sid.chosen["issuer"]):
                        return c.subject.native.get("common_name")
        return certs[0].subject.native.get("common_name") if certs else None
    except Exception:
        return None


def _ents(p):
    e = p.get("Entitlements")
    return e if isinstance(e, dict) else None


def _prov_field(p, f, raw):
    """One profile field (`f` without any provision_/mobileprovision_ prefix) of profile dict `p`."""
    ents = _ents(p)
    ent = lambda k: None if ents is None else ents.get(k)  # noqa: E731
    certs = _certs(p)
    f = re.sub(r"^(?:provision|mobileprovision|profile)_", "", f)
    simple = {"team_name": "TeamName", "app_id_name": "AppIDName", "uuid": "UUID", "name": "Name",
              "platform": "Platform", "version": "Version", "time_to_live": "TimeToLive",
              "is_xcode_managed": "IsXcodeManaged", "provisioned_devices": "ProvisionedDevices",
              "creation_date": "CreationDate", "creation_date_utc": "CreationDate", "creation_utc": "CreationDate",
              "expiration_date": "ExpirationDate", "expiration_date_utc": "ExpirationDate",
              "expiration_utc": "ExpirationDate"}
    if f in simple:
        return _out(p.get(simple[f]))
    if f in ("team_identifier", "team_id"):
        t = p.get("TeamIdentifier")
        return _out(t[0] if isinstance(t, list) and t else None)
    if f == "team_identifiers":
        return _out(p.get("TeamIdentifier"))
    if f in ("application_identifier", "app_id"):
        return _out(ent("application-identifier"))
    if f == "get_task_allow":
        return _out(ent("get-task-allow"))
    if f == "aps_environment":
        return _out(ent("aps-environment"))
    if f == "keychain_access_groups":
        return _out(ent("keychain-access-groups"))
    if f == "entitlement_keys":
        return "none" if ents is None else sorted(ents)
    if f == "entitlement_count":
        return "none" if ents is None else len(ents)
    if f == "provisions_all_devices":
        return bool(p.get("ProvisionsAllDevices", False))
    if f in ("provisioned_device_count", "device_count"):
        d = p.get("ProvisionedDevices")
        return len(d) if isinstance(d, list) else 0
    if f in ("developer_certificate_count",):
        return len(certs) if certs is not None else 0
    if f in ("developer_certificate_sha1s", "developer_certificate_fingerprints_sha1", "certificate_sha1s"):
        return "none" if not certs else [hashlib.sha1(c).hexdigest() for c in certs]
    if f == "developer_certificate_sha256s":
        return "none" if not certs else [hashlib.sha256(c).hexdigest() for c in certs]
    if f == "developer_certificate_subject_cns":
        return "none" if not certs else [_cert_attr(c, "cn") for c in certs]
    if f == "developer_certificate_serial_numbers_hex":
        return "none" if not certs else [_cert_attr(c, "serial") for c in certs]
    if f in ("signer_common_name", "signer_cn"):
        return _out(_signer_cn(raw) if raw[:1] == b"\x30" else None)
    if f == "is_expired_at_creation":
        c, e = p.get("CreationDate"), p.get("ExpirationDate")
        return "none" if c is None or e is None else bool(e <= c)
    return None


def profile_value(data, ctx):
    """mobileprovision / provisioningprofile / provision .<field> of a bare profile (or an .ipa holding one)."""
    if data is None:
        return None
    try:
        p = _profile(data) or _zip_profile(data)
        if p is None:
            return "none"
        return _prov_field(p, ctx.get("field") or "", bytes(data))
    except Exception:
        return None


def ipa_profile_value(data, ctx):
    """ipa.provision_<field>: the .ipa's embedded.mobileprovision (a bare profile is accepted too)."""
    if data is None:
        return None
    try:
        raw = bytes(data)
        p = _profile(raw)
        if p is None:
            zm = _zip_members(raw)
            if zm:
                z, names = zm
                for n in sorted((n for n in names if n.endswith("embedded.mobileprovision") and ".appex/" not in n),
                                key=lambda n: (n.count("/"), n)):
                    raw = z.read(n)
                    p = _profile(raw)
                    if p is not None:
                        break
        if p is None:
            return "none"
        return _prov_field(p, ctx.get("field") or "", raw)
    except Exception:
        return None


def _norm(k):
    return re.sub(r"[^a-z0-9]+", "_", str(k).lower()).strip("_")


_ENT = {"application_identifier": "application-identifier", "app_id": "application-identifier",
        "team_identifier": "com.apple.developer.team-identifier", "get_task_allow": "get-task-allow",
        "aps_environment": "aps-environment", "keychain_access_groups": "keychain-access-groups",
        "application_groups": "com.apple.security.application-groups",
        "app_groups": "com.apple.security.application-groups",
        "associated_domains": "com.apple.developer.associated-domains",
        "icloud_container_identifiers": "com.apple.developer.icloud-container-identifiers",
        "sandbox_enabled": "com.apple.security.app-sandbox", "app_sandbox": "com.apple.security.app-sandbox"}


def entitlements_value(data, ctx):
    """entitlements.<field> of an .entitlements/.xcent plist, or of a profile's Entitlements dict."""
    if data is None:
        return None
    try:
        p = _profile(data)
        ents = _ents(p) if p is not None else _plist(data)
        if ents is None:
            return "none"
        f = ctx.get("field") or ""
        if f in ("entitlement_keys", "keys"):
            return sorted(ents)
        if f in ("entitlement_count", "key_count"):
            return len(ents)
        if f in _ENT:
            if f in ("sandbox_enabled", "app_sandbox") and _ENT[f] not in ents:
                return "none"
            return _out(ents.get(_ENT[f]))
        param = ctx.get("param")
        if param:
            want = _norm(param)
            for k, v in ents.items():
                if _norm(k) == want:
                    return _out(v)
            return "none"
        return None
    except Exception:
        return None


_APX = {"bundle_identifier": "CFBundleIdentifier", "cf_bundle_identifier": "CFBundleIdentifier",
        "bundle_executable": "CFBundleExecutable", "cf_bundle_executable": "CFBundleExecutable",
        "bundle_package_type": "CFBundlePackageType", "cf_bundle_package_type": "CFBundlePackageType",
        "bundle_short_version_string": "CFBundleShortVersionString",
        "cf_bundle_short_version_string": "CFBundleShortVersionString",
        "bundle_version": "CFBundleVersion", "cf_bundle_version": "CFBundleVersion",
        "bundle_display_name": "CFBundleDisplayName", "cf_bundle_display_name": "CFBundleDisplayName",
        "minimum_os_version": "MinimumOSVersion"}
_NSX = {"ns_extension_point_identifier": "NSExtensionPointIdentifier",
        "extension_point_identifier": "NSExtensionPointIdentifier", "extension_point": "NSExtensionPointIdentifier",
        "ns_extension_principal_class": "NSExtensionPrincipalClass",
        "principal_class": "NSExtensionPrincipalClass",
        "ns_extension_main_storyboard": "NSExtensionMainStoryboard"}
_APPEX_DIR = re.compile(r"(?:.*/)?[^/]+\.appex$", re.I)


def _appexes(data, member):
    """[(appex_dir or "", Info.plist dict)]: a bare Info.plist, or every */X.appex/Info.plist of a zip (shallowest
    first; the one the member/question names first)."""
    pl = _plist(data)
    if pl is not None:
        return [("", pl)]
    zm = _zip_members(data)
    if not zm:
        return []
    z, names = zm
    out = []
    for n in names:
        d = posixpath.dirname(n)
        if posixpath.basename(n) == "Info.plist" and _APPEX_DIR.fullmatch(d):
            try:
                p = _plist(z.read(n))
            except Exception:
                p = None
            if p is not None:
                out.append((d, p))
    want = posixpath.basename(member or "").lower()
    return sorted(out, key=lambda c: (not (want and posixpath.basename(c[0]).lower() in (want, want + ".appex")),
                                      c[0].count("/"), c[0]))


def appex_value(data, ctx):
    """appex.<field> of an app-extension Info.plist (NSExtension dict), or of the first .appex in a zip/.ipa."""
    if data is None:
        return None
    try:
        f = ctx.get("field") or ""
        apps = _appexes(bytes(data), ctx.get("member"))
        if f == "appex_count":
            return len([a for a in apps if a[0]])
        if f == "appex_names":
            return [posixpath.basename(a[0]) for a in apps if a[0]] or "none"
        if not apps:
            return "none"
        d, pl = apps[0]
        nsx = pl.get("NSExtension")
        if d == "" and not isinstance(nsx, dict):
            return "none"                      # a bare Info.plist that is not an app extension
        if f == "appex_path":
            return d or "none"
        if f in _APX:
            return _out(pl.get(_APX[f]))
        if f in _NSX:
            return _out(nsx.get(_NSX[f]) if isinstance(nsx, dict) else None)
        if f in ("ns_extension_attribute_keys", "extension_attribute_keys"):
            a = nsx.get("NSExtensionAttributes") if isinstance(nsx, dict) else None
            return list(a) if isinstance(a, dict) else "none"
        param = ctx.get("param")
        if param:
            want = _norm(param)
            for src in (pl, nsx if isinstance(nsx, dict) else {}):
                for k, v in src.items():
                    if _norm(k) == want:
                        return _out(v)
            return "none"
        return None
    except Exception:
        return None
