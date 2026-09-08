#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 verify_periodicity_proof.py --max-rank 6
python3 check_endpoint_rule.py
python3 verify_research.py --max-rank 5
