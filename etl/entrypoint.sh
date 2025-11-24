#!/usr/bin/env bash
set -e

# Entrypoint pour exécuter l'ETL puis exit (design: ETL batch au démarrage)
# Use exec so Python becomes PID 1 (proper signal handling) and forward any args.
if [ "$#" -gt 0 ]; then
	exec python -u "$@"
else
	exec python -u src/main.py
fi
