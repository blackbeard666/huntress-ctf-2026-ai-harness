"""Java class-file DEPTH fields (JVMS ch.4; prebuilt, SPECULATIVE -- never GM-asked yet). The header fields
(magic/version/this_class/super_class/access_flags/counts/source_file) live in java.py; this module walks the whole
ClassFile: constant pool (tag 1 Utf8 u2-len, 3/4 4 B, 5/6 8 B AND two slots, 7/8/16/19/20 u2, 9/10/11/12/17/18 2xu2,
15 u1+u2; Utf8 is MODIFIED UTF-8: \\xc0\\x80 = NUL, supplementary chars as two 3-byte surrogates), fields[], methods[],
class attributes. fmt java (aliases class, jvm) on a .class member; jar.main_class_* resolves the manifest Main-Class
(LAST occurrence, as java.util.jar / java -jar does) to its `a/b/C.class` entry and answers the same fields on it;
jar.module_* read the archive's root module-info.class (else the highest META-INF/versions/N/module-info.class).
Spellings (javap -v -p is the oracle):
  - class names: INTERNAL form as stored (`com/example/Foo`, same as java.this_class); *_dotted -> `com.example.Foo`.
  - interfaces / field_names / method_names / inner_classes / requires / attribute_names: JSON list, stored order
    (method_names includes `<init>` / `<clinit>` exactly as stored).
  - has_main_method: a method `main` with descriptor `([Ljava/lang/String;)V` and ACC_PUBLIC|ACC_STATIC (0x0009) set.
    main_method_descriptor: that descriptor, else the first method named `main`'s descriptor, else "none".
  - inner_classes_count: InnerClasses number_of_classes (javac also lists referenced nested classes such as
    MethodHandles$Lookup); no InnerClasses attribute -> 0.
  - kotlin_metadata_present: a class-level RuntimeVisibleAnnotations entry of type `Lkotlin/Metadata;`.
  - module-info.class (Module attribute): module_name (CONSTANT_Module name, dotted as stored), module_version
    (`jar --module-version` / javac --module-version; absent -> "none"), module_main_class (ModuleMainClass attr,
    internal form; *_dotted variant), requires (JSON module names in stored order, incl. the mandated java.base).
Not a class (wrong magic / Mach-O fat cafebabe / truncated pool) -> "none"."""
import struct

from ..spell import Hex
from .java import _header
from .jar import _zip, descend
from .jar_launch import _main_attrs, _last

_CLASS_FIELDS = (
    "interfaces", "interface_names", "interfaces_dotted",
    "field_count", "field_names",
    "method_names", "method_count",
    "has_main_method", "main_method_present", "has_main", "main_method_descriptor",
    "main_method_access_flags_u16_hex",
    "this_class_dotted", "class_name_dotted", "super_class_dotted",
    "inner_classes_count", "inner_class_count", "inner_classes",
    "kotlin_metadata_present", "has_kotlin_metadata", "is_kotlin",
    "attribute_names", "class_attribute_names",
    "is_module_info",
    "module_name", "module_version", "module_main_class", "module_main_class_dotted", "requires", "module_requires",
)

# jar.main_class_<x> -> <x> computed on the Main-Class entry (header fields too: java.py does not reach into jars)
_JAR_MAIN = (
    "this_class", "this_class_dotted", "super_class", "super_class_dotted", "access_flags_u16_hex",
    "interfaces", "field_count", "fields_count", "field_names", "method_names", "methods_count", "method_count",
    "has_main_method", "main_method_descriptor", "source_file", "major_version", "minor_version", "java_version",
    "kotlin_metadata_present", "inner_classes_count",
)

