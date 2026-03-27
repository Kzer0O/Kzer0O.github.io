#!/bin/bash
#
# autopublish.sh - Check HTB API for retired machines and auto-publish full writeups
# Runs via cron, e.g.: 0 */6 * * * /home/parrot/keyll0ger.github.io/scripts/autopublish.sh
#

set -e

SITE_DIR="/home/parrot/keyll0ger.github.io"
POSTS_DIR="$SITE_DIR/content/posts"
LOG_FILE="$SITE_DIR/scripts/autopublish.log"
HTB_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiY2U5MmEwM2NkODJjZTkyMTZmMmNkZTZkNjkwN2U2MWE1MTIyMmNkYmIzNWQwNjI4MDUwNWY4ZGQ4MzQzNjMwYjY2Njc3YjM0NDQ2MjMzYmUiLCJpYXQiOjE3NzQ2MTc5MzUuNTI5MzY0LCJuYmYiOjE3NzQ2MTc5MzUuNTI5MzY2LCJleHAiOjE4MDYxNTM5MzUuNTIyNjg4LCJzdWIiOiI1NDAyNzIiLCJzY29wZXMiOltdfQ.S69zy4jC1FgXuALtV2D3x5f4xdY4_knRnh6c5lJWKBXuF0sSsrtR3AE8k6aAcbUaDsFS0gNvolPE-bJGKMrq92wbHXqrQbgWT7CqQusKKjmmY6hhJ0P_Ish7QBDH8F_v9VbJVaSh71bxzRHQmIvmhIVuDkknvh7ejLDmsKY9Fw7lG1Ukpb4EFn-CFzPXc0924oqZQGjmyGgD-Vf_2moFbmSV3CAA6K2FNxMZTouDAHw-0CTR8n4zNO-0eFTqW4stfHq17O0zsC6gldoj5qes29ATiljCw-6qhYXPEp2-Hl05YKD_2yFzFNziTIpB25bjUD8IqNTnvcELffBPHgwgcB2kyZTP9b9mhMXZHVcILXX7V0t1ysEEbEwjUA2ABcKs8CM5b97tZHfe8iK75dDZnIuw8K3iviCQE8Zz2iqcY1QbA9SUzGcQAwkkY0856lZQiZX7YGEfn8uyQwligdCaY6pF987QCUlbf47A5t26tvGUHvvo7IJBU1qxmpZklm4w4nOnZf6ub55FD8XVvLxywXijqh-EfcrzYVrbJ-R5S4Msz1WqBg-w74Y0mEStTwdkUTIB53OoJV8DxEUzVFRgxUTTiXPZDTY507aR-yFWoUBlw-T7pRDcUW-BOCNfbCGlIeVP9KZU6YizMpx_8ShmSwd_Nmj9qPheQZnFf41qyII"

# Machine name mapping (lowercase -> API name)
declare -A API_NAMES
API_NAMES[cctv]="CCTV"
API_NAMES[conversor]="Conversor"
API_NAMES[kobold]="Kobold"
API_NAMES[nanocorp]="NanoCorp"
API_NAMES[pirate]="Pirate"
API_NAMES[sorcery]="Sorcery"
API_NAMES[wingdata]="WingData"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=== Auto-publish check started ==="

CHANGED=0

for machine in "${!API_NAMES[@]}"; do
    api_name="${API_NAMES[$machine]}"
    writeup="$POSTS_DIR/${machine}.md"
    tips="$POSTS_DIR/${machine}-tips.md"

    # Skip if no draft writeup exists
    if [ ! -f "$writeup" ]; then
        continue
    fi

    # Skip if writeup is already published (not draft)
    if ! grep -q 'draft: true' "$writeup"; then
        continue
    fi

    # Check HTB API for retirement status
    is_retired=$(curl -s -H "Authorization: Bearer $HTB_TOKEN" -H "Accept: application/json" \
        "https://labs.hackthebox.com/api/v4/machine/profile/$api_name" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin).get('info',{}); print('yes' if d.get('retired') else 'no')" 2>/dev/null)

    if [ "$is_retired" = "yes" ]; then
        log "[$machine] Machine retired! Publishing full writeup..."

        # Publish full writeup: draft: true -> draft: false, update date to today
        sed -i 's/draft: true/draft: false/' "$writeup"
        sed -i "s/^date: .*/date: $(date '+%Y-%m-%d')/" "$writeup"

        # Remove tips version (no longer needed)
        if [ -f "$tips" ]; then
            rm "$tips"
            log "[$machine] Tips version removed"
        fi

        # Remove machine from API_NAMES mapping (won't check again)
        log "[$machine] Full writeup published!"
        CHANGED=1
    else
        log "[$machine] Still active, skipping"
    fi
done

# If changes were made, rebuild and deploy
if [ "$CHANGED" -eq 1 ]; then
    log "Changes detected, rebuilding and deploying..."

    cd "$SITE_DIR"

    # Commit changes on main
    git add -A
    git commit -m "Auto-publish: retired machine writeups

Co-Authored-By: autopublish.sh <noreply@keyll0ger.github.io>"
    git push origin main

    # Build Hugo
    git submodule update --init --recursive
    rm -rf public
    hugo --minify

    # Deploy to gh-pages
    cp -r public /tmp/hugo-autopublish
    git checkout gh-pages
    find . -maxdepth 1 ! -name '.git' ! -name '.' ! -name '.nojekyll' -exec rm -rf {} +
    cp -r /tmp/hugo-autopublish/* .
    rm -rf /tmp/hugo-autopublish themes

    git add -A
    git commit -m "Auto-deploy: retired machine writeups published"
    git push origin gh-pages

    git checkout main

    log "Deploy complete!"
else
    log "No changes needed"
fi

log "=== Auto-publish check finished ==="
