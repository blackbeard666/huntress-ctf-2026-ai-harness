#!/bin/sh
# independent dynamic oracle: run the twin under gdb per host model / trigger; break at copy_frame (its memcpy size = $rsi)
for m in workstation analysis sandbox; do for t in 1 0; do
  r=$(env -i HUNTRESS_HOST_MODEL=$m HUNTRESS_TRIGGER_FAULT=$t gdb -q -batch -ex 'break copy_frame' -ex run \
      -ex 'printf "SIZE=%d\n", $rsi' -ex 'bt' "$1" 2>&1 | grep -E "SIZE|^#[0-9]" | sed -E 's/^#[0-9]+ +(0x[0-9a-f]+ in )?([A-Za-z_0-9]+).*/\2/' | tr '\n' ' ')
  echo "$m trigger=$t: ${r:-NOT_REACHED}"
done; done
