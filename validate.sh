#!/usr/bin/env bash
set -e

echo "Health checks (basic)"

echo "Checking MySQL port 3306..."
# simple check using nc if available
if command -v nc >/dev/null 2>&1; then
  nc -zv localhost 3306 || echo "MySQL port closed"
else
  echo "Install 'nc' for port checks, or check manually"
fi

echo "Open http://localhost:8501 for Streamlit and http://localhost:8088 for Superset (if started)"
