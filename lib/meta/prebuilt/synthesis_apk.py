"""Cross-APK clone vs rebuild synthesis (prebuilt, SPECULATIVE; the spelling was never GM-verified). Coverage-atlas row
"apk-clone-rebuild-synthesis": "which of these APKs are the same app rebuilt, which are clones / repackages, which one
borrows another app's name". Ids `metadata-day-NN-synthesis-<key>`. Members come from the question's `Files: [...]`
list (parsed like lib.meta.synthesis.digest_order), else from `data` when the artifact IS the container zip (all
members, zip order). Per member, by CONTENT only (names / extensions never trusted; non-APK members are skipped):
  * package    = <manifest package=> (apk_manifest walk),     versionCode = android:versionCode (int, absent -> 0);
  * label      = android:label as shown (inline string, or the resources.arsc default-config value; apk_resources);
  * signer     = SHA-256 of the signer certificate DER, lowercase hex (v3.1 > v3 > v2 > v1, apk_signing); unsigned
                 -> no signer; digest = SHA-256 of the whole APK file.
  * .ipa (zip with Payload/<x>.app/Info.plist): package = CFBundleIdentifier, versionCode = CFBundleVersion (dotted
    versions compared numerically), label = CFBundleDisplayName else CFBundleName; no signer (unverified path).
Definitions (names ascending inside every group unless the text says descending; nothing applies -> "none"):
  * original of a package = its lowest-versionCode member (tie -> name);
  * reference package of a label = the package with the most members carrying that label (tie -> lowest
    versionCode, then package name) -- clones are the odd ones out, the family is the reference;
  * clone_members: member whose signer differs from its package original's signer, OR whose label belongs to a
    different reference package whose original's signer differs from the member's;
  * rebuild_members: same package AND same signer as another member, with a different versionCode or APK digest
    (symmetric: the original is listed too; if the text says original / earliest / first / baseline it is excluded);
  * borrowed_label_member: member whose label equals another package's label and whose package is not that label's
    reference package (one -> the name, several -> sorted list);
  * package_groups / signer_groups: {key: sorted names}, keys ascending (object); *_group_list or a text asking for a
    "list of lists"/"array" -> [[names]] ordered by first name;
  * version_code_order: names by versionCode ascending (tie -> name); distinct_package_count / distinct_signer_count."""
import hashlib
import io
import re
import zipfile

FIELDS = {
    ("synthesis", "package_groups"): "apk_value",
    ("synthesis", "package_group_map"): "apk_value",
    ("synthesis", "package_name_groups"): "apk_value",
    ("synthesis", "package_id_groups"): "apk_value",
    ("synthesis", "files_by_package"): "apk_value",
    ("synthesis", "package_group_list"): "apk_value",
    ("synthesis", "signer_groups"): "apk_value",
    ("synthesis", "signer_group_map"): "apk_value",
    ("synthesis", "signer_cert_groups"): "apk_value",
    ("synthesis", "signer_sha256_groups"): "apk_value",
    ("synthesis", "signing_cert_groups"): "apk_value",
    ("synthesis", "certificate_groups"): "apk_value",
    ("synthesis", "files_by_signer"): "apk_value",
    ("synthesis", "signer_group_list"): "apk_value",
    ("synthesis", "clone_members"): "apk_value",
    ("synthesis", "clone_files"): "apk_value",
    ("synthesis", "clone_filenames"): "apk_value",
    ("synthesis", "clones"): "apk_value",
    ("synthesis", "cloned_members"): "apk_value",
    ("synthesis", "repackaged_members"): "apk_value",
    ("synthesis", "repackaged_files"): "apk_value",
    ("synthesis", "clone_count"): "apk_value",
    ("synthesis", "rebuild_members"): "apk_value",
    ("synthesis", "rebuild_files"): "apk_value",
    ("synthesis", "rebuild_filenames"): "apk_value",
    ("synthesis", "rebuilds"): "apk_value",
    ("synthesis", "rebuilt_members"): "apk_value",
    ("synthesis", "rebuild_count"): "apk_value",
    ("synthesis", "borrowed_label_member"): "apk_value",
    ("synthesis", "borrowed_label_file"): "apk_value",
    ("synthesis", "borrowed_label_members"): "apk_value",
    ("synthesis", "borrowed_label_files"): "apk_value",
    ("synthesis", "label_borrower"): "apk_value",
    ("synthesis", "impersonating_member"): "apk_value",
    ("synthesis", "version_code_order"): "apk_value",
    ("synthesis", "versioncode_order"): "apk_value",
    ("synthesis", "version_order"): "apk_value",
    ("synthesis", "distinct_package_count"): "apk_value",
    ("synthesis", "unique_package_count"): "apk_value",
    ("synthesis", "package_count"): "apk_value",
    ("synthesis", "distinct_signer_count"): "apk_value",
    ("synthesis", "unique_signer_count"): "apk_value",
    ("synthesis", "signer_count"): "apk_value",
}


def _ipa(b):
    """(package, version, label) of an .ipa's Payload/<x>.app/Info.plist, or None."""
    import plistlib
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
        info = [n for n in z.namelist() if re.match(r"^Payload/[^/]+\.app/Info\.plist$", n)]
        if not info:
            return None
        p = plistlib.loads(z.read(info[0]))
    except Exception:  # noqa: BLE001 - not an ipa
        return None
    pkg = p.get("CFBundleIdentifier")
    if not isinstance(pkg, str):
        return None
    ver = str(p.get("CFBundleVersion") or "0")
    vkey = tuple(int(x) for x in re.findall(r"\d+", ver)) or (0,)
    return pkg, vkey, p.get("CFBundleDisplayName") or p.get("CFBundleName")


