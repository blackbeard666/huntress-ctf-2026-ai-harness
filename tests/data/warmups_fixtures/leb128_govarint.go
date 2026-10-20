// varint hex writer: go run main.go {uvarint|varint} {cp|utf16} {hex|hex-space} < plain
package main

import (
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"strings"
	"unicode/utf16"
)

func main() {
	in, _ := io.ReadAll(os.Stdin)
	var vals []int64
	if os.Args[2] == "utf16" {
		for _, u := range utf16.Encode([]rune(string(in))) {
			vals = append(vals, int64(u))
		}
	} else {
		for _, r := range string(in) {
			vals = append(vals, int64(r))
		}
	}
	var b []byte
	for _, v := range vals {
		if os.Args[1] == "varint" {
			b = binary.AppendVarint(b, v)
		} else {
			b = binary.AppendUvarint(b, uint64(v))
		}
	}
	if os.Args[3] == "hex" {
		fmt.Print(hex.EncodeToString(b))
	} else {
		parts := make([]string, len(b))
		for i, x := range b {
			parts[i] = fmt.Sprintf("%02x", x)
		}
		fmt.Print(strings.Join(parts, " "))
	}
}