FIELDS = {
    ("java", "interfaces"): "jc_value",
    ("java", "interface_names"): "jc_value",
    ("java", "interfaces_dotted"): "jc_value",
    ("java", "field_count"): "jc_value",
    ("java", "field_names"): "jc_value",
    ("java", "method_names"): "jc_value",
    ("java", "method_count"): "jc_value",
    ("java", "has_main_method"): "jc_value",
    ("java", "main_method_present"): "jc_value",
    ("java", "has_main"): "jc_value",
    ("java", "main_method_descriptor"): "jc_value",
    ("java", "main_method_access_flags_u16_hex"): "jc_value",
    ("java", "this_class_dotted"): "jc_value",
    ("java", "class_name_dotted"): "jc_value",
    ("java", "super_class_dotted"): "jc_value",
    ("java", "inner_classes_count"): "jc_value",
    ("java", "inner_class_count"): "jc_value",
    ("java", "inner_classes"): "jc_value",
    ("java", "kotlin_metadata_present"): "jc_value",
    ("java", "has_kotlin_metadata"): "jc_value",
    ("java", "is_kotlin"): "jc_value",
    ("java", "attribute_names"): "jc_value",
    ("java", "class_attribute_names"): "jc_value",
    ("java", "is_module_info"): "jc_value",
    ("java", "module_name"): "jc_value",
    ("java", "module_version"): "jc_value",
    ("java", "module_main_class"): "jc_value",
    ("java", "module_main_class_dotted"): "jc_value",
    ("java", "requires"): "jc_value",
    ("java", "module_requires"): "jc_value",
    ("class", "interfaces"): "jc_value",
    ("class", "interface_names"): "jc_value",
    ("class", "interfaces_dotted"): "jc_value",
    ("class", "field_count"): "jc_value",
    ("class", "field_names"): "jc_value",
    ("class", "method_names"): "jc_value",
    ("class", "method_count"): "jc_value",
    ("class", "has_main_method"): "jc_value",
    ("class", "main_method_present"): "jc_value",
    ("class", "has_main"): "jc_value",
    ("class", "main_method_descriptor"): "jc_value",
    ("class", "main_method_access_flags_u16_hex"): "jc_value",
    ("class", "this_class_dotted"): "jc_value",
    ("class", "class_name_dotted"): "jc_value",
    ("class", "super_class_dotted"): "jc_value",
    ("class", "inner_classes_count"): "jc_value",
    ("class", "inner_class_count"): "jc_value",
    ("class", "inner_classes"): "jc_value",
    ("class", "kotlin_metadata_present"): "jc_value",
    ("class", "has_kotlin_metadata"): "jc_value",
    ("class", "is_kotlin"): "jc_value",
    ("class", "attribute_names"): "jc_value",
    ("class", "class_attribute_names"): "jc_value",
    ("class", "is_module_info"): "jc_value",
    ("class", "module_name"): "jc_value",
    ("class", "module_version"): "jc_value",
    ("class", "module_main_class"): "jc_value",
    ("class", "module_main_class_dotted"): "jc_value",
    ("class", "requires"): "jc_value",
    ("class", "module_requires"): "jc_value",
    ("jvm", "interfaces"): "jc_value",
    ("jvm", "interface_names"): "jc_value",
    ("jvm", "interfaces_dotted"): "jc_value",
    ("jvm", "field_count"): "jc_value",
    ("jvm", "field_names"): "jc_value",
    ("jvm", "method_names"): "jc_value",
    ("jvm", "method_count"): "jc_value",
    ("jvm", "has_main_method"): "jc_value",
    ("jvm", "main_method_present"): "jc_value",
    ("jvm", "has_main"): "jc_value",
    ("jvm", "main_method_descriptor"): "jc_value",
    ("jvm", "main_method_access_flags_u16_hex"): "jc_value",
    ("jvm", "this_class_dotted"): "jc_value",
    ("jvm", "class_name_dotted"): "jc_value",
    ("jvm", "super_class_dotted"): "jc_value",
    ("jvm", "inner_classes_count"): "jc_value",
    ("jvm", "inner_class_count"): "jc_value",
    ("jvm", "inner_classes"): "jc_value",
    ("jvm", "kotlin_metadata_present"): "jc_value",
    ("jvm", "has_kotlin_metadata"): "jc_value",
    ("jvm", "is_kotlin"): "jc_value",
    ("jvm", "attribute_names"): "jc_value",
    ("jvm", "class_attribute_names"): "jc_value",
    ("jvm", "is_module_info"): "jc_value",
    ("jvm", "module_name"): "jc_value",
    ("jvm", "module_version"): "jc_value",
    ("jvm", "module_main_class"): "jc_value",
    ("jvm", "module_main_class_dotted"): "jc_value",
    ("jvm", "requires"): "jc_value",
    ("jvm", "module_requires"): "jc_value",
    ("jar", "main_class_this_class"): "jc_jar_main",
    ("jar", "main_class_this_class_dotted"): "jc_jar_main",
    ("jar", "main_class_super_class"): "jc_jar_main",
    ("jar", "main_class_super_class_dotted"): "jc_jar_main",
    ("jar", "main_class_access_flags_u16_hex"): "jc_jar_main",
    ("jar", "main_class_interfaces"): "jc_jar_main",
    ("jar", "main_class_field_count"): "jc_jar_main",
    ("jar", "main_class_fields_count"): "jc_jar_main",
    ("jar", "main_class_field_names"): "jc_jar_main",
    ("jar", "main_class_method_names"): "jc_jar_main",
    ("jar", "main_class_methods_count"): "jc_jar_main",
    ("jar", "main_class_method_count"): "jc_jar_main",
    ("jar", "main_class_has_main_method"): "jc_jar_main",
    ("jar", "main_class_main_method_descriptor"): "jc_jar_main",
    ("jar", "main_class_source_file"): "jc_jar_main",
    ("jar", "main_class_major_version"): "jc_jar_main",
    ("jar", "main_class_minor_version"): "jc_jar_main",
    ("jar", "main_class_java_version"): "jc_jar_main",
    ("jar", "main_class_kotlin_metadata_present"): "jc_jar_main",
    ("jar", "main_class_inner_classes_count"): "jc_jar_main",
    ("jar", "module_name"): "jc_jar_module",
    ("jar", "module_version"): "jc_jar_module",
    ("jar", "module_main_class"): "jc_jar_module",
    ("jar", "module_main_class_dotted"): "jc_jar_module",
    ("jar", "module_requires"): "jc_jar_module",
    ("java_archive", "main_class_this_class"): "jc_jar_main",
    ("java_archive", "main_class_super_class"): "jc_jar_main",
    ("java_archive", "main_class_access_flags_u16_hex"): "jc_jar_main",
    ("java_archive", "main_class_interfaces"): "jc_jar_main",
    ("java_archive", "main_class_method_names"): "jc_jar_main",
    ("java_archive", "main_class_has_main_method"): "jc_jar_main",
    ("java_archive", "main_class_main_method_descriptor"): "jc_jar_main",
    ("java_archive", "main_class_source_file"): "jc_jar_main",
    ("java_archive", "main_class_major_version"): "jc_jar_main",
    ("java_archive", "main_class_java_version"): "jc_jar_main",
    ("java_archive", "module_name"): "jc_jar_module",
    ("java_archive", "module_version"): "jc_jar_module",
    ("java_archive", "module_main_class"): "jc_jar_module",
    ("java_archive", "module_requires"): "jc_jar_module",
}

