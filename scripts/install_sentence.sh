#!/bin/bash
set -e

echo "=== Hugging Face CLI 설치 ==="
pip install --user huggingface-hub
export PATH="$HOME/.local/bin:$PATH"

echo "=== SentenceTransformer 모델 파일 다운로드 ==="
mkdir -p ./models/all-MiniLM-L6-v2

# Hugging Face 환경변수 설정 (토큰 추가 시 여기에)
export HF_HUB_DISABLE_PROGRESS_BARS=1

/usr/local/bin/hf download sentence-transformers/all-MiniLM-L6-v2 \
  --repo-type model \
  --local-dir ./models/all-MiniLM-L6-v2 \
  --force-download \
  --quiet

echo "=== 모델 파일 다운로드 완료 ==="
ls -l ./models/all-MiniLM-L6-v2

echo "=== SentenceTransformer 로컬 로드 테스트 ==="
python - <<'EOF'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("./models/all-MiniLM-L6-v2")
print("모델 로드 성공", type(model))
EOF

echo "SentenceTransformer(all-MiniLM-L6-v2) 설치 완료!"