def profile(b):
    """{package, vc, label, signer, digest} of an APK / IPA, or None (not one)."""
    b = bytes(b or b"")
    if b[:2] != b"PK":
        return None
    from .apk_manifest import _manifest, version_code
    m = _manifest(b)
    if not isinstance(m, tuple) or not m[1]:
        ipa = _ipa(b)
        if ipa is None:
            return None
        return {"package": ipa[0], "vc": ipa[1], "label": ipa[2], "signer": None,
                "digest": hashlib.sha256(b).hexdigest()}
    from .apk_resources import label_resolved
    from .apk_signing import cert_sha256
    vc = version_code(b, {})
    vc = vc if isinstance(vc, int) else 0
    try:
        label = label_resolved(b, {})
    except Exception:  # noqa: BLE001
        label = None
    try:
        signer = cert_sha256(b, {})
    except Exception:  # noqa: BLE001
        signer = None
    return {"package": m[1], "vc": (vc,), "label": label.strip() if isinstance(label, str) and label != "none"
            and label.strip() else None,
            "signer": signer if isinstance(signer, str) and re.fullmatch(r"[0-9a-f]{64}", signer) else None,
            "digest": hashlib.sha256(b).hexdigest()}


def _instr(text):
    return re.sub(r"Files:\s*\[.*?\]", "", text or "", flags=re.S)


def _desc(text):
    return bool(re.search(r"\bdescending\b|\breverse\b|\bnewest first\b|\bhighest first\b", _instr(text), re.I))


def _sorted(names, text):
    return sorted(names, reverse=_desc(text))


def _groups(rows, key, field, text):
    g = {}
    for r in rows:
        k = r[key]
        if k is not None:
            g.setdefault(k, []).append(r["name"])
    if not g:
        return "none"
    as_list = field.endswith("_list") or re.search(r"list of lists|array of arrays|\barrays?\b|list of groups",
                                                   _instr(text), re.I)
    if as_list:
        return sorted((sorted(v) for v in g.values()), key=lambda v: v[0])
    return {k: _sorted(g[k], text) for k in sorted(g)}


def analyse(rows):
    """(originals {pkg: row}, label refs {label: (pkg, row)}, clones set, rebuild pairs set, borrowers set)."""
    by_pkg = {}
    for r in rows:
        by_pkg.setdefault(r["package"], []).append(r)
    orig = {p: min(rs, key=lambda r: (r["vc"], r["name"])) for p, rs in by_pkg.items()}
    by_label = {}
    for r in rows:
        if r["label"]:
            by_label.setdefault(r["label"], []).append(r)
    ref = {}
    for lab, rs in by_label.items():
        cnt = {}
        for r in rs:
            cnt[r["package"]] = cnt.get(r["package"], 0) + 1
        pk = min(cnt, key=lambda p: (-cnt[p], orig[p]["vc"], p))
        ref[lab] = (pk, orig[pk])
    clones, borrowers = set(), set()
    for r in rows:
        o = orig[r["package"]]
        if r["signer"] != o["signer"]:
            clones.add(r["name"])
        if r["label"] and r["label"] in ref:
            pk, ro = ref[r["label"]]
            if pk != r["package"]:
                borrowers.add(r["name"])
                if r["signer"] != ro["signer"]:
                    clones.add(r["name"])
    rebuilds = set()
    for p, rs in by_pkg.items():
        for a in rs:
            for b in rs:
                if a is not b and a["signer"] is not None and a["signer"] == b["signer"] \
                        and (a["vc"] != b["vc"] or a["digest"] != b["digest"]):
                    rebuilds.add(a["name"])
    return orig, ref, clones, rebuilds, borrowers


def apk_value_of(names, get_bytes, field, text=""):
    """The raw value for `field` over `names`; None = unreadable, "none" = no APK / nothing applies."""
    rows = []
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        p = profile(b)
        if p is not None:
            p["name"] = n
            rows.append(p)
    if not rows:
        return "none"
    f = field or ""
    if f.startswith("package") and "group" in f or f == "files_by_package":
        return _groups(rows, "package", f, text)
    if ("signer" in f or "cert" in f) and "group" in f or f == "files_by_signer":
        return _groups(rows, "signer", f, text)
    if f in ("distinct_package_count", "unique_package_count", "package_count"):
        return len({r["package"] for r in rows})
    if f in ("distinct_signer_count", "unique_signer_count", "signer_count"):
        return len({r["signer"] for r in rows if r["signer"]})
    if f.startswith("version"):
        ks = sorted(((r["vc"], r["name"]) for r in rows), reverse=_desc(text))
        return [n for _, n in ks]
    orig, _ref, clones, rebuilds, borrowers = analyse(rows)
    if f.startswith(("clone", "repackaged")):
        return len(clones) if f.endswith("count") else (_sorted(clones, text) or "none")
    if f.startswith("rebuil"):
        if re.search(r"\b(original|earliest|first|baseline|reference)\b", _instr(text), re.I):
            rebuilds -= {o["name"] for o in orig.values()}
        return len(rebuilds) if f.endswith("count") else (_sorted(rebuilds, text) or "none")
    if f.startswith(("borrowed", "label_borrower", "impersonating")):
        out = sorted(borrowers)
        if not out:
            return "none"
        return out[0] if len(out) == 1 and not f.endswith(("members", "files")) else out
    return None


def apk_value(data, ctx):
    """synthesis.<APK clone / rebuild field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        q = ctx.get("question")
        text = str((q.get("question") if isinstance(q, dict) else q) or "")
        v = apk_value_of(names, read, ctx.get("field") or "", text)
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
