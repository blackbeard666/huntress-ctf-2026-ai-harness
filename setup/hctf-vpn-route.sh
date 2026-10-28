#!/bin/sh
# Pin the Homebase /32 to the MAIN tunnel (D28 post-mortem #18). Called by the hctf-vpn unit twice: as OpenVPN's
# --route-up script (after every (re)connect's routes, env $dev = our tun device) and from ExecStartPost (backup).
#
# Why: main tun0 and the rehearsal copy's tun1 both sit in 10.200.0.0/16. The server pushes `10.1.0.0/16 via 10.200.0.1`;
# the kernel resolves that gateway through whichever 10.200.0.0/16 connected route comes first -- tun1 when the rehearsal copy's
# tunnel is up -- so 10.1.50.243 (main's Homebase) left via tun1 and every reconnect undid the manual fix. A /32 on our
# device wins over the /16 regardless of which tunnel the /16 bound to.
#
# usage: hctf-vpn-route.sh [dev]     (dev: $1, else OpenVPN's $dev, else tun0). Always exits 0 (never fails the unit).
HB="${HCTF_HB_HOST:-10.1.50.243}"
DEV="${1:-${dev:-tun0}}"
IP="${HCTF_IP_BIN:-/sbin/ip}"
[ -x "$IP" ] || IP=ip
# ExecStartPost runs while OpenVPN is still connecting: wait (<= 25 s) for the device to carry its IPv4 address
i=0
while [ "$i" -lt 25 ]; do
  "$IP" -4 addr show dev "$DEV" 2>/dev/null | grep -q 'inet ' && break
  i=$((i + 1))
  sleep 1
done
if "$IP" route replace "$HB/32" dev "$DEV" 2>/dev/null; then
  echo "hctf-vpn-route: $HB/32 -> $DEV"
else
  echo "hctf-vpn-route: could not pin $HB/32 to $DEV (device not up?)" >&2
fi
exit 0
