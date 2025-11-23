#!/usr/bin/env bash
set -e

# Script d'initialisation minimal pour Superset (placeholder)
# Il est recommandé d'adapter selon la doc officielle: https://superset.apache.org/docs/installation/installing-superset-using-docker

# Enforce 12-factor: admin credentials must be provided via environment variables
if [ -z "${SUPERSET_ADMIN_USER:-}" ] || [ -z "${SUPERSET_ADMIN_PASSWORD:-}" ]; then
	echo "ERROR: SUPERSET_ADMIN_USER and SUPERSET_ADMIN_PASSWORD must be set in the environment."
	echo "Please add them to your .env or pass them to the container. Example:"
	echo "  SUPERSET_ADMIN_USER=admin"
	echo "  SUPERSET_ADMIN_PASSWORD=changeme"
	exit 1
fi

# Apply DB migrations
superset db upgrade
export FLASK_APP=superset

# Create admin user only if it does not already exist (idempotent)
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

# Initialize Superset
superset init

# Keep the container running
gunicorn --bind 0.0.0.0:8088 "superset.app:create_app()"
