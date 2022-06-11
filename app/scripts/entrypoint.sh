#!/bin/sh

set -e

python app/wait_for_redis.py
uvicorn app.main:app --host=0.0.0.0 --port=8000
