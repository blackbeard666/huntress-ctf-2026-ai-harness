#!/bin/bash
# usage: bash solvein_oracle.sh <bin> <input>  -> runs the binary natively (prints ACCEPT/REJECT) + readelf FUNC check
cd "$(dirname "$0")"
readelf -sW "$1" 2>/dev/null | awk '$4=="FUNC" && $8=="check"{print "symbol check present"}'
./"$1" "$2"
