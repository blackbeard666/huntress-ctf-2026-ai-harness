"""JAR fields (GM-verified). A jar is a zip holding META-INF/MANIFEST.MF; its main section (until the first blank line)
is `Name: value` lines, 72-byte wrapped (a continuation line starts with ONE space, which is dropped). Parsed by
lib.meta.prebuilt.jar."""


def main_class(data, ctx):
    """D22: the manifest's main-section Main-Class verbatim, continuation lines joined ("arena.evidence.ArtifactMain"
    on the single, TT and all 6 Mastery sets); no manifest / no attribute -> "none"."""
    from .prebuilt.jar import jar_manifest
    return jar_manifest(data, dict(ctx or {}, field="main_class"))
