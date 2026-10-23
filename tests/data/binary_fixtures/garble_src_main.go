package main

import (
	"fmt"
	"os"
)

const beacon = "https://c2.example.invalid/gate.php"

var cfg = "HCFG{id=7;mode=xor;key=0x5a}"

func secretKey() string { return "Sup3rS3cr3tKey!" }

func main() {
	if len(os.Args) > 5 {
		fmt.Println(beacon, secretKey())
	}
	fmt.Println(cfg, "mutex:Global\\garbleMx01")
}
