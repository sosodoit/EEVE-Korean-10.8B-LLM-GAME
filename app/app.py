import streamlit as st
from pathlib import Path
import json
import time 
import pathlib

from utils.loader import load_css, render_image, img_to_base64
from utils.ollama_service import (
    llm_witch_persona,
    llm_ingredients,
    llm_answer_dish,
    llm_santa_hints,
    llm_witch_chat,
    ai_evaluate_dish,
)

BASE_DIR = pathlib.Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(page_title="루돌프를 돌려줘", layout="wide")


#------------------------------------------------------------#
# 1. 초기 설정
#------------------------------------------------------------#
def init_game(level):
    
    if level == "하":
        score_limit = 50        
        ingredient_cnt = 2
        opportunities = 3

    elif level == "중":
        score_limit = 60         
        ingredient_cnt = 5
        opportunities = 3

    elif level == "상":
        score_limit = 70        
        ingredient_cnt = 10
        opportunities = 3

    else:
        score_limit = 50  
        ingredient_cnt = 2
        opportunities = 3

    persona = llm_witch_persona(level)
    ingredients = llm_ingredients(level, ingredient_cnt)
    answer_dish = llm_answer_dish(level, persona["persona"], llm_ingredients(level, ingredient_cnt)) 
    santa_hints = llm_santa_hints(answer_dish, persona["taste"])  

    st.session_state.update({
        "level": level,
        "score_limit": score_limit,
        "ingredient_cnt": ingredient_cnt,
        "opportunities": opportunities,
        "attempts": 0,
        "witch_persona": persona,
        "ingredients": ingredients,
        "answer_dish": answer_dish,
        "santa_hints": santa_hints,
        "chat_history": [],
        "chat_turns": 0,
        "game_over": False,
        "feedback": "",
        "success": False,
        "score": 0,
        "checked_items": 0,
        "total_items": 20,
        "revealed_hints": [],
        "page": "game",
        "initialized": True,
    })


