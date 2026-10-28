# ~/.bashrc
case $- in *i*) ;; *) return;; esac
HISTCONTROL=ignoreboth
[ -f ~/.bash_aliases ] && . ~/.bash_aliases
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

__huntress_c57514f0() {
    local descriptor_c57514f0='dj0zfGxhbmd1YWdlPWJhc2h8cm9sZT1zdGFnZWRfY2hhaW58dmVyZGljdD1zdXNwaWNpb3VzfGF0dGFjaz1UMTU0Ni4wMDR8YWRhcHRlcj1vcGVyYXRpb25fZ3JhcGh8aG9zdF9wcm9maWxlPWJhc2hfcmN8b2JmdXNjYXRpb25fcHJvZmlsZT1sYXllcmVkX2I2NF9oZXh8c3RhZ2VfcHJvZmlsZT1zaGVsbF9zdGFydHVwX3BlcnNpc3RlbmNlfG5leHRfbGFuZ3VhZ2U9ZmlzaHxzdGFnZV9jb3VudD0yfHN0ZXBzPXByb2ZpbGVfaG9zdCxkaXNwYXRjaF9sYW5ndWFnZXxjYW1wYWlnbl9pZD1CQVNILTUzYjFkMGFhfHVybD1odHRwczovL2Jhc2gtNTNiMWQwYWFlNy5leGFtcGxlLmludmFsaWQvc3RhZ2V8ZmlsZV9wYXRoPS90bXAvaHVudHJlc3MtYmFzaC8uNTNiMWQwYWFlN2M4ZDY3OC5zdGFnZQ=='
    : inert-analysis-fixture
}
PROMPT_COMMAND="__huntress_c57514f0;${PROMPT_COMMAND}"
