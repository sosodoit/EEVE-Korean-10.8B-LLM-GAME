#!/bin/bash
set -e

echo "=== LLaMA3 모델 다운로드 중 ==="
export OLLAMA_MODE=noninteractive
ollama pull llama3

echo "LLaMA3 모델 설치 완료!"
