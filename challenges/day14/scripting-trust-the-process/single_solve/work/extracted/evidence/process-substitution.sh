  # Huntress advanced Bash syntax fixture
  readonly Material_19563221='dj0xfGZlYXR1cmU9cHJvY2Vzc19zdWJzdGl0dXRpb258cHJpbWl0aXZlPXByb2Nlc3Nfc3Vic3RpdHV0aW9uX3JlYWRlcnxjYW1wYWlnbl9pZD1CQVNIWC1GMUJEOEQwQXxzdGFnZV9jb3VudD0xfHN0ZXBzPXJlY29nbml6ZV9zeW50YXgscmVjb25zdHJ1Y3RfaW50ZW50'
  readonly Codec_19563221='base64_literal|'
  Feature_19563221() {
    local value; while read -r value; do : "$value"; done < <(printf '%s\n' fixture)
  }
  Decode() { printf '%s' "${Material_19563221}" | base64 --decode; }
  Inspect_19563221() {
    local NeUtRaL; if ((2 > 1)); then NeUtRaL=left; else NeUtRaL=right; fi
    local PaSs=0; while ((PaSs++ < 1)); do Decode; done
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_19563221; fi
