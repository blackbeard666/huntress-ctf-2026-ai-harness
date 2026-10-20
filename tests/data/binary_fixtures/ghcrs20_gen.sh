#!/bin/bash
# D20 GHC + RS20 fixtures: the cached GM members (7z, WinZip AE-2 pw "infected"), plus two decoys built with coreutils.
# usage (repo root): bash tests/data/binary_fixtures/ghcrs20_gen.sh
set -euo pipefail
R=challenges/day20/binary-resourceful; O=tests/data/binary_fixtures; T=$(mktemp -d)
7z e -y -pinfected -o"$T" "$R/single_solve/artifacts/latest/evidence.zip" d20--variant-000.elf >/dev/null
7z e -y -pinfected -o"$T" "$R/solver/cases/auto-time_trial-97b7dcda/artifacts/evidence.zip" d20--variant-004.elf >/dev/null
7z e -y -pinfected -o"$T" "$R/solver/cases/auto-mastery-301f436d/artifacts/delivery 1: evidence.zip" 'd20--*.elf' >/dev/null
cp "$T/d20--variant-000.elf" $O/ghcrs20_d20_single_v000.bin
cp "$T/d20--variant-004.elf" $O/ghcrs20_d20_tt_v004.bin
cp "$(ls "$T"/d20--variant-00[5-9].elf | head -1)" $O/ghcrs20_d20_mastery.bin
# decoy 1: one scratch byte flipped (last byte of the file) -> scratch sha256 no longer verifies -> no RS20 facts
cp $O/ghcrs20_d20_single_v000.bin $O/ghcrs20_decoy_badscratch.bin
printf 'X' | dd of=$O/ghcrs20_decoy_badscratch.bin bs=1 seek=$(( $(stat -c %s $O/ghcrs20_decoy_badscratch.bin) - 1 )) conv=notrunc status=none
# decoy 2: truncated to 600000 bytes (section headers, link-info note, gold note and overlay all cut off)
head -c 600000 $O/ghcrs20_d20_single_v000.bin > $O/ghcrs20_decoy_trunc.bin
rm -rf "$T"
