#!/usr/bin/env bash
# independent reader for one langof fixture: file(1), readelf .comment, nm symbol cues, javap, dnfile assembly refs,
# wasm-objdump, unzip. usage: bash langof_oracle.sh <fixture.bin>
f=$1
echo "file: $(file -b "$f")"
case "$(file -b "$f")" in
  ELF*) readelf -p .comment "$f" 2>/dev/null | grep -E 'GCC|clang' | head -2
        echo "nm _Z count: $(nm -a "$f" 2>/dev/null | grep -c ' _Z')"
        echo "nm runtime-cue symbols: $(nm -a -D "$f" 2>/dev/null | grep -cE 'caml_|ghczmprim|_gfortran_|kfun:|_vinit|cob_init')"
        echo "strings runtime-cue literals: $(strings -a "$f" | grep -cE 'caml_|ghczmprim|_gfortran_|kfun:|_vinit|cob_init')";;
  *"compiled Java class"*) t=$(mktemp -d)/X.class; cp "$f" "$t"
        echo "javap Lkotlin/Metadata; refs: $(javap -v "$t" 2>/dev/null | grep -c 'Lkotlin/Metadata;')";;
  *Mono/.Net*) python3 -c "import dnfile,sys; p=dnfile.dnPE(sys.argv[1]); print('assembly refs:', sorted(str(r.Name) for r in p.net.mdtables.AssemblyRef))" "$f";;
  *WebAssembly*) wasm-objdump -h "$f" | grep -E 'Custom|producers' || echo "no custom/producers section";;
  Zip*) unzip -l "$f" | tail -n +4 | grep -c '\.class$' | sed 's/^/class entries: /';;
esac
