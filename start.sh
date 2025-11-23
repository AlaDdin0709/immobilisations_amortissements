#!/usr/bin/env bash
set -e

if [ ! -f .env ]; then
  echo "Please copy .env.example to .env and edit it first."
  exit 1
fi

docker-compose up --build
