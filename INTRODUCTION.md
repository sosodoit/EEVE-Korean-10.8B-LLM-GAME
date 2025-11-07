## 1. 기획

- [초기스토리노트](docs/STORYNOTE.md)

- **게임 대상**
    - 남녀노소 누구나 쉽게 즐길 수 있는 
    - 직관적 선택, 창의력, 도전 욕구

- **사용자 경험**
    - 선택 결과에 따른 반응과 반복 도전의 재미를 통해 성취감 제공
    - 게임을 했을뿐인데 따뜻한 선물로 이어짐

- **사회적 가치**
    - 성공 시 기부액이 적립되어, 즐거운 플레이 동시에 따뜻한 나눔으로

- **비즈니스 모델**
    - 식당 광고 ↔ 사용자에게는 생성된 요리와 관련된 식당 추천

<br>
<br>

## 2. 게임 배경

- 크리스마스 선물 배달 직전 긴박한 시간대, 눈 덮인 북극 마녀의 마성 그 어딘가….
- 마녀는 루돌프를 납치했고, 플레이어는 제한된 시간 안에 루돌프를 되찾아야 함
- 마녀의 입맛을 만족시키면 루돌프를 돌려줌
- 루돌프의 상태가 게임 진행 상황에 따라 변화

<br>
<br>

## 3. 캐릭터 설정
- 마녀 베르타: 장난꾸러기 소문난 미식가 베르타 `utils.prompts.witch_persona_prompt` `utils.ollama_service.llm_witch_persona`

```python
if level == "하":
    witch_type = "상냥하고 귀엽지만 호기심 많고 알록달록한걸 좋아하는 마녀."
elif level == "중":
    witch_type = "조금 까칠하고 예민하지만 새로운 조합을 좋아하는 마녀."
else:
    witch_type = "거만하고 변덕스러운 미식가 마녀."
```

- 루돌프: 납치된 순록, 시간이 지날수록(3번의 기회) 마녀에게 동화되어감
- 산타: 선물 준비로 바빠서 구출해줄 플레이어 모집, 대신 산타힘으로 원격힌트를 제공하는 조력자
- 플레이어: 루돌프 구출을 위해 마녀의 입맛을 탐색하고 요리를 만들어내는 it's you

<br>
<br>

## 4. 게임 로직
### **요약:** 난이도 선택 → 마녀와 3번 대화 + 재료 보고 요리 설명 3번 시도 → 엔딩

<p align="center">
    <img width="1000" alt="image" src="https://github.com/sosodoit/EEVE-Korean-10.8B-LLM-GAME/blob/main/docs/img/flow.png" />
</p>

<br>
<br>

### **게임 시작:**
    - 루돌프 납치 사건 발생 → 산타의 긴급요청!!
    - 난이도(하·중·상) 선택

<img width="1000" alt="image" src="https://github.com/sosodoit/EEVE-Korean-10.8B-LLM-GAME/blob/main/docs/img/img1.png" />
<br>
<br>

### **요리 미션 시작:**
    - 마녀의 대사를 통해 입맛 단서 추론 (대화 3번 가능) `utils.prompts.ingredients_prompt` `utils.ollama_service.llm_witch_chat`
    - 2/5/10가지 재료 제시 > 주어진 재료를 가지고 정답 요리 생성 `utils.prompts.answer_dish_prompt` `utils.ollama_service.llm_ingredients` `utils.ollama_service.llm_answer_dish`
    - 2/5/10가지 재료 제시 > 선택한 재료 단어가 포함되도록 텍스트 입력으로 요리 생성 
    - 정답요리와 얼마나 유사한지 AI 평가 (난이도와 마녀페르소나 고려한 평가 프롬프팅) `utils.prompts.evaluate_dish_prompt` `utils.ollama_service.ai_evaluate_dish`
    - 산타의 힌트는 3회 사용 가능 `utils.prompts.isanta_hints_prompt` `utils.ollama_service.llm_santa_hints`
    - 정답 제출 3회 시도 가능

<img width="1000" alt="image" src="https://github.com/sosodoit/EEVE-Korean-10.8B-LLM-GAME/blob/main/docs/img/img2.png" />

### **요리 평가 및 엔딩:**
    #기준  
    - 총점 100점 기준 (평가 항목 기반 AI 채점 +  난이도별 `score_limit` 기준)
    - 하: 50점 이상
    - 중: 60점 이상
    - 상: 70점 이상

    #엔딩
    - 루돌프 구출 성공 시 성공 메세지
    - 루돌프 구출 실패 시 실패 메세지

<br>
<br>

## 5. 기술 스택
- `Python` `Ollama (EEVE-10.8B)` `Streamlit`
- LLM Role System: `witch / santa`
- [Miro](https://share.google/dVrQyVoMGk1712PcN) `마인드맵, 다이어그램 등 like figma`

<br>
<br>

## 6. 폴더 구조

```bash
root/
├── app/
│   ├── assets/   
│   ├── utils/                # LLM 서비스 관련
│   │   ├── loader.py
│   │   ├── prompts.py      
│   │   ├── ollama_client.py 
│   │   └── ollama_service.py 
│   └── app.py                # 메인 실행 파일              
├── scripts/                  # RunPod 초기 세팅 스크립트
└── requirements.txt
```

<br>
<br>


## 7. 개선 및 확장 가능성

- **확장 요소**
    - 루돌프 및 마녀 페르소나 확장으로 추가 콘텐츠 가능
    - 사용자 참여형 랭킹 시스템
    - 시즌별 테마 업데이트로 게임 확작성
    - 광고 및 보상형 구조로 수익·기부 연계 (결과 요리 기반 식당 추천)

<br>
<br>

## 8. 개발 과정 및 트러블 슈팅 
- 아래 내용 [블로그](https://blog.naver.com/reo_n_mary)에 작성해볼 예정임다, 방문 환영!! 🫡
``` bash
# Python 패키지 설치
pip install -r requirements.txt

# RunPod 환경 초기 세팅
bash scripts/run_all.sh

# Streamlit 실행
streamlit run app/app.py
```
- runpod + ollama + streamlit 환경 셋팅 과정
- streamlit 연결 거부 사태
- 요리 평가 방식 개선 과정
- 프롬프팅 개선 과정 (주요사례)
    - 모든 응답을 json으로 + 후처리
    - 마녀가 나보고 마녀라고 하는 헛소리 제거 
    - 영어 텍스트 출력 최대한 제어
    - Modelfile 설정 후 프롬프팅 짧게 써도 비슷한 응답 출력
    - [Modelfile의 SYSTEM 프롬프트 설정](docs/MODELFILE.md)
