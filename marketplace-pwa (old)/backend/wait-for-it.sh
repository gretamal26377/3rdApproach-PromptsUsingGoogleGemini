# filepath: .\marketplace-pwa\backend\wait-for-it.sh
#!/usr/bin/env bash
host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Waiting for $host:$port to be available..."
  sleep 2
done

echo "$host:$port is available. Starting the application..."
exec $cmd