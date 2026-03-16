#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_BASE=(docker compose)
if [[ -f "docker-compose.prod.yml" ]]; then
  HAS_PROD=1
else
  HAS_PROD=0
fi

profiles=()
use_prod=0
selected_action=""

print_header() {
  printf "\n=========================================\n"
  printf "      TFG Chatbot Compose Launcher      \n"
  printf "=========================================\n"
}

ask_yes_no() {
  local prompt="$1"
  local default="$2"
  local answer

  while true; do
    if [[ "$default" == "y" ]]; then
      read -r -p "$prompt [Y/n]: " answer || true
      answer="${answer:-y}"
    else
      read -r -p "$prompt [y/N]: " answer || true
      answer="${answer:-n}"
    fi

    case "${answer,,}" in
      y|yes) return 0 ;;
      n|no) return 1 ;;
      *) echo "Please answer y or n." ;;
    esac
  done
}

select_mode() {
  if [[ "$HAS_PROD" -eq 0 ]]; then
    use_prod=0
    return
  fi

  echo
  echo "Select compose mode:"
  echo "1) Dev (docker-compose.yml)"
  echo "2) Prod-like (docker-compose.yml + docker-compose.prod.yml)"

  while true; do
    read -r -p "Choice [1-2]: " mode || true
    case "$mode" in
      1) use_prod=0; break ;;
      2) use_prod=1; break ;;
      *) echo "Invalid option. Use 1 or 2." ;;
    esac
  done
}

select_profiles() {
  echo
  echo "Optional profiles:"

  if ask_yes_no "Enable observability profile?" "n"; then
    profiles+=("observability")
  fi

  if ask_yes_no "Enable gpu profile?" "n"; then
    profiles+=("gpu")
  fi

  if ask_yes_no "Enable devtools profile (mongo-express)?" "n"; then
    profiles+=("devtools")
  fi
}

select_action() {
  echo
  echo "Choose action:"
  echo "1) Up detached"
  echo "2) Up attached"
  echo "3) Down"
  echo "4) Restart"
  echo "5) Ps"
  echo "6) Logs"

  while true; do
    read -r -p "Choice [1-6]: " action || true
    case "$action" in
      1|2|3|4|5|6)
        selected_action="$action"
        return
        ;;
      *)
        echo "Invalid option. Use 1-6."
        ;;
    esac
  done
}

build_compose_cmd() {
  local cmd=("${COMPOSE_BASE[@]}")

  if [[ "$use_prod" -eq 1 ]]; then
    cmd+=("-f" "docker-compose.yml" "-f" "docker-compose.prod.yml")
  fi

  for p in "${profiles[@]}"; do
    cmd+=("--profile" "$p")
  done

  printf '%s\n' "${cmd[@]}"
}

run_action() {
  local action="$1"
  mapfile -t compose_cmd < <(build_compose_cmd)

  echo
  echo "Resolved command prefix: ${compose_cmd[*]}"

  case "$action" in
    1)
      if ask_yes_no "Build images before starting?" "y"; then
        "${compose_cmd[@]}" up -d --build
      else
        "${compose_cmd[@]}" up -d
      fi
      ;;
    2)
      if ask_yes_no "Build images before starting?" "y"; then
        "${compose_cmd[@]}" up --build
      else
        "${compose_cmd[@]}" up
      fi
      ;;
    3)
      if ask_yes_no "Remove orphans?" "y"; then
        "${compose_cmd[@]}" down --remove-orphans
      else
        "${compose_cmd[@]}" down
      fi
      ;;
    4)
      "${compose_cmd[@]}" down --remove-orphans
      if ask_yes_no "Build images before restarting?" "y"; then
        "${compose_cmd[@]}" up -d --build
      else
        "${compose_cmd[@]}" up -d
      fi
      ;;
    5)
      "${compose_cmd[@]}" ps
      ;;
    6)
      read -r -p "Service name (empty for all): " service || true
      if [[ -n "${service:-}" ]]; then
        "${compose_cmd[@]}" logs -f "$service"
      else
        "${compose_cmd[@]}" logs -f
      fi
      ;;
  esac
}

main() {
  print_header
  select_mode
  select_profiles
  select_action
  run_action "$selected_action"
}

main "$@"
