# 📸 PhysicsSolverBot - AI 물리 문제 해결사

> **Gemini 2.0 Flash + SymPy + Streamlit** 기반 멀티모달 물리 문제 풀이 AI 에이전트

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 프로젝트 개요

**PhysicsSolverBot**은 이미지 또는 텍스트로 물리 문제를 입력받아 **AI가 분석하고 단계별로 풀이**해주는 멀티모달 에이전트입니다.

### 핵심 특징

- 🖼️ **멀티모달 입력**: 이미지(문제 사진) 또는 텍스트로 문제 입력
- 🧮 **정확한 계산**: SymPy 라이브러리를 통한 기호 수학 연산 (환각 방지)
- 🔧 **Function Calling**: Gemini의 Tool Use 기능으로 자동 도구 선택
- 📝 **단계별 풀이**: Chain of Thought 프롬프팅으로 논리적 풀이 과정 제공
- 🎨 **현대적 UI**: Streamlit 기반의 직관적인 웹 인터페이스

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (main.py)                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  📷 이미지 업로드 │  │  ✍️ 텍스트 입력  │  │  📊 결과 표시   │ │
│  └────────┬────────┘  └────────┬────────┘  └────────▲────────┘ │
└───────────┼─────────────────────┼───────────────────┼───────────┘
            │                     │                   │
            ▼                     ▼                   │
┌─────────────────────────────────────────────────────┼───────────┐
│                   Gemini Agent (agent.py)           │           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  • 멀티모달 입력 처리 (이미지 + 텍스트)                       ││
│  │  • Function Calling을 통한 도구 선택                         ││
│  │  • Chain of Thought 프롬프팅                                 ││
│  └──────────────────────────┬──────────────────────────────────┘│
└─────────────────────────────┼───────────────────────────────────┘
                              │ Tool Call
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SymPy Tools (tools.py)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │solve_equation│ │  derivative  │ │   integral   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  kinematics  │ │   simplify   │ │   evaluate   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 프로젝트 구조

```
PhysicsSolverBot/
├── 📄 main.py              # Streamlit UI (웹 인터페이스)
├── 🤖 agent.py             # Gemini 멀티모달 에이전트 (Function Calling)
├── 🧮 tools.py             # SymPy 기반 수학/물리 계산 도구
├── 📋 requirements.txt     # 의존성 패키지 목록
├── 🔐 .env                 # 환경 변수 (API 키)
├── 📖 README.md            # 프로젝트 문서
└── 🚫 .gitignore           # Git 제외 파일 목록
```

---

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/PhysicsSolverBot.git
cd PhysicsSolverBot
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Linux/Mac)
source venv/bin/activate

# 활성화 (Windows)
.\venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. API 키 설정

```bash
# .env 파일 생성
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

> 💡 API 키는 [Google AI Studio](https://aistudio.google.com/)에서 무료로 발급받을 수 있습니다.

### 5. 앱 실행

```bash
streamlit run main.py
```

브라우저에서 `http://localhost:8501` 접속!

---

## 📱 사용 방법

### 방법 1: 이미지로 문제 풀기

1. **API 키 입력**: 사이드바에 Google API Key 입력
2. **이미지 업로드**: "📷 이미지로 풀기" 탭에서 물리 문제 사진 업로드
3. **문제 풀기 클릭**: AI가 이미지를 분석하고 풀이 시작
4. **결과 확인**: 단계별 풀이 과정과 정답 확인

### 방법 2: 텍스트로 문제 풀기

1. **API 키 입력**: 사이드바에 Google API Key 입력
2. **문제 입력**: "✍️ 텍스트로 풀기" 탭에서 문제 직접 입력
3. **예시 선택**: 드롭다운에서 예시 문제 선택 가능
4. **풀이 시작**: AI가 문제를 분석하고 도구를 사용해 계산

### 지원 기능

| 기능 | 설명 | 예시 |
|------|------|------|
| 📐 방정식 풀이 | 1차/2차 방정식 해 구하기 | `2x + 4 = 10`, `x² + 5x + 6 = 0` |
| 📈 미분 | 함수의 도함수 계산 | `d/dx (x³ + 2x)` → `3x² + 2` |
| 📊 적분 | 부정적분 및 정적분 | `∫x² dx` → `x³/3 + C` |
| 🚀 등가속도 운동 | v, a, t, s 관계 계산 | 초기속도 0, 가속도 10, 시간 5 → 속도? |
| ✨ 수식 간소화 | 복잡한 수식 정리 | `(x+1)(x-1)` → `x² - 1` |
| 🔢 값 대입 | 수식에 숫자 대입 | `F = ma`, m=2, a=5 → F=10 |

---

## 🔧 핵심 컴포넌트 설명

### 1. `tools.py` - SymPy 계산 도구

SymPy 라이브러리를 활용한 **기호 수학(Symbolic Math)** 계산 도구입니다.

```python
from tools import solve_equation, calculate_derivative, calculate_integral

# 방정식 풀이
result = solve_equation("2*x + 4 = 10")
# → x = 3

# 미분
result = calculate_derivative("x**3 + 2*x", "x")
# → 3x² + 2

# 적분
result = calculate_integral("x**2", "x", "0", "1")
# → 1/3
```

