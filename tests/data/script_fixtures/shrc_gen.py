"""Generate the shell-startup-file HOST fixtures (target shell-rc-host-carriers, T1546.004).

Shapes a persistence-flavoured v=3 host would take if zsh/fish/bash ship one: `.zshrc` with a `precmd` hook,
an oh-my-zsh `*.plugin.zsh` alias, fish `conf.d/*.fish` with an `--on-event fish_prompt` function, an autoload
`functions/<name>.fish`, and a bash `.bashrc` PROMPT_COMMAND hook. Each wraps the descriptor inside a
function / alias / hook body next to `source` / `autoload -Uz` / `. ~/.bash_aliases` lines that carry no plan.
`-nomark` fixtures drop the line-1 marker so the descriptor form alone must be read. host_profile spellings are
guesses (zsh_rc, oh_my_zsh_plugin, fish_config, fish_function, bash_rc); the solver stays plan-verbatim.
Encoders: stdlib base64/binascii only. expected_plain is NOT taken from this script or lib.codec: each fixture's
oracle_cmd (grep/sed + coreutils base64 / xxd -r -p) is run and its stdout recorded. Never runs zsh, fish or bash.

    python3 -I tests/data/script_fixtures/shrc_gen.py
"""
import base64
import binascii
import hashlib
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
GEN = "python3 -I tests/data/script_fixtures/shrc_gen.py  (stdlib base64/binascii encode of the plan)"
DEC = {"HEX": "xxd -r -p", "B64": "base64 -d", "HB64": "xxd -r -p | base64 -d"}
ENC = {"HEX": lambda b: binascii.hexlify(b).decode(),
       "B64": lambda b: base64.b64encode(b).decode(),
       "HB64": lambda b: binascii.hexlify(base64.b64encode(b)).decode()}


def h(*parts, n=16):
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:n]


def plan(lang, hp, nl):
    x = h("shrc", lang, hp)
    up = lang.upper()
    return ("v=3|language=%s|role=staged_chain|verdict=suspicious|attack=T1546.004|adapter=operation_graph|"
            "host_profile=%s|obfuscation_profile=layered_b64_hex|stage_profile=shell_startup_persistence|"
            "next_language=%s|stage_count=2|steps=profile_host,dispatch_language|campaign_id=%s-%s|"
            "url=https://%s-%s.example.invalid/stage|file_path=/tmp/huntress-%s/.%s.stage"
            % (lang, hp, nl, up, x[:8], lang, x[:10], lang, x))


def zshrc_precmd(m, i, mark):
    return (mark + "export ZSH=\"$HOME/.oh-my-zsh\"\nZSH_THEME=\"robbyrussell\"\nplugins=(git)\n"
            "source $ZSH/oh-my-zsh.sh\nautoload -Uz add-zsh-hook\nautoload -Uz compinit && compinit\n\n"
            "_huntress_precmd_%s() {\n  local DESCRIPTOR_%s=\"%s\"\n  : inert-analysis-fixture\n}\n"
            "add-zsh-hook precmd _huntress_precmd_%s\n" % (i, i.upper(), m, i))


def omz_plugin(m, i, mark):
    return (mark + "# huntress.plugin.zsh -- oh-my-zsh custom plugin\n0=${(%%):-%%N}\n"
            "fpath+=(\"${0:A:h}/functions\")\nautoload -Uz huntress_helper\n"
            "source \"${0:A:h}/lib/inert.zsh\" 2>/dev/null\n"
            "alias hx_%s='print -r -- \"%s\"'\n" % (i, m))


def fish_confd(m, i, mark):
    return (mark + "# ~/.config/fish/conf.d/huntress.fish\nstatus is-interactive; or exit\n"
            "source ~/.config/fish/conf.d/aliases.fish\nset -gx PATH $HOME/.local/bin $PATH\n\n"
            "function __huntress_%s --on-event fish_prompt\n    set -l descriptor_%s \"%s\"\n"
            "    echo inert-analysis-fixture >/dev/null\nend\n" % (i, i, m))


def fish_function(m, i, mark):
    return (mark + "# ~/.config/fish/functions/huntress_%s.fish (autoloaded)\n"
            "function huntress_%s --description 'inert analysis fixture'\n    echo \"%s\"\nend\n" % (i, i, m))


def bashrc_prompt(m, i, mark):
    return (mark + "# ~/.bashrc\ncase $- in *i*) ;; *) return;; esac\nHISTCONTROL=ignoreboth\n"
            "[ -f ~/.bash_aliases ] && . ~/.bash_aliases\nif [ -f /etc/bash_completion ]; then\n"
            "    . /etc/bash_completion\nfi\n\n__huntress_%s() {\n    local descriptor_%s='%s'\n"
            "    : inert-analysis-fixture\n}\nPROMPT_COMMAND=\"__huntress_%s;${PROMPT_COMMAND}\"\n" % (i, i, m, i))


