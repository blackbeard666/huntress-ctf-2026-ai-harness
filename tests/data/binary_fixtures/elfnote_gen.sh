#!/bin/sh
# Builds the elfnote_* fixtures (run inside tests/data/binary_fixtures): HCFG blob in a custom ELF note.
# HCFG blob + note records are written with python3 stdlib struct/zlib (independent of lib/binary.py);
# placement by GNU objcopy (SHT_NOTE section) or by gas `.section .note.x,"a",@note` + GNU ld (PT_NOTE segment).
set -e
T=${TMPDIR:-/tmp}/elfnote; mkdir -p "$T"
blob() {  # $1 = key, $2 = json -> HCFG v1 blob on stdout
python3 -c 'import sys,struct,zlib; k=int(sys.argv[1]); p=sys.argv[2].encode(); sys.stdout.buffer.write(b"HCFG"+struct.pack("<BBHI",1,k,len(p),zlib.crc32(p))+bytes(b^k for b in p))' "$1" "$2"
}
note() {  # $1 = owner, $2 = type, $3 = desc file, $4 = align -> one note record on stdout
python3 -c 'import sys,struct; o=sys.argv[1].encode()+b"\0"; t=int(sys.argv[2],0); d=open(sys.argv[3],"rb").read(); a=int(sys.argv[4]); h=struct.pack("<III",len(o),len(d),t)+o; h+=b"\0"*(-len(h)%a); r=h+d; sys.stdout.buffer.write(r+b"\0"*(-len(r)%a))' "$1" "$2" "$3" "$4"
}
printf 'int main(void){return 0;}\n' > "$T/m.c"
# 1) SHT_NOTE section added by objcopy (alloc,readonly; 4-aligned), owner "Huntress", type 0x48434647
blob 90 '{"c2":"10.13.37.7:8443","sleep":30,"id":"note-sec"}' > "$T/b1"
note Huntress 0x48434647 "$T/b1" 4 > "$T/n1"
gcc -O1 -o "$T/a1" "$T/m.c"
objcopy --add-section .note.huntress="$T/n1" --set-section-flags .note.huntress=alloc,readonly "$T/a1" elfnote_objcopy_sec.bin
# 2) PT_NOTE variant: gas-emitted 8-aligned note (owner "HTRS": namesz 5 -> desc at +24, not +20) + a GNU note
#    before it in the same section; linker script maps it into its own PT_NOTE segment.
blob 0 '{"c2":"https://cfg.example/x","jitter":7}' > "$T/b2"
python3 -c 'import sys; d=open(sys.argv[1],"rb").read(); print(".section .note.htrs,\"a\",@note\n.balign 8\n.long 4\n.long 4\n.long 0x1234\n.asciz \"GNU\"\n.long 0xdeadbeef\n.balign 8\n.long 5\n.long %d\n.long 7\n.asciz \"HTRS\"\n.balign 8\n.byte %s\n.balign 8" % (len(d), ",".join(str(b) for b in d)))' "$T/b2" > "$T/n2.s"
cat > "$T/n2.ld" <<'LD'
PHDRS { text PT_LOAD FILEHDR PHDRS; hnote PT_NOTE; }
SECTIONS { . = 0x400000 + SIZEOF_HEADERS; .text : { *(.text*) } :text  .note.htrs : { *(.note.htrs) } :text :hnote }
LD
printf '.globl _start\n.text\n_start: mov $60,%%eax\nxor %%edi,%%edi\nsyscall\n' > "$T/s.s"
as -o "$T/s.o" "$T/s.s"; as -o "$T/n2.o" "$T/n2.s"
ld -T "$T/n2.ld" -o elfnote_ptnote_align8.bin "$T/s.o" "$T/n2.o"
# 2b) same image with the section header table zeroed (e_shoff/e_shnum/e_shstrndx = 0): PT_NOTE only
python3 -c 'import sys; d=bytearray(open(sys.argv[1],"rb").read()); d[0x28:0x30]=bytes(8); d[0x3c:0x40]=bytes(4); open(sys.argv[2],"wb").write(d)' elfnote_ptnote_align8.bin elfnote_ptnote_noshdr.bin
# 3) decoy: custom note whose desc is NOT an HCFG (magic HCFX) -> hcfg_note_offset "none"
printf 'HCFX\001\000\004\000junkjunk' > "$T/b3"
note Huntress 1 "$T/b3" 4 > "$T/n3"
objcopy --add-section .note.huntress="$T/n3" --set-section-flags .note.huntress=alloc,readonly "$T/a1" elfnote_decoy_hcfx.bin
# 4) decoy: plain gcc ELF, no custom note at all; 5) decoy: renamed impostor (the raw note record, no ELF)
cp "$T/a1" elfnote_decoy_plain.bin
cp "$T/n1" elfnote_decoy_rawnote.bin