**주요 특징:**
- `CalculationResult` 데이터 클래스로 구조화된 결과 반환
- 텍스트 및 LaTeX 형식 동시 지원
- 암시적 곱셈 지원 (`2x` → `2*x`)
- 포괄적인 에러 처리

### 2. `agent.py` - Gemini 멀티모달 에이전트

Google Gemini 2.0 Flash 모델을 활용한 **Function Calling 기반 에이전트**입니다.

```python
from agent import PhysicsSolverAgent

agent = PhysicsSolverAgent(api_key="your_key")

# 이미지 분석 및 풀이
result = agent.analyze_and_solve("problem.png")

# 텍스트 문제 풀이
result = agent.solve_text_problem("초기 속도 0에서 10m/s²로 5초 가속하면?")
```

**주요 특징:**
- `genai.protos.FunctionDeclaration`을 통한 도구 정의
- 자동 Function Call 처리 및 결과 통합
- 멀티모달 입력 지원 (이미지 + 텍스트)

### 3. `main.py` - Streamlit UI

```python
# 실행
streamlit run main.py --server.port 8501
```

**주요 특징:**
- 반응형 2-탭 인터페이스 (이미지/텍스트)
- 실시간 API 키 검증
- Markdown/LaTeX 렌더링 지원
- 결과 다운로드 기능

---

## 🛡️ 개발 시 주의사항 및 팁

### 1. 환각(Hallucination) 방지 전략

AI가 직접 암산하지 않고 **반드시 SymPy 도구를 호출**하도록 설계했습니다.

```python
# agent.py의 시스템 프롬프트
system_prompt = """
계산이 필요한 경우 반드시 도구(Tool)를 사용해 정확한 값을 계산하고,
풀이 과정을 단계별로 설명해라.
"""

# Function Calling 설정으로 도구 사용 강제
tool_config={"function_calling_config": {"mode": "AUTO"}}
```

**향후 개선 방향:**
- Tool 사용 로그를 `st.expander`로 UI에 표시하여 **AI 사고 과정 투명화**
- 도구 호출 여부 검증 로직 추가

### 2. 프롬프트 엔지니어링 (Chain of Thought)

논리적 비약을 막기 위한 **구조화된 프롬프팅**을 적용했습니다.

```python
# agent.py 시스템 프롬프트
"""
너는 친절하고 명석한 물리학 튜터다.

역할:
1. 학생이 제시한 물리 문제를 정확히 이해한다.
2. 문제에서 주어진 값과 구해야 할 값을 명확히 파악한다.
3. 적절한 물리 공식과 개념을 적용한다.
4. 계산이 필요한 경우 반드시 도구(Tool)를 사용한다.
5. 풀이 과정을 단계별로 친절하게 설명한다.
"""
```

**향후 개선 방향:**
- 문제 유형 분류 단계 추가 (역학, 전자기학, 열역학 등)
- 변수 나열 → 공식 선택 → 계산 → 검증의 4단계 프로세스

### 3. 보안 (Sandboxing) 고려사항

⚠️ **현재 구현의 보안 한계:**

```python
# tools.py에서 sympy.sympify() 사용
# 이는 내부적으로 eval()과 유사한 동작을 할 수 있음
expr = sp.sympify(expression)
```

✅ **상용화 시 권장 사항:**

```python
# 1. 입력 검증 강화
ALLOWED_FUNCTIONS = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt']
def validate_expression(expr_str):
    # 허용된 함수만 사용 가능하도록 검증
    pass

# 2. 샌드박스 환경에서 실행
# - Docker 컨테이너 격리
# - E2B (Code Interpreter API) 활용
# - AWS Lambda 등 서버리스 함수 활용
```

> 💡 **면접 어필 포인트**: "실제 상용화 단계에서는 Python 코드를 로컬이 아닌 **Docker 컨테이너나 E2B 같은 샌드박스 환경**에서 실행하여 보안을 강화해야 함을 알고 있습니다."

---

## 📊 API 사용량 및 제한

| 플랜 | 분당 요청 | 일일 요청 | 비용 |
|------|----------|----------|------|
| 무료 | 15회 | 1,500회 | $0 |
| 유료 | 1,000회+ | 무제한 | 종량제 |

> 429 오류 발생 시 1-2분 대기 후 재시도하세요.

---

## 🔮 향후 개선 계획

- [ ] **Tool 사용 로그 시각화**: st.expander로 AI 사고 과정 공개
- [ ] **문제 유형 자동 분류**: 역학/전자기학/열역학 등 카테고리화
- [ ] **풀이 검증 시스템**: 역계산으로 답 검증
- [ ] **학습 이력 관리**: 풀이한 문제 저장 및 복습 기능
- [ ] **Docker 컨테이너화**: 배포 및 보안 강화
- [ ] **다국어 지원**: 영어/한국어 문제 자동 감지

---

## 🛠️ 기술 스택

| 카테고리 | 기술 |
|----------|------|
| **Language** | Python 3.10+ |
| **AI Model** | Google Gemini 2.0 Flash |
| **Math Engine** | SymPy 1.13+ |
| **Web Framework** | Streamlit 1.40+ |
| **Image Processing** | Pillow |

---

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 🙋 문의

질문이나 제안이 있으시면 Issue를 등록해주세요!

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요! ⭐**

</div>
