import random
import streamlit as st
from pathlib import Path
import pathlib
import base64

def load_css(file_name: str):

    css_path = Path("assets") / file_name
    
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def img_to_base64(path: str) -> str:
    """
    base64로 이미지 변환
    """
    return base64.b64encode(Path(path).read_bytes()).decode()

def render_image(image_path: str, css_class: str = "", width=None, alt=None):
    """
    base64로 변환한 이미지 출력
    - image_path: 이미지 경로
    - css_class: 추가 CSS 클래스
    - width: px 단위 폭 (옵션)
    - alt: 대체 텍스트 (옵션)
    """
    b64_img = img_to_base64(image_path)
    width_attr = f'width="{width}"' if width else ""
    alt_attr = f'alt="{alt}"' if alt else ""
    class_attr = f'class="{css_class}"' if css_class else ""
    
    st.markdown(
        f'<img src="data:image/png;base64,{b64_img}" {width_attr} {alt_attr} {class_attr}>',
        unsafe_allow_html=True
    )