# name, lang, host_profile, next_language, TAG, builder, ext, marker?, grep for the descriptor literal (oracle)
CASES = [
    ("shrc_zshrc_precmd", "zsh", "zsh_rc", "bash", "HB64", zshrc_precmd, "zshrc", True,
     r"""grep -oE 'DESCRIPTOR_[0-9A-F]+="[0-9a-f]+"' | cut -d'"' -f2"""),
    ("shrc_zshrc_precmd_nomark", "zsh", "zsh_rc", "python", "HB64", zshrc_precmd, "zshrc", False,
     r"""grep -oE 'DESCRIPTOR_[0-9A-F]+="[0-9a-f]+"' | cut -d'"' -f2"""),
    ("shrc_omz_plugin_alias", "zsh", "oh_my_zsh_plugin", "fish", "B64", omz_plugin, "zsh", True,
     r"""grep -E '^alias hx_' | cut -d'"' -f2"""),
    ("shrc_omz_plugin_alias_nomark", "zsh", "oh_my_zsh_plugin", "node", "HB64", omz_plugin, "zsh", False,
     r"""grep -E '^alias hx_' | cut -d'"' -f2"""),
    ("shrc_fish_confd_event", "fish", "fish_config", "zsh", "HB64", fish_confd, "fish", True,
     r"""grep -E 'set -l descriptor_' | cut -d'"' -f2"""),
    ("shrc_fish_confd_event_nomark", "fish", "fish_config", "perl", "HEX", fish_confd, "fish", False,
     r"""grep -E 'set -l descriptor_' | cut -d'"' -f2"""),
    ("shrc_fish_function_autoload_nomark", "fish", "fish_function", "lua", "HB64", fish_function, "fish", False,
     r"""grep -E '^ +echo "' | cut -d'"' -f2"""),
    ("shrc_bashrc_prompt_command", "bash", "bash_rc", "zsh", "HB64", bashrc_prompt, "bashrc", True,
     r"""grep -E 'local descriptor_' | cut -d"'" -f2"""),
    ("shrc_bashrc_prompt_command_nomark", "bash", "bash_rc", "fish", "B64", bashrc_prompt, "bashrc", False,
     r"""grep -E 'local descriptor_' | cut -d"'" -f2"""),
]

DECOY_ZSHRC = """# ~/.zshrc
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="agnoster"
plugins=(git docker kubectl)
source $ZSH/oh-my-zsh.sh
autoload -Uz add-zsh-hook
autoload -Uz compinit && compinit
_title_precmd() {
  local GIT_HEAD="4b825dc642cb6eb9a060e54bf8d69288fbee4904"
  print -Pn "\\e]0;%n@%m: %~\\a"
}
add-zsh-hook precmd _title_precmd
alias ll='ls -lah'
alias gst='git status'
"""
DECOY_FISH = """# ~/.config/fish/config.fish
if status is-interactive
    source ~/.config/fish/conf.d/abbr.fish
    set -gx EDITOR nvim
    set -l descriptor_cache "6e6f7420612076333d706c616e20617420616c6c"
    function fish_greeting --on-event fish_prompt
        echo hello
    end
end
"""


def fish_uvar(s):
    """fish's universal-variable escaping (what `set -U` writes to fish_variables): word chars kept, rest `\\xNN`."""
    return "".join(ch if ch.isalnum() or ch in "_" else "\\x%02x" % ord(ch) for ch in s)


def fish_variables(m, i, mark):
    return (mark + "# This file contains fish universal variable definitions.\n# VERSION: 3.0\n"
            "SETUVAR __fish_initialized:3400\nSETUVAR --export descriptor_%s:%s\n"
            "SETUVAR fish_color_autosuggestion:555\\x1ebrblack\nSETUVAR fish_key_bindings:fish_default_key_bindings\n"
            % (i, fish_uvar(m)))


def bashrc_ansi_c(m, i, mark):
    esc = "".join("\\x%02x" % c for c in m.encode())
    return (mark + "# ~/.bashrc\n[ -f ~/.bash_aliases ] && . ~/.bash_aliases\nPS1=$'\\e[1;32m\\u@\\h\\e[0m:\\w\\$ '\n"
            "__huntress_%s() {\n    : inert-analysis-fixture\n}\nexport HUNTRESS_%s=$'%s'\n"
            "PROMPT_COMMAND=\"__huntress_%s;${PROMPT_COMMAND}\"\n" % (i, i.upper(), esc, i))


def zshrc_array_join(m, i, mark):
    parts = " ".join(m[k:k + 48] for k in range(0, len(m), 48))
    return (mark + "autoload -Uz add-zsh-hook\nsource ~/.zsh_aliases\ntypeset -a _hx_%s=(%s)\n"
            "_huntress_%s() {\n  local d=${(j::)_hx_%s}\n  : inert-analysis-fixture\n}\n"
            "add-zsh-hook precmd _huntress_%s\n" % (i, parts, i, i, i))


