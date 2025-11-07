#-----------------------------------------------------#
# log_game_event       : 평가로그체킹
# call_ollama          : 시스템역할
# llm_witch_persona    : 마녀 생성
# llm_ingredients      : 재료 생성 
# llm_answer_dish      : 정답 요리 생성
# llm_santa_hints      : 산타 힌트 생성
# llm_witch_chat       : 마녀와의 대화
# ai_evaluate_dish     : 마녀의 요리 평가
#-----------------------------------------------------#
import json
import numpy as np
import random
from pathlib import Path
from datetime import datetime
from utils.ollama_client import chat_with_ollama, chat_with_ollama_msg
from utils.prompts import EVALUATION_ITEMS, witch_persona_prompt, ingredients_prompt, answer_dish_prompt, santa_hints_prompt, witch_chat_prompt, evaluate_dish_prompt

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "game_log.txt"



# 평가로그체킹
def log_game_event(data: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"\n[{timestamp}] LOG\n" + json.dumps(data, ensure_ascii=False, indent=2)
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")



# 시스템역할
def call_ollama(model_name: str, prompt: str, role: str):
    """
    캐릭터 역할(role)에 따라 Ollama에 요청
    role: "witch" | "santa" | "chef" | "witch_judge"
    """
    if not isinstance(prompt, str):
        prompt = json.dumps(prompt, ensure_ascii=False)
    messages = [
        {"role": "system", "content": f"role={role}"},
        {"role": "user", "content": prompt},
    ]
    response = chat_with_ollama_msg(model_name, messages)
    return response



# 마녀 생성
def llm_witch_persona(level: str):
    role = "witch"
    if level == "하":
        witch_type = "상냥하고 귀엽지만 호기심 많고 알록달록한걸 좋아하는 마녀."
    elif level == "중":
        witch_type = "조금 까칠하고 예민하지만 새로운 조합을 좋아하는 마녀."
    else:
        witch_type = "거만하고 변덕스러운 미식가 마녀."

    prompt = witch_persona_prompt(level, witch_type)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)
    if response.startswith("```"):
        response = response.strip("`").replace("json", "").strip()

    start, end = response.find("{"), response.rfind("}") + 1
    try:
        result = json.loads(response[start:end])
        persona = result.get("persona", "")
        taste = result.get("taste", "")
    except:
        persona = "변덕스럽고 알록달록한 걸 좋아하는 마녀."
        taste = "괴상한 향과 희귀한 재료를 좋아해."
    return {"persona": persona, "taste": taste}




# 재료 생성
def llm_ingredients(level: str, ingredient_cnt: int):
    role = "chef"
    prompt = ingredients_prompt(level, ingredient_cnt)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)
    if response.startswith("```"):
        response = response.strip("`").replace("json", "").strip()

    start, end = response.find("["), response.rfind("]") + 1
    try:
        ingredients = json.loads(response[start:end])
    except:
        ingredients = [{"name": "감자", "favor": "good", "reason": "부드러워서 좋아해"}]
    return ingredients




# 정답 요리 생성
def llm_answer_dish(level, persona, ingredients):
    role = "chef"
    prompt = answer_dish_prompt(level, persona, ingredients)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)

    if response.startswith("```"):
        response = response.strip("`").replace("json", "").strip()

    start, end = response.find("{"), response.rfind("}") + 1
    clean_json = response[start:end] if start != -1 else response

    try:
        result = json.loads(clean_json)
        answer_dish = result.get("answer_dish", "이상한 요리")
    except json.JSONDecodeError:
        answer_dish = "이상한 요리"

    # 최소 1개 재료 이름 강제 포함 (개선 필요)
    try:
        if isinstance(ingredients, str):
            ing_list = json.loads(ingredients)
        else:
            ing_list = ingredients or []
        names = [i.get("name") for i in ing_list if isinstance(i, dict) and i.get("name")]
        if names and not any(name in answer_dish for name in names):
            answer_dish = f"{names[0]}를 넣은 {answer_dish}"
    except Exception:
        pass

    return answer_dish



# 산타 힌트 생성
def llm_santa_hints(answer_dish, taste):
    role = "santa"
    selected_items = random.sample(EVALUATION_ITEMS, 3)
    prompt = santa_hints_prompt(answer_dish, taste, selected_items)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)

    if response.startswith("```"):
        response = response.strip("`").replace("json", "").strip()

    start, end = response.find("["), response.rfind("]") + 1
    try:
        hints = json.loads(response[start:end])
    except:
        hints = [f"{item}에 어울리는 요리를 생각해봐." for item in selected_items]

    return hints




# 마녀와 대화
def llm_witch_chat(level, persona, ingredients, chat_history, user_msg):
    role = "witch"
    prompt = witch_chat_prompt(level, persona, ingredients, chat_history, user_msg)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)
    return response.strip()




# 요리 평가
def ai_evaluate_dish(level, persona, user_dish, answer_dish, ingredients=None, score_limit=70):
    role = "witch_judge"

    if user_dish.strip() == answer_dish.strip():
        result = {"checked_items": 20, "score": 100, "feedback": "이건 완전히 내가 만든 요리잖아."}
        log_game_event({"판정": "PASS (정답 일치)", "결과": result})
        return True, result["feedback"], 100, 20, 20

    prompt = evaluate_dish_prompt(level, persona, answer_dish, user_dish)
    response = call_ollama("EEVE-Korean-10.8B", prompt, role)

    if response.startswith("```"):
        response = response.strip("`").replace("json", "").strip()

    start, end = response.find("{"), response.rfind("}") + 1
    try:
        result = json.loads(response[start:end])
    except:
        result = {"checked_items": 0, "score": 0, "feedback": "흥, 잘 모르겠네."}

    checked_items = int(result.get("checked_items", 0))
    score = round((checked_items / 20) * 100, 2)
    feedback = result.get("feedback", "흥, 잘 모르겠네.")
    passed = score >= score_limit

    log_game_event({
        "정답 요리": answer_dish,
        "사용자 요리": user_dish,
        "체크 항목": checked_items,
        "점수": score,
        "판정": "PASS" if passed else "FAIL",
        "피드백": feedback
    })
    return passed, feedback, score, checked_items, 20
