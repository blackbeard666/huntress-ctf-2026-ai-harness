# Huntress advanced Bash syntax fixture

readonly Material_7373f48c='dj0xfGZlYXR1cmU9Z2V0b3B0c19zdGF0ZXxwcmltaXRpdmU9b3B0aW9uX3BhcnNlcl9zdGF0ZXxjYW1wYWlnbl9pZD1CQVNIWC1CNkQ1RTFCNnxzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'

readonly Codec_7373f48c='base64_literal|'

Feature_7373f48c() {

  local OPTIND option; while getopts ':ab:' option -- -a -b fixture; do case "$option" in a|b) : ;; esac; done

}

Decode() { printf '%s' "${Material_7373f48c}" | base64 --decode; }

Inspect_7373f48c() {

  local -a compass=(north south); local n="${compass[*]}"

  local p=0; while ((p++ < 1)); do Decode; done

}

if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_7373f48c; fi

