#!/usr/bin/env bash
# set -euo pipefail: strict mode to catch errors and undefined variables
set -euo pipefail

# wait-for-it.sh - wait for a TCP service to be available before running a command
# Usage: ./wait-for-it.sh host port -- command args...
# Environment variables:
#   WAIT_TIMEOUT  (seconds, default 60)
#   WAIT_INTERVAL (seconds between retries, default 2)

host="$1"
port="$2"
shift 2

if [ "$#" -eq 0 ]; then
  echo "No command specified to run after wait. Usage: $0 host port -- command" >&2
  exit 2
fi

# Timeout and interval
WAIT_TIMEOUT="${WAIT_TIMEOUT:-60}"
WAIT_INTERVAL="${WAIT_INTERVAL:-2}"
# SECONDS is a special bash built-in var that tracks script runtime
# in seconds since it started
end_time=$((SECONDS + WAIT_TIMEOUT))

# Choose probe tool up-front and fail early if none present
if command -v nc >/dev/null 2>&1; then
  PROBE_TOOL=nc
elif command -v bash >/dev/null 2>&1; then
  PROBE_TOOL=bash
elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
  PROBE_TOOL=python
else
  echo "No suitable probing tool found: need nc, bash (with /dev/tcp) or python" >&2
  exit 2
fi

# Probe loop using selected tool
while true; do
  case "$PROBE_TOOL" in
    nc)
      if nc -z "$host" "$port" >/dev/null 2>&1; then break; fi
      ;;
    bash)
      if bash -c "</dev/tcp/${host}/${port}" >/dev/null 2>&1; then break; fi
      ;;
    python)
      PY_BIN="$(command -v python3 || command -v python)"
      if $PY_BIN -c "import socket; s=socket.socket();
        s.settimeout(1); s.connect(('${host}', ${port}));
        s.close()" >/dev/null 2>&1; then break; fi
      ;;
  # esac: Mark end of the case block. Esac is case spelled backwards
  # and it follows shell syntax convention for ending blocks
  # eg: fi for if 
  esac

  # -ge: "greater than or equal to" in shell scripting 
  if [ $SECONDS -ge $end_time ]; then
    echo "Timed out after ${WAIT_TIMEOUT}s waiting for ${host}:${port}" >&2
    exit 1
  fi

  echo "Waiting for ${host}:${port}..."
  sleep "$WAIT_INTERVAL"
done

echo "${host}:${port} is available. Starting the application..."

# Exec the provided command so it becomes PID 1 and receives signals
exec "$@"