#!/usr/bin/env bash
set -eu
cd "$(git rev-parse --show-toplevel)"
source .maintain/python.sh
"$COURSE_PYTHON" .maintain/check-course.py
