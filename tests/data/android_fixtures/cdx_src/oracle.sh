#!/bin/sh
# Independent reader for the cdx_* fixtures (no lib.android): pull the optimised-dex entry with unzip -p, prove the
# container (lief.VDEX for vdex 006 / readelf --dyn-syms `oatdata` for the OAT / od for the cdex & vdex019 magic), then
# take the encoded pool string with lief's DEX string list (vdex006) or binutils `strings -n 24` and decode it with
# coreutils base64 -d / base32 -d / xxd -r -p. Prints the ANS token (nothing for the decoy's 15-hex near miss).
apk=$1; T=${TMPDIR:-/tmp}/cdx_oracle.$$; mkdir -p "$T"
case "$apk" in
*vdex006*) unzip -p "$apk" assets/oat/arm64/base.vdex > "$T/v"
  .venv/bin/python -I -c 'import lief,sys; v=lief.VDEX.parse(sys.argv[1]); print("vdex", v.header.version, len(v.dex_files), "dex", file=sys.stderr); [print(s) for f in v.dex_files for s in f.strings if len(s)>=24]' "$T/v" | grep -o "cHJvb2Y9[A-Za-z0-9+/]*=*" | base64 -d ;;
*cdex_b32*) unzip -p "$apk" assets/payload/core.cdex > "$T/v"; od -An -c -N8 "$T/v" >&2
  strings -n 24 "$T/v" | grep -o "OBZG633G[A-Z2-7]*=*" | base32 -d ;;
*vdex019*) unzip -p "$apk" assets/oat/arm64/base.vdex > "$T/v"; od -An -c -N12 "$T/v" >&2
  strings -n 24 "$T/v" | grep -o "70726f6f[0-9a-f]*" | xxd -r -p ;;
*oat*) unzip -p "$apk" assets/oat/arm64/base.odex > "$T/v"; readelf --dyn-syms -W "$T/v" | grep -w oatdata >&2
  strings -n 24 "$T/v" | grep -o "cHJvb2Y9[A-Za-z0-9+/]*=*" | base64 -d ;;
esac | grep -ao 'ANS-[0-9a-fA-F]\{16\}'
rm -rf "$T"
