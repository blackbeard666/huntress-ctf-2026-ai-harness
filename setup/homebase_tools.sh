#!/usr/bin/env bash
# Heavy analysis toolchain ON Homebase, no root: everything lands in ~/hbtools (bin/ on PATH for Homebase workers and
# hb_timed). Downloads straight from upstream on the VM (AWS egress is fast; the player VPN is ~140 KB/s), versions
# matched to the local toolbox (setup/install_tools.sh). Idempotent: each tool is skipped once its marker exists.
# ~/hw/bin's links point at /home/testpwn/... and dangle on the VM; PATH lookups skip dangling links, so ~/hbtools/bin
# placed after ~/hw/bin fills exactly those gaps.
set -uo pipefail
T=~/hbtools; B=$T/bin; DL=$T/.dl
mkdir -p "$B" "$DL"
JADX_V=1.5.6 APKTOOL_V=2.11.1 GHIDRA_V=12.1.4 RIZIN_V=0.9.1 UPX_V=5.0.2
log() { echo "[hb-tools] $*"; }
fetch() { curl -fsSL --retry 3 --connect-timeout 15 -o "$2" "$1"; }
# Resolve a GitHub release asset URL by regex (tag "latest" or an exact tag); empty on failure.
gh_asset() {
  local api="https://api.github.com/repos/$1/releases/${2/#latest/latest}"
  [ "$2" = latest ] || api="https://api.github.com/repos/$1/releases/tags/$2"
  curl -fsSL --connect-timeout 15 "$api" | python3 -c "
import json,re,sys
for a in json.load(sys.stdin).get('assets',[]):
    if re.search(r'''$3''', a['name']): print(a['browser_download_url']); break"
}
wrap() { printf '#!/usr/bin/env bash\n%s\n' "$2" > "$B/$1"; chmod +x "$B/$1"; }

# JDK 21 (Temurin): jadx/apktool/dex2jar need a JRE, Ghidra needs a JDK.
if [ ! -x $T/jdk/bin/java ]; then
  fetch "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse" $DL/jdk.tgz \
    && mkdir -p $T/jdk && tar -xzf $DL/jdk.tgz -C $T/jdk --strip-components=1 && log "jdk 21 ok" || log "jdk FAILED"
fi
[ -x $T/jdk/bin/java ] && ln -sf $T/jdk/bin/java $B/java
export JAVA_HOME=$T/jdk PATH="$B:$PATH"

if [ ! -x $T/jadx/bin/jadx ]; then
  fetch "https://github.com/skylot/jadx/releases/download/v$JADX_V/jadx-$JADX_V.zip" $DL/jadx.zip \
    && mkdir -p $T/jadx && python3 -c "import zipfile;zipfile.ZipFile('$DL/jadx.zip').extractall('$T/jadx')" \
    && chmod +x $T/jadx/bin/* && log "jadx $JADX_V ok" || log "jadx FAILED"
fi
[ -x $T/jadx/bin/jadx ] && wrap jadx "JAVA_HOME=$T/jdk exec $T/jadx/bin/jadx \"\$@\""

if [ ! -s $T/apktool.jar ]; then
  fetch "https://github.com/iBotPeaches/Apktool/releases/download/v$APKTOOL_V/apktool_$APKTOOL_V.jar" $T/apktool.jar \
    && log "apktool $APKTOOL_V ok" || { rm -f $T/apktool.jar; log "apktool FAILED"; }
fi
[ -s $T/apktool.jar ] && wrap apktool "exec $T/jdk/bin/java -jar $T/apktool.jar \"\$@\""

if [ ! -x $T/dex2jar/d2j-dex2jar.sh ]; then
  u=$(gh_asset pxb1988/dex2jar latest '^dex-tools.*\.zip$')
  [ -n "$u" ] && fetch "$u" $DL/d2j.zip && python3 -c "
import zipfile,os,shutil
z=zipfile.ZipFile('$DL/d2j.zip'); z.extractall('$DL/d2j'); top=os.path.join('$DL/d2j',os.listdir('$DL/d2j')[0])
shutil.rmtree('$T/dex2jar',ignore_errors=True); shutil.move(top,'$T/dex2jar')" && chmod +x $T/dex2jar/*.sh \
    && log "dex2jar ok" || log "dex2jar FAILED"
fi
if [ -x $T/dex2jar/d2j-dex2jar.sh ]; then
  wrap d2j-dex2jar "JAVA_HOME=$T/jdk PATH=$T/jdk/bin:\$PATH exec $T/dex2jar/d2j-dex2jar.sh \"\$@\""; cp $B/d2j-dex2jar $B/dex2jar
fi

if [ ! -x $T/rizin/bin/rizin ]; then
  u=$(gh_asset rizinorg/rizin "v$RIZIN_V" 'static-x86_64\.tar\.xz$')
  [ -n "$u" ] && fetch "$u" $DL/rizin.txz && mkdir -p $T/rizin && tar -xJf $DL/rizin.txz -C $T/rizin \
    && { [ -x $T/rizin/bin/rizin ] || mv $T/rizin/*/* $T/rizin/ 2>/dev/null; true; } && log "rizin $RIZIN_V ok" || log "rizin FAILED"
