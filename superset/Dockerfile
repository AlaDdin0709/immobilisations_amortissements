FROM apache/superset:3.1.0

# Install PyMySQL as root so Superset can connect to MySQL databases
USER root
RUN pip install --no-cache-dir pymysql && \
    apt-get update && \
    apt-get install -y --no-install-recommends unzip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the image's unprivileged user
USER superset
# Respect 12-factor: do not embed secrets at build time. Copy runtime config that reads env vars.
COPY superset_config.py /app/pythonpath/superset_config.py
# Set init script executable at copy time
COPY --chmod=0755 init-superset.sh /app/init-superset.sh
COPY --chmod=0755 init-superset.sh /app/docker/docker-init.sh
CMD ["/app/init-superset.sh"]
