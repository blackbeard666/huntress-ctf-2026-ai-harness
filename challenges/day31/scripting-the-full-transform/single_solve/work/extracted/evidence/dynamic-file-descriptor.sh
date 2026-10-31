  # Huntress advanced Bash syntax fixture
  readonly Material_751314ae='034844091310140100071048110c1b14181c162a131c19102a11100616071c05011a070905071c181c011c0310481419191a16140110112a131c19102a11100616071c05011a070916141805141c121b2a1c11483734263d2d58434c40334d4d36340906011412102a161a001b014844090601100506480710161a121b1c0f102a060c1b01140d590710161a1b0601070016012a1c1b01101b01'
  readonly Codec_751314ae='xor_hex|75'
  Feature_751314ae() {
    local descriptor_fd; exec {descriptor_fd}<<<'fixture'; exec {descriptor_fd}<&-
  }
  Decode() { local raw="${Material_751314ae}" index value; for ((index=0; index<${#raw}; index+=2)); do value=$((16#${raw:index:2} ^ 16#75)); printf -v value '\\x%02x' "$value"; printf '%b' "$value"; done; }
  Inspect_751314ae() {
    local -a compass=(north south); local item1="${compass[*]}"
    case 1 in 1) Decode ;; esac
  }
  if [[ ${HUNTRESS_INSPECT_ONLY:-0} == 1 ]]; then Inspect_751314ae; fi
