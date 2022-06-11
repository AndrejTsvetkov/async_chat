#!/bin/sh

set -e

python app/wait_for_redis.py
make app
