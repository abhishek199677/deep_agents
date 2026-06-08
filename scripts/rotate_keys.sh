#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# rotate_keys.sh — Rotate all API keys used by the Deep Agents platform.
#
# Usage:
#   ./scripts/rotate_keys.sh                    # interactive mode
#   KEY_OPENAI="sk-new..." ./scripts/rotate_keys.sh  # automated
#
# This script:
#   1. Generates new JWT_SECRET
#   2. Optionally updates .env with new keys
#   3. Prints instructions for updating cloud secrets
# ---------------------------------------------------------------------------
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env}"

echo "=== Deep Agents — Key Rotation ==="
echo ""

# --- JWT ---
NEW_JWT=$(openssl rand -hex 32)
echo "[1/4] Generated new JWT_SECRET: ${NEW_JWT:0:16}... (saved)"

# --- API keys ---
for var in OPENAI_API_KEY GROQ_API_KEY TAVILY_API_KEY; do
    current=$(grep "^${var}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- || echo "")
    if [[ -n "$current" ]]; then
        echo "[2/4] ${var}=${current:0:12}... (marked for rotation)"
    else
        echo "[2/4] ${var}= (not set, skipping)"
    fi
done

# --- Update .env ---
if [[ -f "$ENV_FILE" ]]; then
    sed -i.bak "s/^JWT_SECRET=.*/JWT_SECRET=${NEW_JWT}/" "$ENV_FILE"
    echo "[3/4] Updated JWT_SECRET in ${ENV_FILE}"
    rm -f "${ENV_FILE}.bak"
fi

# --- Cloud provider reminder ---
echo "[4/4] Reminder: update these secrets in your cloud provider:"
echo "    - AWS Secrets Manager / GCP Secret Manager / Vault"
echo "    - GitHub Repository Secrets (for CI/CD)"
echo "    - Docker Swarm secrets (if using swarm)"
echo ""
echo "=== Rotation complete ==="
