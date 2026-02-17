# Color codes
PURPLE="\[\033[1;35m\]"
GREEN="\[\033[1;32m\]"
CYAN="\[\033[1;36m\]"
YELLOW="\[\033[1;33m\]"
RED="\[\033[1;31m\]"
RESET="\[\033[0m\]"

# Kessel heartbeat (static)
kessel_heartbeat() {
    if [[ -f "$HOME/rayrock/manifesto.bin" ]]; then
        echo -ne "${CYAN}■${RESET}"
    else
        echo -ne "${RED}■${RESET}"
    fi
}

# Git branch (optional)
git_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null
}

# PS1 prompt
export PS1="${PURPLE}[Rayrock Kessel Flow] ${GREEN}\w ${YELLOW}\$(git_branch) ${CYAN}\$(kessel_heartbeat) ${RESET}\n$ "