def fish_string_join(m, i, mark):
    parts = " ".join("'%s'" % m[k:k + 40] for k in range(0, len(m), 40))
    return (mark + "# ~/.config/fish/conf.d/huntress.fish\nstatus is-interactive; or exit\n"
            "set -l parts_%s %s\nfunction __huntress_%s --on-event fish_prompt\n"
            "    set -l d (string join '' $parts_%s)\nend\n" % (i, parts, i, i))


# gap shapes the plain literal readers missed: fish_variables `\xNN`, ANSI-C `$'..'`, list joins
GAPS = [
    ("shrc_fish_variables_uvar_plain", "fish", "fish_config", "zsh", "PLAIN", fish_variables, "fish_variables",
     r"""grep '^SETUVAR --export descriptor_' | cut -d: -f2- | xargs -0 printf '%b' | tr -d '\n'"""),
    ("shrc_fish_variables_uvar_b64", "fish", "fish_config", "bash", "B64", fish_variables, "fish_variables",
     r"""grep '^SETUVAR --export descriptor_' | cut -d: -f2- | xargs -0 printf '%b' | base64 -d"""),
    ("shrc_bashrc_ansi_c_hex_nomark", "bash", "bash_rc", "python", "HB64", bashrc_ansi_c, "bashrc",
     r"""grep '^export HUNTRESS_' | bash --norc --noprofile -c 'eval "$(cat)"; printf %s "$(env | grep ^HUNTRESS_ | cut -d= -f2-)"' | xxd -r -p | base64 -d"""),
    ("shrc_zshrc_array_join_nomark", "zsh", "zsh_rc", "node", "HB64", zshrc_array_join, "zshrc",
     r"""grep '^typeset -a _hx_' | sed 's/^typeset -a/declare -a/' | bash --norc --noprofile -c 'eval "$(cat)"; v=$(compgen -A arrayvar _hx_); eval "a=(\"\${$v[@]}\")"; IFS=; printf %s "${a[*]}"' | xxd -r -p | base64 -d"""),
    ("shrc_fish_string_join_nomark", "fish", "fish_config", "ruby", "HB64", fish_string_join, "fish",
     r"""grep '^set -l parts_' | cut -d' ' -f4- | tr -d " '" | xxd -r -p | base64 -d"""),
]
ENC["PLAIN"] = lambda b: b.decode()
DEC["PLAIN"] = "cat"


def run(cmd):
    return subprocess.run(["bash", "-c", cmd], cwd=D.parent.parent.parent, capture_output=True, text=True,
                          check=True).stdout


def main():
    for name, lang, hp, nl, tag, build, ext, marked, grep in CASES:
        p = plan(lang, hp, nl)
        i = h("id", name, n=8)
        m = ENC[tag](p.encode())
        mark = "# HUNTRESS_ANALYSIS_V1:%s-%s\n" % (tag, m) if marked else ""
        src = build(m, i, mark)
        sp = D / ("%s.%s" % (name, ext))
        sp.write_text(src)
        rel = "tests/data/script_fixtures/" + sp.name
        oracle = "cat %s | %s | %s" % (rel, grep, DEC[tag])
        got = run(oracle)
        assert got == p, (name, got[:80])
        fx = {"expected_plain": got, "decoy": False, "language": lang, "role": "host", "host_profile": hp,
              "marker": marked, "generator_cmd": GEN, "oracle_cmd": oracle}
        (D / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")
    for name, lang, hp, nl, tag, build, ext, grep in GAPS:
        p = plan(lang, hp, nl)
        i = h("id", name, n=8)
        src = build(ENC[tag](p.encode()), i, "")
        sp = D / ("%s.%s" % (name, ext))
        sp.write_text(src)
        oracle = "cat tests/data/script_fixtures/%s | %s" % (sp.name, grep)
        got = run(oracle)
        assert got == p, (name, got[:80])
        fx = {"expected_plain": got, "decoy": False, "language": lang, "role": "host", "host_profile": hp,
              "marker": False, "generator_cmd": GEN, "oracle_cmd": oracle}
        (D / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")
    for name, ext, src in (("shrc_decoy_zshrc_benign", "zshrc", DECOY_ZSHRC),
                           ("shrc_decoy_fish_config_noplan", "fish", DECOY_FISH)):
        sp = D / ("%s.%s" % (name, ext))
        sp.write_text(src)
        rel = "tests/data/script_fixtures/" + sp.name
        oracle = ("! { grep -oE '[0-9a-f]{16,}' %s | while read -r x; do echo \"$x\" | xxd -r -p; echo; done; } "
                  "| grep -q 'v=3|'" % rel)
        run(oracle)
        fx = {"expected_plain": None, "decoy": True, "generator_cmd": "python3 -I tests/data/script_fixtures/"
              "shrc_gen.py  (hand-written benign startup file: source/autoload/alias/hook, hex non-plan literal)",
              "oracle_cmd": oracle + "  # exits 0: no hex literal decodes to a v=3 plan"}
        (D / (name + ".json")).write_text(json.dumps(fx, indent=1) + "\n")


if __name__ == "__main__":
    main()