#------------------------------------------------------------#
# 2. 시작 페이지
#------------------------------------------------------------#
def intro_page():
    css = (ASSETS_DIR / "intro.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="section top-section"><h1>루돌프를 돌려줘</h1></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="rule-section">', unsafe_allow_html=True)
        
        render_image(ASSETS_DIR / "img/flying-witch.png", width=50)
    
        st.markdown(
                """
                크리스마스 전날 밤,<br>
                장난꾸러기 미식가로 소문난 마녀 베르타가 루돌프를 납치했습니다.<br>
                산타는 선물 배달로 너무 바빠요!<br>
                **산타를 대신해 마녀의 입맛을 맞춰 루돌프를 구출해주세요!**
                """,
                unsafe_allow_html=True,
            )

        # 게임 규칙
        st.markdown("### 게임 규칙")
        st.markdown(
            """
            1. **난이도(하·중·상)** 를 선택하세요, 마녀의 입맛이 결정됩니다.  
            2. **제시된 재료**를 보고 요리를 상상해 설명하세요.  
            3. 마녀와의 **대화는 최대 3번**, 그녀의 취향을 눈치채야 합니다.  
            4. **요리 만들기 버튼**을 누르면 마법 항아리가 반응하고, 마녀가 당신의 요리를 **평가**합니다.  
            5. **3번 안에 마녀를 만족시키면 루돌프를 구출**합니다.  
            6. **산타의 힌트**는 최대 3번 사용 가능하고, 잘 활용해보세요! 
            """
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("하", key="easy_btn", use_container_width=True):
                st.session_state["level"] = "하"
                st.rerun()
        with col2:
            if st.button("중", key="normal_btn", use_container_width=True):
                st.session_state["level"] = "중"
                st.rerun()
        with col3:
            if st.button("상", key="hard_btn", use_container_width=True):
                st.session_state["level"] = "상"
                st.rerun()

    if st.session_state["level"]:
        st.success(f"선택된 난이도: {st.session_state['level']}")
        with st.container():
            if st.button("게임 시작", key="start_game_btn", use_container_width=True):
                st.session_state["start_game"] = True
                st.session_state["page"] = "game"
                st.session_state["initialized"] = False
                st.rerun()
    else:
        st.info("난이도를 선택하세요.")




#------------------------------------------------------------#
# 4. 게임 시작
#------------------------------------------------------------#
def game_page():
    css = (ASSETS_DIR / "game.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    # 상단: 남은 시도 + 산타 힌트
    remaining = st.session_state["opportunities"] - st.session_state["attempts"]
    hints = st.session_state["santa_hints"]
    unlocked = bool(st.session_state["revealed_hints"])
    hints_html = "".join(f"<div class='hint-text'>{hints[i]}</div>" for i in st.session_state["revealed_hints"])

    add_col, _, _, _, _ = st.columns([0.3, 1, 0.3, 0.3, 0.3])
    with add_col:
        st.markdown(f"""
            <div class="attempt-bar">
                <b>남은 시도:</b> {remaining}회
            </div>
        """, unsafe_allow_html=True)

    top_col1, _, top_col2, top_col3, top_col4 = st.columns([0.3, 1, 0.3, 0.3, 0.3])
    with top_col1:
        if st.button("다시 시작", key="restart_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "intro"
            st.rerun()
        
    with top_col2:
        if st.button("🎁산타힌트1", disabled=0 in st.session_state["revealed_hints"], use_container_width=True):
            st.session_state["revealed_hints"].append(0)
            st.rerun()
    with top_col3:
        if st.button("🎁산타힌트2", disabled=1 in st.session_state["revealed_hints"], use_container_width=True):
            st.session_state["revealed_hints"].append(1)
            st.rerun()
    with top_col4:
        if st.button("🎁산타힌트3", disabled=2 in st.session_state["revealed_hints"], use_container_width=True):
            st.session_state["revealed_hints"].append(2)
            st.rerun()

    st.markdown(f"""
    <div class="info-card {'unlocked' if unlocked else 'locked'}">
        <div class="info-title">🎅 산타의 힌트</div>
        {hints_html or '<div class="hint-text">힌트를 열어보세요.</div>'}
    </div>
    """, unsafe_allow_html=True)


    left, right = st.columns([1.5, 1.5])

    # 좌측: 마녀 + 대화
    with left:
        st.markdown('<div class="equal-box">', unsafe_allow_html=True)
        render_witch_and_chat()
        st.markdown('</div>', unsafe_allow_html=True)

    # 우측: 루돌프 + 요리공간
    with right:
        st.markdown('<div class="equal-box">', unsafe_allow_html=True)
        render_rudolph_and_cooking()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 최종 결과
    render_result()




#------------------------------------------------------------#
# 5. 마녀 대화
#------------------------------------------------------------#
def render_witch_and_chat():

    # 상태별 마녀 이미지
    if st.session_state.get("success"):
        witch_img = "witch.png"
    elif st.session_state.get("game_over"):
        witch_img = "witch.png"
    else:
        witch_img = "witch.png"

    # 최근 대화 또는 요리 피드백 표시
    if st.session_state["chat_history"]:
        last_msg = st.session_state["chat_history"][-1]["text"]
    elif st.session_state.get("feedback"):
        last_msg = st.session_state["feedback"]
    else:
        last_msg = "어디 요리맛좀 봐볼까?"

    # -------------------------------
    # 마녀 카드 (루돌프 카드 스타일 통일)
    # -------------------------------
    st.markdown(f"""
        <div class="info-card witch-box">
            <div class="info-title">마녀 베르타</div>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{img_to_base64(str(ASSETS_DIR / 'img' / witch_img))}" 
                    class="witch-avatar" width="120">
            </div>
            <div class="hint-text" style="text-align:center;">{last_msg}</div>
        </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 대화창 (스크롤 가능)
    # -------------------------------

    chat_box = st.container(border=True)
    with chat_box:
        for msg in st.session_state["chat_history"]:
            role = "bubble-user" if msg["role"] == "user" else "bubble-witch"
            st.markdown(f"<div class='{role}'>{msg['text']}</div>", unsafe_allow_html=True)

    # -------------------------------
    # 대화 입력창
    # -------------------------------
    turns = st.session_state["chat_turns"]
    if turns < 3 and not st.session_state["game_over"]:
        
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("마녀의 취향 알아내기", placeholder="예: 올챙이알 좋아해?", label_visibility="collapsed")
            send = st.form_submit_button("보내기")
        
        st.caption(f"남은 대화 횟수: {3 - turns}")

        if send and msg:
            st.session_state["chat_history"].append({"role": "user", "text": msg})
            reply = llm_witch_chat(
                st.session_state["level"],
                st.session_state["witch_persona"],
                st.session_state["ingredients"],
                st.session_state["chat_history"],
                msg,
            )
            st.session_state["chat_history"].append({"role": "assistant", "text": reply})
            st.session_state["chat_turns"] += 1
            st.rerun()
            
    else:
        st.info("마녀와의 대화는 최대 3번까지입니다.")


# ------------------------------------------------------------ #
# 요리 공간
# ------------------------------------------------------------ #
def render_cooking_area():
    ingredients = st.session_state["ingredients"]
    if isinstance(ingredients, str):
        ingredients = json.loads(ingredients)

    ing_html = "".join(f"<span class='ingredient-chip'>{i['name']}</span>" for i in ingredients)
    cauldron_b64 = img_to_base64(str(ASSETS_DIR / "img" / "cooking-pot.png"))

    st.markdown(f"""
        <div class="info-card cooking-area">
            <div class="info-title">마녀의 주방</div>
            <div class="ingredient-list">{ing_html}</div>
            <div id="cauldron-box" class="cauldron-box" style="display:none;">
                <img src="data:image/png;base64,{cauldron_b64}" class="cauldron-appear" style="text-align:center; width="160";">
            </div>
        </div>
    """, unsafe_allow_html=True)
    

    user_dish = st.text_area("마녀의 입맛을 사로잡을 요리 설명", height=120, placeholder="예: 달콤한 딸기 시럽을 뿌린 개구리 눈알...")

    # render_image(str(ASSETS_DIR / "img" / "cooking-pot.png"), css_class="result-img", width=200)

    if st.button("요리 만들기", key="cook_btn", use_container_width=True) and not st.session_state["game_over"]:
        if not user_dish.strip():
            st.warning("요리 설명을 입력해주세요.")
            return

        st.markdown("""
            <script>
            const pot = document.getElementById('cauldron-box');
            pot.style.display = 'flex';
            pot.style.justifyContent = 'center';
            pot.style.alignItems = 'center';
            setTimeout(() => { pot.style.display = 'none'; }, 2000);
            </script>
        """, unsafe_allow_html=True)

        time.sleep(2)
        st.session_state["attempts"] += 1
        success, feedback, score, checked_items, total_items = ai_evaluate_dish(
            st.session_state["level"],
            st.session_state["witch_persona"]["persona"],
            user_dish,
            st.session_state["answer_dish"],
            st.session_state["ingredients"],
            st.session_state["score_limit"],
        )

        st.session_state.update({
            "success": success,
            "feedback": feedback,
            "score": score,
            "checked_items": checked_items,
            "total_items": total_items,
            "game_over": success or st.session_state["attempts"] >= st.session_state["opportunities"]
        })



# ------------------------------------------------------------ #
# 루돌프 상태 + 요리 공간
# ------------------------------------------------------------ #
def render_rudolph_and_cooking():

    # 루돌프 상태
    attempts = st.session_state["attempts"]
    if attempts == 0:
        rudolph_img = "rudolph.png"
        text = "루돌프의 코가 밝게 빛납니다."
        sub = "괜찮아, 아직 힘이 남아있어!"

    elif attempts == 1:
        rudolph_img = "rudolph.png"
        text = "루돌프의 코가 희미해졌습니다."
        sub = "조금 어지럽지만 버틸 수 있어..."

    else:
        rudolph_img = "rudolph.png"
        text = "루돌프의 코 빛이 거의 사라졌습니다."
        sub = "오케이 바이..."
        
    st.markdown(f"""
        <div class="info-card rudolph-box">
            <div class="info-title">마녀에게 잡힌 루돌프</div>
            <div style="text-align:center;">
                <img src="data:image/png;base64,{img_to_base64(str(ASSETS_DIR / 'img' / rudolph_img))}" 
                    class="rudolph-status" width="120">
            </div>
            <div class="hint-text" style="text-align:center;">{text}</div>
            <div class="hint-sub" style="text-align:center;">{sub}</div>
        </div>
    """, unsafe_allow_html=True)

    # 요리 공간
    render_cooking_area()




def render_result():
    if not st.session_state["game_over"]:
        return

    st.divider()


    col1, _, col2, _, col3 = st.columns([1, 0.5, 3, 0.5, 1])

    with col1:
        st.markdown(f"**최종 점수:** {st.session_state['score']} / 100")
    
    with col2:
        if st.session_state["success"]:
            st.markdown("<div class='feedback-card success'>😊 베르타: 훌륭해. 루돌프를 데려가도 좋아.</div>", unsafe_allow_html=True)
            
        else:
            st.markdown("<div class='feedback-card fail'>😠 베르타: 아직 멀었어. 다음엔 더 맛있게 만들어보렴.</div>", unsafe_allow_html=True)

    st.markdown("")

    with col3:
        if st.button("다시 시작", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "intro"
            st.rerun()

#------------------------------------------------------------#
# 6. 실행
#------------------------------------------------------------#
if __name__ == "__main__":
    defaults = {
        "level": None, 
        "score_limit": None, 
        "ingredient_cnt": None,
        "witch_persona": None, 
        "ingredients": None, 
        "answer_dish": None,
        "santa_hints": None, 
        "chat_history": [], 
        "chat_turns": 0,
        "game_over": False, 
        "result_message": "", 
        "success": False,
        "feedback": "", 
        "start_game": False, 
        "revealed_hints": [],
        "score": 0, 
        "similarity": 0.0, 
        "match_count": 0,
        "page": "intro", 
        "initialized": False, 
        "cooking": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state["page"] == "game" and not st.session_state["level"]:
        st.session_state["page"] = "intro"

    if st.session_state["page"] == "intro":
        intro_page()
    else:
        if not st.session_state["initialized"]:
            init_game(st.session_state["level"])
            st.session_state["initialized"] = True
        game_page()
