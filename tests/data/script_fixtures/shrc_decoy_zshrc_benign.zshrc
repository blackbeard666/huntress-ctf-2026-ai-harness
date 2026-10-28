# ~/.zshrc
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="agnoster"
plugins=(git docker kubectl)
source $ZSH/oh-my-zsh.sh
autoload -Uz add-zsh-hook
autoload -Uz compinit && compinit
_title_precmd() {
  local GIT_HEAD="4b825dc642cb6eb9a060e54bf8d69288fbee4904"
  print -Pn "\e]0;%n@%m: %~\a"
}
add-zsh-hook precmd _title_precmd
alias ll='ls -lah'
alias gst='git status'
