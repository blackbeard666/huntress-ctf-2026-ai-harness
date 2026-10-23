// garble_oracle: independent reader (Go stdlib debug/elf + debug/gosym + debug/buildinfo) -> expected_facts JSON.
// garble randomizes the pclntab magic; we record it, then restore the go1.20 magic so debug/gosym can parse.
package main

import (
	"bytes"
	"debug/buildinfo"
	"debug/elf"
	"debug/gosym"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strings"
)

func main() {
	f, err := elf.Open(os.Args[1])
	if err != nil {
		fmt.Println("null")
		return
	}
	s := f.Section(".gopclntab")
	if s == nil {
		fmt.Println("null")
		return
	}
	out := map[string]any{"literals_recovered": "none"}
	ver, path := "none", "none"
	if bi, err := buildinfo.ReadFile(os.Args[1]); err == nil {
		ver = bi.GoVersion
		if bi.Path != "" {
			path = bi.Path
		}
	}
	out["go_version"], out["go_module_path"] = ver, path
	out["buildinfo_stripped"] = fmt.Sprint((ver == "unknown" || ver == "") && path == "none")
	d, _ := s.Data()
	mg := d[:4]
	known := false
	for _, k := range []string{"fbffffff", "faffffff", "f0ffffff", "f1ffffff"} {
		kb, _ := hex.DecodeString(k)
		known = known || bytes.Equal(mg, kb)
	}
	out["pclntab_magic"], out["pclntab_magic_known"], out["has_garble"] = hex.EncodeToString(mg), fmt.Sprint(known), fmt.Sprint(!known)
	nfunc, nfiles := binary.LittleEndian.Uint64(d[8:]), binary.LittleEndian.Uint64(d[16:])
	out["func_count"], out["file_count"] = fmt.Sprint(nfunc), fmt.Sprint(nfiles)
	out["garble_tiny"] = fmt.Sprint(!known && nfiles*4 < nfunc)
	copy(d[:4], []byte{0xf1, 0xff, 0xff, 0xff})
	tab, err := gosym.NewTable(nil, gosym.NewLineTable(d, f.Section(".text").Addr))
	if err != nil {
		fmt.Println("null")
		return
	}
	var mains []string
	lit := 0
	re := regexp.MustCompile(`^[\w/.-]+\.init\.func\d+$`)
	for _, fn := range tab.Funcs {
		if strings.HasPrefix(fn.Name, "main.") {
			mains = append(mains, fn.Name)
		}
		if re.MatchString(fn.Name) {
			lit++
		}
	}
	if mains == nil {
		out["main_functions"] = "none"
	} else {
		out["main_functions"] = mains
	}
	out["literal_closures"] = fmt.Sprint(lit)
	j, _ := json.Marshal(out)
	fmt.Println(string(j))
}
