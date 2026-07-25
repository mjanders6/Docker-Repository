#!/bin/bash
set -e

# Fix ownership and permissions
echo "🔧 Fixing permissions..."
find /server -exec chown "${MC_UID}:${MC_GID}" {} + 2>/dev/null || true
chmod +x /server/run.sh 2>/dev/null || true

# Drop privileges and run as MC user
echo "🔧 Dropping to MC user (${MC_UID}:${MC_GID})..."
exec gosu "${MC_UID}:${MC_GID}" bash -c '

cd /server

# -------------------------------
# 1. Copy runtime files (overwrite if exists)
# -------------------------------
echo "🔧 Restoring runtime files from /server/runtime..."
for f in ops.json whitelist.json banned-players.json; do
    if [ -f "/server/runtime/$f" ]; then
        cp -f "/server/runtime/$f" "$f"
    fi
done

# -------------------------------
# 2. Generate server.properties
# -------------------------------
if [ -f /server/config/server.properties.template ]; then
    echo "🔧 Generating server.properties from template..."
    envsubst < /server/config/server.properties.template > server.properties
fi

echo "==== FINAL server.properties ===="
cat server.properties 2>/dev/null || echo "No server.properties yet"
echo "================================="

# -------------------------------
# 3. Accept EULA
# -------------------------------
echo "eula=true" > eula.txt

# -------------------------------
# 4. Start Minecraft
# -------------------------------
echo "🚀 Starting Minecraft server..."
# exec java -Xmx4096M -Xms2048M -jar server.jar nogui
# before step 4, write/update user_jvm_args.txt
echo "-Xmx4096M -Xms2048M" > user_jvm_args.txt
exec ./run.sh nogui
'
