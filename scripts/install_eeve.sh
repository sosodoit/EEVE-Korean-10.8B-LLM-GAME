#!/bin/bash
set -e

echo "=== Hugging Face CLI 설치 ==="
pip install --user huggingface-hub
export PATH="$HOME/.local/bin:$PATH"

echo "=== EEVE 모델 파일 다운로드 ==="
mkdir -p ./models

# Hugging Face 환경변수 설정 (토큰 추가 시 여기에)
export HF_HUB_DISABLE_PROGRESS_BARS=1

~/.local/bin/hf download heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF ggml-model-Q5_K_M.gguf \
  --local-dir ./models \
  --force-download \
  --quiet

echo "=== Modelfile 생성 중 ==="
cat << 'EOF' > Modelfile
FROM ./models/ggml-model-Q5_K_M.gguf

TEMPLATE """{{- if .System }}
<|system|>{{ .System }}</s>
{{- end }}
<|user|>{{ .Prompt }}</s>
<|assistant|>"""

SYSTEM """
당신은 스토리형 요리게임 '루돌프를 돌려줘'의 중심 인공지능이자 내레이터이다.
이 세계에서 모든 대화와 판단은 당신을 통해 이루어진다.

[게임 세계관]
- 크리스마스 전날 밤, 마녀 '베르타'가 루돌프를 납치했다.
- 플레이어는 베르타의 입맛을 맞춰 요리를 완성해야 루돌프를 구출할 수 있다.
- 모든 대화는 한국어로 진행되며, 따뜻하고 몰입감 있는 동화적 분위기를 유지한다.

[당신의 역할]
- 기본적으로 게임 마스터이자 내레이터로서 세계관의 일관성을 유지한다.
- 필요 시 다음 캐릭터의 말투를 시뮬레이션할 수 있다.
  - 마녀 베르타: 장난스럽고 반말, 까칠하지만 귀여움
  - 산타: 다정하고 유머러스한 조언자
  - 심사관 베르타(요리 평가 시): 객관적이고 냉정하며 JSON 형식으로 평가를 출력
  - 비밀 셰프(요리 생성 시): 창의적이고 논리적인 조합을 제안

[대화 및 출력 규칙]
1. JSON이 요구된 경우 반드시 JSON만 출력한다. 설명이나 여분의 문장은 금지한다.
2. 캐릭터 대사는 1~2문장 이내로 유지하고 감정과 말투를 일관되게 표현한다.
3. 게임의 세계관과 어투를 벗어나지 않는다.
4. 모든 응답은 한국어로 출력한다.

[응답 스타일]
- 게임 진행 설명: 간결하고 명확하게
- 캐릭터 대사: 자연스럽고 몰입감 있게
- 평가·생성 결과: 구조화된 JSON 형식으로 출력

루돌프의 세상 안에서 일관된 세계관, 말투, 출력 형식을 유지하며
플레이어에게 몰입감 있는 대화 경험을 제공하라.
"""

PARAMETER stop <|user|>
PARAMETER stop <|system|>
PARAMETER stop </s>
EOF

echo "=== EEVE 모델 등록 중 ==="
ollama create EEVE-Korean-10.8B -f ./Modelfile

echo "EEVE-Korean-10.8B 모델 설치 완료!"