_SIZE = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
_MAIN_DESC = "([Ljava/lang/String;)V"


def _mutf8(raw):
    """Modified UTF-8 -> str (NUL as C0 80, supplementary chars as CESU-8 surrogate pairs)."""
    try:
        s = raw.replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass")
        return s.encode("utf-16-le", "surrogatepass").decode("utf-16-le")
    except UnicodeError:
        return raw.decode("utf-8", "replace")


class _R:
    def __init__(self, b, off):
        self.b, self.off = b, off

    def u1(self):
        v = self.b[self.off]
        self.off += 1
        return v

    def u2(self):
        v, = struct.unpack_from(">H", self.b, self.off)
        self.off += 2
        return v

    def u4(self):
        v, = struct.unpack_from(">I", self.b, self.off)
        self.off += 4
        return v

    def take(self, n):
        if self.off + n > len(self.b):
            raise ValueError("truncated")
        v = self.b[self.off:self.off + n]
        self.off += n
        return v


def _skip_element_value(r):
    tag = chr(r.u1())
    if tag in "BCDFIJSZsc":
        r.u2()
    elif tag == "e":
        r.u2()
        r.u2()
    elif tag == "@":
        _skip_annotation(r)
    elif tag == "[":
        for _ in range(r.u2()):
            _skip_element_value(r)
    else:
        raise ValueError("bad element_value tag")


