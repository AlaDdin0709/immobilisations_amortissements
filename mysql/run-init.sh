set -euo pipefail

MYSQL_HOST=${MYSQL_HOST:-mysql}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-root}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-}
INIT_SQL_PATH=${INIT_SQL_PATH:-/init/init.sql}

echo "Waiting for MySQL at ${MYSQL_HOST}:${MYSQL_PORT}..."
until mysqladmin ping -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" --silent; do
  sleep 1
done

echo "MySQL is up — applying ${INIT_SQL_PATH} (if present)"

if [ -f "${INIT_SQL_PATH}" ]; then
  export MYSQL_PWD="${MYSQL_PASSWORD}"
  mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u "${MYSQL_USER}" < "${INIT_SQL_PATH}" || {
    echo "Warning: mysql client returned non-zero status while applying init.sql" >&2
    exit 1
  }
  echo "Schema initialization applied."
else
  echo "No init.sql found at ${INIT_SQL_PATH}; nothing to do."
fi

echo "db init script finished"
