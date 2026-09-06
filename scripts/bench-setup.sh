#!/usr/bin/env bash
# ============================================================
# KNC — one-command bench with the full locked stack
#   Frappe v15 · ERPNext · Payments · Telephony · Helpdesk ·
#   Builder · Drive · knc (custom) — installed and seeded.
#
# Prereqs: bench CLI, MariaDB, Redis, Node 18+, yarn, Python 3.10-3.12
#   macOS: `brew install libmagic` (Drive needs it at runtime).
#   (see https://docs.frappe.io/framework/user/en/installation)
#
# IMPORTANT: the bench path must NOT contain spaces — bench splits
#   commands on whitespace and breaks. Run this from a space-free path.
#
# Usage:
#   DB_ROOT_PASSWORD=yourpw ./bench-setup.sh [site-name]
#     # default site: knc.localhost
# ============================================================
set -euo pipefail

SITE="${1:-knc.localhost}"
BENCH_DIR="knc-bench"
KNC_APP_PATH="$(cd "$(dirname "$0")/knc" && pwd)"
PY="${PYTHON:-/opt/homebrew/bin/python3.11}"   # Frappe v15 needs 3.10-3.12

# Idempotent install: skip if already on the site, surface real errors.
app_installed () { bench --site "$SITE" list-apps 2>/dev/null | grep -qE "^$1[[:space:]]"; }
ensure_app ()   { app_installed "$1" || bench --site "$SITE" install-app "$1"; }

echo "==> 1/7 Initialising bench (frappe v15, python $PY)"
if [ ! -d "$BENCH_DIR" ]; then
  bench init "$BENCH_DIR" --frappe-branch version-15 --python "$PY"
fi
cd "$BENCH_DIR"

echo "==> 2/7 Fetching apps (branches pinned to v15-compatible)"
# telephony before helpdesk — helpdesk imports it as a required app.
[ -d apps/erpnext ]   || bench get-app erpnext   --branch version-15
[ -d apps/payments ]  || bench get-app payments  --branch version-15
[ -d apps/telephony ] || bench get-app telephony            # only ships 'develop'
[ -d apps/builder ]   || bench get-app builder   --branch master
[ -d apps/helpdesk ]  || bench get-app helpdesk  --branch main
[ -d apps/drive ]     || bench get-app drive     --branch main
# knc is a local, non-git app → wire it in as an editable symlink
# (bench get-app can't consume a plain local folder). Source must be at a
# space-free path for the editable pip install to resolve.
if [ ! -e apps/knc ]; then
  ln -sfn "$KNC_APP_PATH" apps/knc
  ./env/bin/python -m pip install -e apps/knc
  grep -qx knc sites/apps.txt || echo knc >> sites/apps.txt
fi

echo "==> 3/7 Creating site: $SITE"
if [ ! -d "sites/$SITE" ]; then
  bench new-site "$SITE" \
    --admin-password admin \
    --db-root-password "${DB_ROOT_PASSWORD:-root}"
fi

echo "==> 4/7 Installing the ERPNext stack (knc comes after setup)"
for app in erpnext payments telephony helpdesk builder drive; do
  ensure_app "$app"
done

echo "==> 5/7 ERPNext setup wizard (creates Company + masters)"
# knc's seed needs Item Groups / UOMs / Price Lists, which only
# exist once the wizard has run. `bench execute` prints the return value
# only when truthy, so an empty result == no Company yet == run the wizard.
# Assign to a var first — nested quotes inside `[ "$(...)" ]` break the test.
YEAR="$(date +%Y)"
EXISTING_COMPANY="$(bench --site "$SITE" execute frappe.db.get_value --kwargs "{'doctype': 'Company', 'filters': {}, 'fieldname': 'name'}" 2>/dev/null | tail -1)"
if [ -z "$EXISTING_COMPANY" ]; then
  bench --site "$SITE" execute \
    frappe.desk.page.setup_wizard.setup_wizard.setup_complete \
    --kwargs "{'args': {'currency': 'USD', 'full_name': 'Administrator', 'company_name': 'KNC', 'company_abbr': 'RP', 'industry': 'Services', 'country': 'United States', 'timezone': 'America/New_York', 'language': 'english', 'chart_of_accounts': 'Standard', 'fy_start_date': '${YEAR}-01-01', 'fy_end_date': '${YEAR}-12-31', 'company_tagline': 'Brand identity in ten days', 'email': 'admin@knc.localhost', 'password': 'admin'}}"
fi

echo "==> 6/7 Installing knc (runs after_install seed)"
ensure_app knc

echo "==> 7/7 Migrate + build"
bench --site "$SITE" migrate
bench build

cat <<EOF

============================================================
 Done. Start the bench:   cd $BENCH_DIR && bench start
 Site:                    http://$SITE:8000
 Login:                   Administrator / admin
 Company:                 KNC (USD) — change in the wizard/UI if needed

 Next steps (manual, one-time):
 1. Payments: create Stripe Settings + Payment Gateway Account,
    then select it in KNC Settings → Payment Gateway Account
 2. Builder: design /start wizard + /portal pages
    (paste scripts from builder-kit/, see builder-kit/README.md)
 3. Email: support@ inbound -> Helpdesk; no-reply outbound
 4. KNC Integration Settings: add Friday as a subscriber when ready
============================================================
EOF
