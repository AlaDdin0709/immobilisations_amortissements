#!/usr/bin/env bash
set -e

# --- Check environment variables ---
if [ -z "${SUPERSET_ADMIN_USER:-}" ] || [ -z "${SUPERSET_ADMIN_PASSWORD:-}" ]; then
    echo "ERROR: SUPERSET_ADMIN_USER and SUPERSET_ADMIN_PASSWORD must be set."
    exit 1
fi

# --- Apply DB migrations ---
echo "Running database migrations..."
superset db upgrade
export FLASK_APP=superset

# --- Create admin user if not exists ---
if superset fab list-users 2>/dev/null | grep -qi "^${SUPERSET_ADMIN_USER}\b"; then
    echo "Admin user '${SUPERSET_ADMIN_USER}' already exists - skipping creation"
else
    echo "Creating admin user '${SUPERSET_ADMIN_USER}'"
    superset fab create-admin \
        --username "${SUPERSET_ADMIN_USER}" \
        --firstname "Superset" \
        --lastname "Admin" \
        --email "admin@example.com" \
        --password "${SUPERSET_ADMIN_PASSWORD}"
fi

# --- Initialize Superset ---
echo "Initializing Superset..."
superset init

echo "Checking for dashboards to import..."
if [ -d /app/dashboards ]; then
    for zipfile in /app/dashboards/*.zip; do
        [ -f "$zipfile" ] || continue
        echo "Processing dashboard ZIP: $zipfile"

        # Backup original ZIP (only once)
        if [ ! -f "${zipfile}.bak" ]; then
            echo "Backing up $zipfile -> ${zipfile}.bak"
            cp "$zipfile" "${zipfile}.bak"
        fi

        # Patch the database URI inside the ZIP to use current MySQL env 
        echo "Patching DB URI inside ZIP (if present)..."
        python - "$zipfile" <<'PY'
import sys, zipfile, tempfile, os, shutil, re

zip_path = sys.argv[1]
tmpdir = tempfile.mkdtemp()
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        names = z.namelist()
        z.extractall(tmpdir)

    target = None
    for n in names:
        if n.replace('\\','/').endswith('/databases/MySQL.yaml') or n == 'databases/MySQL.yaml':
            target = n
            break
    if target:
        target_path = os.path.join(tmpdir, target)
        with open(target_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        user = os.environ.get('MYSQL_USER','admin')
        pwd = os.environ.get('MYSQL_PASSWORD','admin')
        host = os.environ.get('MYSQL_HOST','mysql')
        port = os.environ.get('MYSQL_PORT','3306')
        db = os.environ.get('MYSQL_DATABASE','paris_immobilisations_db')
        new_uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"
        new_content, n = re.subn(r"sqlalchemy_uri:\\s*.*", f"sqlalchemy_uri: {new_uri}", content)
        if n:
            with open(target_path, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            # recreate zip
            tmp_zip = zip_path + '.tmp'
            with zipfile.ZipFile(tmp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for root, dirs, files in os.walk(tmpdir):
                    for f in files:
                        full = os.path.join(root, f)
                        arc = os.path.relpath(full, tmpdir).replace('\\','/')
                        z.write(full, arc)
            shutil.move(tmp_zip, zip_path)
finally:
    shutil.rmtree(tmpdir)
PY

        # Run import using the admin user so permission checks pass
        echo "Importing: $zipfile"
        superset import_dashboards -p "$zipfile" -u "${SUPERSET_ADMIN_USER:-admin}" 2>&1 | tee /tmp/import_error.log || {
            echo "=== IMPORT FAILED ==="
            cat /tmp/import_error.log
            echo "Continuing without this dashboard..."
        }
    done
    echo "Dashboard import process complete"
else
    echo "No dashboards directory found at /app/dashboards"
fi


# --- Keep container running ---
echo "Starting Superset web server..."
exec gunicorn \
    --bind 0.0.0.0:8088 \
    --timeout 120 \
    --workers 2 \
    "superset.app:create_app()"