def _skip_annotation(r):
    t = r.u2()
    for _ in range(r.u2()):
        r.u2()
        _skip_element_value(r)
    return t


def parse_class(b):
    """A dict describing a ClassFile, or None when `b` is not a (parseable) class."""
    h = _header(b)
    if h is None:
        return None
    minor, major, cpc = h
    b = bytes(b)
    r = _R(b, 10)
    pool, i = {}, 1
    while i < cpc:
        tag = r.u1()
        if tag == 1:
            pool[i] = (1, _mutf8(r.take(r.u2())))
        elif tag in _SIZE:
            pool[i] = (tag, r.take(_SIZE[tag]))
        else:
            return None
        i += 2 if tag in (5, 6) else 1

    def utf8(idx):
        t = pool.get(idx)
        return t[1] if t and t[0] == 1 else None

    def ref(idx, tag):     # Class (7) / Module (19) / Package (20) -> its Utf8 name
        t = pool.get(idx)
        return utf8(struct.unpack(">H", t[1])[0]) if t and t[0] == tag else None

    def attrs():
        out = []
        for _ in range(r.u2()):
            name = utf8(r.u2())
            out.append((name, r.take(r.u4())))
        return out

    def members():
        out = []
        for _ in range(r.u2()):
            flags, ni, di = r.u2(), r.u2(), r.u2()
            out.append((flags, utf8(ni), utf8(di), attrs()))
        return out

    flags, this_i, super_i = r.u2(), r.u2(), r.u2()
    ifaces = [ref(r.u2(), 7) for _ in range(r.u2())]
    fields = members()
    methods = members()
    cattrs = attrs()
    c = {"minor": minor, "major": major, "flags": flags, "this": ref(this_i, 7),
         "super": ref(super_i, 7) if super_i else None, "interfaces": ifaces, "fields": fields,
         "methods": methods, "attrs": cattrs, "inner": None, "annotations": [], "source_file": None,
         "module": None, "module_main_class": None}
    for name, body in cattrs:
        a = _R(body, 0)
        if name == "SourceFile" and len(body) == 2:
            c["source_file"] = utf8(a.u2())
        elif name == "InnerClasses":
            n = a.u2()
            c["inner"] = [ref(struct.unpack_from(">H", body, 2 + 8 * k)[0], 7) for k in range(n)
                          if 2 + 8 * k + 2 <= len(body)]
            c["inner_count"] = n
        elif name == "RuntimeVisibleAnnotations":
            for _ in range(a.u2()):
                c["annotations"].append(utf8(_skip_annotation(a)))
        elif name == "ModuleMainClass" and len(body) == 2:
            c["module_main_class"] = ref(a.u2(), 7)
        elif name == "Module":
            mname, _mflags, vi = ref(a.u2(), 19), a.u2(), a.u2()
            req = []
            for _ in range(a.u2()):
                req.append(ref(a.u2(), 19))
                a.u2()
                a.u2()
            c["module"] = {"name": mname, "version": utf8(vi) if vi else None, "requires": req}
    return c


def _dotted(name):
    return name.replace("/", ".") if name else None


def _main(c):
    for fl, n, d, _ in c["methods"]:
        if n == "main" and d == _MAIN_DESC and fl & 0x0009 == 0x0009:
            return fl, d
    for fl, n, d, _ in c["methods"]:
        if n == "main":
            return fl, d
    return None, None


