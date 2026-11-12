#!/usr/bin/env bash
cd "$(dirname "$0")/R4"
export PYTHONPATH="$PWD/../mujoco-python:$PWD"
exec python3 "$@"
