"""
📸 AI 물리 문제 해결사 - Streamlit UI
이미지 기반 물리 문제 분석 및 풀이 (Powered by Gemini)
"""

import streamlit as st
from PIL import Image
import io

from agent import PhysicsSolverAgent

# 페이지 설정
st.set_page_config(
    page_title="📸 AI 물리 문제 해결사",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* 메인 헤더 */
    .main-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.15) 0%, rgba(79, 172, 254, 0.15) 100%);
        border-radius: 24px;
        margin-bottom: 2rem;
        border: 1px solid rgba(233, 69, 96, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e94560 0%, #4facfe 50%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #a0aec0;
        font-size: 1.15rem;
        font-family: 'Outfit', sans-serif;
    }
    
    /* 업로드 영역 */
    .upload-area {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%);
        border: 2px dashed rgba(79, 172, 254, 0.4);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: rgba(79, 172, 254, 0.8);
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15) 0%, rgba(0, 242, 254, 0.15) 100%);
    }
    
    /* 이미지 프리뷰 */
    .image-preview {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(79, 172, 254, 0.3);
    }
    
    /* 결과 영역 */
    .result-area {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.08) 0%, rgba(79, 172, 254, 0.08) 100%);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1.5rem;
        font-family: 'Outfit', sans-serif;
        line-height: 1.8;
    }
    
    .result-header {
        color: #00f2fe;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 사이드바 스타일 */
    .sidebar-section {
        background: rgba(22, 33, 62, 0.9);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(79, 172, 254, 0.2);
    }
    
    .sidebar-title {
        color: #4facfe;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: 'Outfit', sans-serif;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #e94560 0%, #f472b6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.9rem 2rem;
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.4);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input {
        background: rgba(22, 33, 62, 0.9);
        border: 2px solid rgba(79, 172, 254, 0.3);
        border-radius: 12px;
        color: #e8e8e8;
        font-family: 'Outfit', sans-serif;
        padding: 0.8rem 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4facfe;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.2);
    }
    
    /* 텍스트 영역 */
    .stTextArea textarea {
        background: rgba(22, 33, 62, 0.9);
        border: 2px solid rgba(79, 172, 254, 0.3);
        border-radius: 12px;
        color: #e8e8e8;
        font-family: 'Outfit', sans-serif;
    }
    
    /* 파일 업로더 */
    .stFileUploader {
        background: transparent;
    }
    
    .stFileUploader > div {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%);
        border: 2px dashed rgba(79, 172, 254, 0.4);
        border-radius: 16px;
        padding: 1rem;
    }
    
    /* 성공/에러 메시지 */
    .stSuccess {
        background: rgba(0, 200, 150, 0.2);
        border: 1px solid rgba(0, 200, 150, 0.4);
        border-radius: 12px;
    }
    
    .stError {
        background: rgba(233, 69, 96, 0.2);
        border: 1px solid rgba(233, 69, 96, 0.4);
        border-radius: 12px;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(22, 33, 62, 0.5);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a0aec0;
        font-family: 'Outfit', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e94560 0%, #f472b6 100%);
        color: white;
    }
    
    /* 히든 스트림릿 요소 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 마크다운 스타일 */
    .element-container .stMarkdown {
        color: #e8e8e8;
    }
    
    /* 수식 스타일 */
    .katex {
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """세션 상태 초기화"""
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "result" not in st.session_state:
        st.session_state.result = None
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def create_agent(api_key: str) -> bool:
    """에이전트를 생성합니다."""
    try:
        st.session_state.agent = PhysicsSolverAgent(api_key)
        st.session_state.api_key = api_key
        return True
    except Exception as e:
        st.error(f"❌ API 키 설정 실패: {str(e)}")
        return False


def main():
    initialize_session_state()
    
    # ===== 사이드바 =====
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">🔑 API 설정</div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key 입력
        api_key_input = st.text_input(
            "Google API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="Google API Key를 입력하세요",
            help="Google AI Studio에서 발급받은 API 키를 입력하세요."
        )
        
        # API Key 변경 시 에이전트 재생성
        if api_key_input and api_key_input != st.session_state.api_key:
            if create_agent(api_key_input):
                st.success("✅ API 키가 설정되었습니다!")
        elif api_key_input and st.session_state.agent is None:
            create_agent(api_key_input)
        
        # API 키 상태 표시
        if st.session_state.agent:
            st.markdown("🟢 **연결됨**")
        else:
            st.markdown("🔴 **API 키 필요**")
        
        st.markdown("---")
        
        # 사용 방법
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">📚 사용 방법</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        1. **API 키 입력** - Google AI Studio에서 발급
        2. **이미지 업로드** - 물리 문제 사진 업로드
        3. **문제 풀기 클릭** - AI가 분석 및 풀이
        4. **결과 확인** - 단계별 풀이 확인
        """)
        
        st.markdown("---")
        
        # 지원 기능
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">🔧 지원 기능</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        - 📐 **방정식 풀이**
        - 📈 **미분 계산**
        - 📊 **적분 계산**
        - 🚀 **등가속도 운동**
        - ✨ **수식 간소화**
        - 🔢 **값 대입 계산**
        """)
        
        st.markdown("---")
        
        # 초기화 버튼
        if st.button("🗑️ 결과 초기화", use_container_width=True):
            st.session_state.result = None
            st.session_state.uploaded_image = None
            st.session_state.chat_history = []
            st.rerun()
    
    # ===== 메인 영역 =====
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>📸 AI 물리 문제 해결사</h1>
        <p>Powered by Google Gemini | 이미지를 업로드하면 AI가 문제를 분석하고 풀이해드립니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API 키 확인
    if not st.session_state.agent:
        st.warning("⚠️ 사이드바에서 Google API Key를 입력해주세요.")
        st.info("""
        **API 키 발급 방법:**
        1. [Google AI Studio](https://aistudio.google.com/) 접속
        2. 'Get API key' 클릭
        3. 새 API 키 생성
        4. 왼쪽 사이드바에 붙여넣기
        """)
        return
    
    # 탭 구성
    tab1, tab2 = st.tabs(["📷 이미지로 풀기", "✍️ 텍스트로 풀기"])
    
    # ===== 탭 1: 이미지로 풀기 =====
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📤 문제 이미지 업로드")
            
            # 이미지 업로더
            uploaded_file = st.file_uploader(
                "물리 문제가 있는 이미지를 업로드하세요",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                help="지원 형식: PNG, JPG, JPEG, GIF, WEBP"
            )
            
            if uploaded_file is not None:
                # 이미지 저장
                image = Image.open(uploaded_file)
                st.session_state.uploaded_image = image
                
                # 이미지 표시
                st.image(image, caption="업로드된 이미지", use_container_width=True)
                
                # 추가 맥락 입력
                additional_context = st.text_area(
                    "추가 정보 (선택사항)",
                    placeholder="예: 중력가속도는 10 m/s²로 가정해줘, 공기 저항은 무시해줘...",
                    height=80
                )
                
                # 문제 풀기 버튼
                if st.button("🚀 문제 풀기", use_container_width=True, type="primary"):
                    with st.spinner("🧠 AI가 문제를 분석하고 있습니다..."):
                        try:
                            result = st.session_state.agent.analyze_and_solve(
                                image,
                                additional_context=additional_context
                            )
                            st.session_state.result = result
                        except Exception as e:
                            st.error(f"❌ 오류 발생: {str(e)}")
        
        with col2:
            st.markdown("### 📝 풀이 결과")
            
            if st.session_state.result:
                # 결과 표시 (LaTeX 렌더링 지원)
                st.markdown("""
                <div class="result-area">
                    <div class="result-header">✨ AI 풀이</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Markdown + LaTeX 렌더링
                st.markdown(st.session_state.result)
                
                # 복사 버튼
                st.markdown("---")
                st.download_button(
                    "📋 결과 다운로드",
                    st.session_state.result,
                    file_name="physics_solution.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            else:
                st.info("👈 왼쪽에서 이미지를 업로드하고 '문제 풀기' 버튼을 클릭하세요.")
    
    # ===== 탭 2: 텍스트로 풀기 =====
    with tab2:
        st.markdown("### ✍️ 물리 문제 입력")
        
        # 예시 문제
        example_problems = [
            "초기 속도 0 m/s로 출발한 물체가 10 m/s²의 가속도로 5초간 이동했을 때 최종 속도와 이동 거리는?",
            "질량 2kg인 물체에 10N의 힘이 작용할 때 가속도는? (F=ma 적용)",
            "높이 45m에서 자유낙하하는 물체가 지면에 도달하는 데 걸리는 시간은? (g=10m/s²)",
            "x² + 5x + 6 = 0을 풀어줘",
            "sin(x)를 x에 대해 미분하면?",
            "∫(x² + 2x) dx를 구해줘"
        ]
        
        # 예시 선택
        selected_example = st.selectbox(
            "💡 예시 문제 선택 (또는 직접 입력)",
            ["직접 입력"] + example_problems
        )
        
        # 문제 입력
        if selected_example == "직접 입력":
            problem_text = st.text_area(
                "물리 문제를 입력하세요",
                placeholder="예: 시속 72km로 달리던 자동차가 급정거하여 4초 만에 멈췄다. 제동 거리는?",
                height=120
            )
        else:
            problem_text = st.text_area(
                "물리 문제를 입력하세요",
                value=selected_example,
                height=120
            )
        
        # 풀기 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧮 풀이 시작", use_container_width=True, type="primary"):
                if problem_text.strip():
                    with st.spinner("🧠 AI가 문제를 풀고 있습니다..."):
                        try:
                            result = st.session_state.agent.solve_text_problem(problem_text)
                            st.session_state.result = result
                        except Exception as e:
                            st.error(f"❌ 오류 발생: {str(e)}")
                else:
                    st.warning("⚠️ 문제를 입력해주세요.")
        
        # 결과 표시
        if st.session_state.result:
            st.markdown("---")
            st.markdown("### 📝 풀이 결과")
            
            st.markdown("""
            <div class="result-area">
                <div class="result-header">✨ AI 풀이</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Markdown + LaTeX 렌더링
            st.markdown(st.session_state.result)
            
            # 다운로드 버튼
            st.download_button(
                "📋 결과 다운로드",
                st.session_state.result,
                file_name="physics_solution.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.85rem;">
        <p>🔬 PhysicsSolverBot | Powered by Google Gemini 2.0 Flash</p>
        <p>수식 계산에는 SymPy를 사용합니다</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