def _field_value(c, field):
    none = "none"
    if field in ("interfaces", "interface_names"):
        return list(c["interfaces"])
    if field == "interfaces_dotted":
        return [_dotted(n) for n in c["interfaces"]]
    if field in ("field_count", "fields_count"):
        return len(c["fields"])
    if field == "field_names":
        return [n for _, n, _, _ in c["fields"]]
    if field == "method_names":
        return [n for _, n, _, _ in c["methods"]]
    if field in ("method_count", "methods_count"):
        return len(c["methods"])
    if field in ("has_main_method", "main_method_present", "has_main"):
        fl, d = _main(c)
        return d == _MAIN_DESC and fl & 0x0009 == 0x0009
    if field == "main_method_descriptor":
        return _main(c)[1] or none
    if field == "main_method_access_flags_u16_hex":
        fl = _main(c)[0]
        return none if fl is None else Hex(fl, 4)
    if field == "this_class":
        return c["this"] or none
    if field in ("this_class_dotted", "class_name_dotted"):
        return _dotted(c["this"]) or none
    if field == "super_class":
        return c["super"] or none
    if field == "super_class_dotted":
        return _dotted(c["super"]) or none
    if field == "access_flags_u16_hex":
        return Hex(c["flags"], 4)
    if field == "source_file":
        return c["source_file"] or none
    if field == "major_version":
        return c["major"]
    if field == "minor_version":
        return c["minor"]
    if field == "java_version":
        m = c["major"]
        return str(m - 44) if m >= 49 else "1.%d" % (m - 44)
    if field in ("inner_classes_count", "inner_class_count"):
        return c.get("inner_count", 0)
    if field == "inner_classes":
        return list(c["inner"] or [])
    if field in ("kotlin_metadata_present", "has_kotlin_metadata", "is_kotlin"):
        return "Lkotlin/Metadata;" in c["annotations"]
    if field in ("attribute_names", "class_attribute_names"):
        return [n for n, _ in c["attrs"]]
    if field == "is_module_info":
        return c["module"] is not None
    m = c["module"]
    if field == "module_name":
        return (m or {}).get("name") or none
    if field == "module_version":
        return (m or {}).get("version") or none
    if field in ("requires", "module_requires"):
        return none if m is None else list(m["requires"])
    if field == "module_main_class":
        return c["module_main_class"] or none
    if field == "module_main_class_dotted":
        return _dotted(c["module_main_class"]) or none
    return None


def _safe(fn):
    try:
        return fn()
    except (struct.error, IndexError, ValueError, TypeError, KeyError, AttributeError):
        return "none"


def jc_value(data, ctx):
    """java|class|jvm.<field> on a .class member."""
    if data is None:
        return None

    def run():
        c = parse_class(data)
        return "none" if c is None else _field_value(c, (ctx or {}).get("field") or "")
    return _safe(run)


def _read(z, name):
    try:
        return z.read(name)
    except Exception:  # noqa: BLE001 -- encrypted / bad CRC / unsupported method
        return None


def jc_jar_main(data, ctx):
    """jar.main_class_<field>: <field> of the class entry the manifest Main-Class (last occurrence) names."""
    if data is None:
        return None

    def run():
        z, main = _main_attrs(data, ctx)
        if main is None:
            return "none"
        mc = _last(main, "Main-Class")
        if not mc:
            return "none"
        name = mc.strip().replace(".", "/") + ".class"
        names = z.namelist()
        if name not in names:
            low = {n.lower(): n for n in names}
            name = low.get(name.lower())
            if name is None:
                return "none"
        c = parse_class(_read(z, name))
        field = ((ctx or {}).get("field") or "")[len("main_class_"):]
        return "none" if c is None else _field_value(c, field)
    return _safe(run)


def jc_jar_module(data, ctx):
    """jar.module_*: the archive's module-info.class (root, else highest META-INF/versions/N/)."""
    if data is None:
        return None

    def run():
        z = _zip(descend(data, ctx))
        if z is None:
            return "none"
        names = z.namelist()
        cand = "module-info.class" if "module-info.class" in names else None
        if cand is None:
            vers = []
            for n in names:
                p = n.split("/")
                if len(p) == 4 and p[:2] == ["META-INF", "versions"] and p[3] == "module-info.class" and p[2].isdigit():
                    vers.append((int(p[2]), n))
            cand = max(vers)[1] if vers else None
        if cand is None:
            return "none"
        c = parse_class(_read(z, cand))
        if c is None or c["module"] is None:
            return "none"
        field = (ctx or {}).get("field") or ""
        return _field_value(c, "requires" if field == "module_requires" else field)
    return _safe(run)