fi
for x in rizin rz-bin rz-asm rz-ax rz-hash rz-find rz-diff; do [ -x $T/rizin/bin/$x ] && ln -sf $T/rizin/bin/$x $B/$x; done

if [ ! -x $B/upx ]; then
  fetch "https://github.com/upx/upx/releases/download/v$UPX_V/upx-$UPX_V-amd64_linux.tar.xz" $DL/upx.txz \
    && tar -xJf $DL/upx.txz -C $DL && cp $DL/upx-$UPX_V-amd64_linux/upx $B/upx && log "upx $UPX_V ok" || log "upx FAILED"
fi

if [ ! -x $B/GoReSym ]; then
  u=$(gh_asset mandiant/GoReSym latest '[Ll]inux.*\.zip$')
  [ -n "$u" ] && fetch "$u" $DL/goresym.zip && python3 -c "
import zipfile
z=zipfile.ZipFile('$DL/goresym.zip')
n=[i for i in z.namelist() if i.rstrip('/').endswith('GoReSym')][0]
open('$B/GoReSym','wb').write(z.read(n))" && chmod +x $B/GoReSym && log "GoReSym ok" || log "GoReSym FAILED"
fi

if [ ! -x $T/exiftool/exiftool ]; then
  v=$(curl -fsSL --connect-timeout 15 https://exiftool.org/ver.txt 2>/dev/null)
  # exiftool.org only keeps the newest tarball; the GitHub tag archive is stable
  [ -n "$v" ] && { fetch "https://github.com/exiftool/exiftool/archive/refs/tags/$v.tar.gz" $DL/exif.tgz \
    || fetch "https://exiftool.org/Image-ExifTool-$v.tar.gz" $DL/exif.tgz; } && mkdir -p $T/exiftool \
    && tar -xzf $DL/exif.tgz -C $T/exiftool --strip-components=1 && log "exiftool $v ok" || log "exiftool FAILED"
fi
[ -x $T/exiftool/exiftool ] && ln -sf $T/exiftool/exiftool $B/exiftool

# Ghidra headless (~450 MB unpacked). 3.8 GB RAM: cap the heap so a decompile can't starve hb_timed.
if [ ! -x $T/ghidra/support/analyzeHeadless ]; then
  u=$(gh_asset NationalSecurityAgency/ghidra "Ghidra_${GHIDRA_V}_build" '\.zip$')
  [ -n "$u" ] && fetch "$u" $DL/ghidra.zip && python3 -c "
import zipfile,os,shutil
z=zipfile.ZipFile('$DL/ghidra.zip'); z.extractall('$DL/gh'); top=os.path.join('$DL/gh',os.listdir('$DL/gh')[0])
shutil.rmtree('$T/ghidra',ignore_errors=True); shutil.move(top,'$T/ghidra')" \
    && chmod +x $T/ghidra/support/* $T/ghidra/Ghidra/Features/Decompiler/os/linux_x86_64/* 2>/dev/null \
    && sed -i 's/^MAXMEM=.*/MAXMEM=1536M/' $T/ghidra/support/analyzeHeadless && rm -rf $DL/gh $DL/ghidra.zip \
    && log "ghidra $GHIDRA_V ok" || log "ghidra FAILED"
fi
[ -x $T/ghidra/support/analyzeHeadless ] && wrap analyzeHeadless "JAVA_HOME=$T/jdk PATH=$T/jdk/bin:\$PATH exec $T/ghidra/support/analyzeHeadless \"\$@\""

# .NET 10 SDK + ILSpy CLI 11.x (user-space dotnet-install; ilspycmd 11 targets net10.0, same as the local toolbox).
if ! ls -d $T/dotnet/shared/Microsoft.NETCore.App/10.* >/dev/null 2>&1; then
  fetch https://dot.net/v1/dotnet-install.sh $DL/dotnet-install.sh \
    && bash $DL/dotnet-install.sh --channel 10.0 --install-dir $T/dotnet >/dev/null 2>&1 && log "dotnet 10 ok" || log "dotnet FAILED"
fi
if [ -x $T/dotnet/dotnet ]; then
  ln -sf $T/dotnet/dotnet $B/dotnet
  [ -x $T/dotnet-tools/ilspycmd ] || DOTNET_ROOT=$T/dotnet DOTNET_CLI_TELEMETRY_OPTOUT=1 $T/dotnet/dotnet tool install \
    ilspycmd --version 11.1.0.9782 --tool-path $T/dotnet-tools >/dev/null 2>&1 && log "ilspycmd ok"
  [ -x $T/dotnet-tools/ilspycmd ] && wrap ilspycmd "DOTNET_ROOT=$T/dotnet exec $T/dotnet-tools/ilspycmd \"\$@\""
fi

# Python-side tools the lanes use (user site; same as homebase_setup.sh's pip line).
python3 -m pip install --user --break-system-packages -q binwalk pyinstxtractor-ng uncompyle6 2>&1 | tail -1
rm -rf $DL
for t in java jadx apktool d2j-dex2jar rizin upx GoReSym exiftool analyzeHeadless dotnet ilspycmd; do
  [ -x $B/$t ] && echo "[ok] $t" || echo "[MISSING] $t"
done
touch $T/.done
