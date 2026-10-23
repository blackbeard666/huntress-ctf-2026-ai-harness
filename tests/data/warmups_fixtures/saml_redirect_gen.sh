#!/bin/sh
# Offline generator for saml-redirect-* fixtures. Compressors: gzip(1) (raw deflate = gzip -9n minus its 10-byte header
# and 8-byte trailer), zlib-flate(1) (qpdf, zlib), gzip -9n (gzip). base64(1) coreutils; URL-quoting jq @uri.
# usage: sh saml_redirect_gen.sh <raw|zlib|gzip> <quote|plain>  (plain text on stdin -> encoded value on stdout)
case "$1" in
  raw) gzip -9n | tail -c +11 | head -c -8 ;;
  zlib) zlib-flate -compress ;;
  gzip) gzip -9n ;;
esac | base64 -w0 | if [ "$2" = quote ]; then jq -sRrj @uri; else cat; fi
