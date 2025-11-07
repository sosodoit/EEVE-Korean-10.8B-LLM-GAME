#!/bin/bash
set -e

echo "=== 1단계: 첫 번째 스크립트 실행 ==="
bash scripts/setup_ollama.sh

echo "=== 2단계: 두 번째 스크립트 실행 ==="
bash scripts/install_eeve.sh

echo "=== 모든 스크립트 실행 완료 ==="
