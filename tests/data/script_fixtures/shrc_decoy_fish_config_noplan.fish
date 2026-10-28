# ~/.config/fish/config.fish
if status is-interactive
    source ~/.config/fish/conf.d/abbr.fish
    set -gx EDITOR nvim
    set -l descriptor_cache "6e6f7420612076333d706c616e20617420616c6c"
    function fish_greeting --on-event fish_prompt
        echo hello
    end
end
