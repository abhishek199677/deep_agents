#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Deep Agents — Production Deployment Script
# Target: Cloud VM with Docker Compose + Let's Encrypt SSL
# =============================================================================

if [ $# -lt 1 ]; then
    echo "Usage: ./scripts/deploy.sh <domain>"
    echo "  domain: your production domain (e.g., agents.yourcompany.com)"
    exit 1
fi

DOMAIN="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Deploying Deep Agents to $DOMAIN"
echo ""

# ─── 1. Validate environment ──────────────────────────────────────────────
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "❌ OPENAI_API_KEY is not set"
    echo "   Set it with: export OPENAI_API_KEY='sk-...'"
    exit 1
fi

if [ -z "${JWT_SECRET:-}" ]; then
    echo "❌ JWT_SECRET is not set"
    echo "   Generate one with: export JWT_SECRET=\$(openssl rand -hex 32)"
    exit 1
fi

if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    echo "❌ POSTGRES_PASSWORD is not set"
    echo "   Set it with: export POSTGRES_PASSWORD='<strong-password>'"
    exit 1
fi

# ─── 2. Set up SSL certificates ───────────────────────────────────────────
echo "📜 Obtaining SSL certificate for $DOMAIN..."
mkdir -p "$SCRIPT_DIR/certs"

if [ ! -f "$SCRIPT_DIR/certs/cert.pem" ]; then
    docker run --rm -it \
        -v "$SCRIPT_DIR/certs:/etc/letsencrypt" \
        -p 80:80 \
        certbot/certbot certonly --standalone \
        -d "$DOMAIN" \
        --non-interactive --agree-tos \
        --email "admin@$DOMAIN" || true

    # Symlink for nginx
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        ln -sf "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SCRIPT_DIR/certs/cert.pem"
        ln -sf "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SCRIPT_DIR/certs/key.pem"
    fi
else
    echo "   SSL certificates already exist"
fi

# ─── 3. Export environment ────────────────────────────────────────────────
export DOMAIN
export CORS_ORIGINS="https://$DOMAIN"
export APP_ENV=production

# ─── 4. Pull latest and restart ───────────────────────────────────────────
echo "🐳 Building and starting Docker stack..."
cd "$SCRIPT_DIR"
docker compose build --pull
docker compose up -d

echo ""
echo "✅ Deployment complete!"
echo "   https://$DOMAIN"
echo ""
echo "📋 Useful commands:"
echo "   docker compose logs -f    # View logs"
echo "   docker compose ps          # Check status"
echo "   ./scripts/deploy.sh        # Re-deploy"
