"""
PhysicsSolverBot - Gemini AI 멀티모달 에이전트
이미지 기반 물리 문제 분석 및 풀이
"""

import os
import json
import re
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv
from PIL import Image
import io

from tools import (
    solve_equation,
    calculate_derivative,
    calculate_integral,
    kinematics_solver,
    simplify_expression,
    evaluate_expression,
    CalculationResult
)

# 환경 변수 로드
load_dotenv()


class PhysicsSolverAgent:
    """멀티모달 물리 문제 풀이 AI 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        에이전트 초기화
        
        Args:
            api_key: Google API 키 (없으면 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_key)
        
        # Function Calling을 위한 도구 정의
        self.tools = self._define_tools()
        
        # Gemini 모델 설정 (Function Calling 포함)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=self._get_system_prompt(),
            tools=self.tools
        )
        
        # 대화 히스토리
        self.chat_history: List[Dict[str, str]] = []
        self.chat = None
        
        # 도구 함수 매핑
        self.tool_functions = {
            "solve_equation": solve_equation,
            "calculate_derivative": calculate_derivative,
            "calculate_integral": calculate_integral,
            "kinematics_solver": kinematics_solver,
            "simplify_expression": simplify_expression,
            "evaluate_expression": evaluate_expression
        }
    
    def _get_system_prompt(self) -> str:
        """시스템 프롬프트를 반환합니다."""
        return """너는 친절하고 명석한 물리학 튜터다. 
이미지를 보고 문제를 파악한 뒤, 필요한 경우 도구(Tool)를 사용해 정확한 값을 계산하고, 풀이 과정을 단계별로 설명해라.

역할:
1. 학생이 제시한 물리 문제(텍스트 또는 이미지)를 정확히 이해한다.
2. 문제에서 주어진 값과 구해야 할 값을 명확히 파악한다.
3. 적절한 물리 공식과 개념을 적용한다.
4. 계산이 필요한 경우 반드시 도구(Tool)를 사용하여 정확한 값을 구한다.
5. 풀이 과정을 단계별로 친절하게 설명한다.

사용 가능한 도구:
- solve_equation: 방정식 풀이 (예: "2*x + 4 = 10")
- calculate_derivative: 미분 계산
- calculate_integral: 적분 계산 (부정적분 및 정적분)
- kinematics_solver: 등가속도 운동 문제 풀이 (v0, v, a, t, s)
- simplify_expression: 수식 간소화
- evaluate_expression: 수식에 값 대입 계산

응답 형식:
- 수식은 LaTeX로 표시 (예: $v = v_0 + at$)
- 단위를 항상 명시
- 풀이를 단계별로 나누어 설명
- 한국어로 친근하게 응답"""

    def _define_tools(self) -> List[genai.protos.Tool]:
        """Gemini Function Calling을 위한 도구를 정의합니다."""
        
        # 함수 선언 정의
        solve_equation_func = genai.protos.FunctionDeclaration(
            name="solve_equation",
            description="주어진 방정식을 풉니다. 변수는 자동으로 감지됩니다. 예: '2*x + 4 = 10', 'x**2 - 4 = 0'",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "equation_str": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="방정식 문자열. 예: '2*x + 4 = 10', 'x**2 + 5*x + 6 = 0'"
                    )
                },
                required=["equation_str"]
            )
        )
        
        calculate_derivative_func = genai.protos.FunctionDeclaration(
            name="calculate_derivative",
            description="주어진 수식의 미분을 계산합니다.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "expression": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="미분할 수식. 예: 'x**2 + 3*x', 'sin(x)'"
                    ),
                    "variable": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="미분할 변수. 기본값: 'x'"
                    ),
                    "order": genai.protos.Schema(
                        type=genai.protos.Type.INTEGER,
                        description="미분 차수. 기본값: 1"
                    )
                },
                required=["expression"]
            )
        )
        
        calculate_integral_func = genai.protos.FunctionDeclaration(
            name="calculate_integral",
            description="주어진 수식의 적분을 계산합니다. 정적분 또는 부정적분 가능.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "expression": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="적분할 수식. 예: 'x**2', 'cos(x)'"
                    ),
                    "variable": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="적분할 변수. 기본값: 'x'"
                    ),
                    "lower_bound": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="정적분의 하한. 예: '0'"
                    ),
                    "upper_bound": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="정적분의 상한. 예: '1'"
                    )
                },
                required=["expression"]
            )
        )
        
        kinematics_solver_func = genai.protos.FunctionDeclaration(
            name="kinematics_solver",
            description="1차원 등가속도 운동 문제를 풉니다. 주어진 값들로 미지수를 계산합니다. 변수: v0(초기속도 m/s), v(최종속도 m/s), a(가속도 m/s²), t(시간 s), s(변위 m)",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "known_values": genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        description="알려진 값들의 딕셔너리. 예: {'v0': 0, 'a': 10, 't': 5}"
                    ),
                    "find": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="구하고자 하는 변수. 'v0', 'v', 'a', 't', 's' 중 하나"
                    )
                },
                required=["known_values", "find"]
            )
        )
        
        simplify_expression_func = genai.protos.FunctionDeclaration(
            name="simplify_expression",
            description="수식을 간소화합니다.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "expression": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="간소화할 수식"
                    )
                },
                required=["expression"]
            )
        )
        
        evaluate_expression_func = genai.protos.FunctionDeclaration(
            name="evaluate_expression",
            description="수식에 값을 대입하여 계산합니다.",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "expression": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="계산할 수식. 예: 'm*a', 'F/m'"
                    ),
                    "substitutions": genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        description="변수와 값의 딕셔너리. 예: {'m': 2, 'a': 5}"
                    )
                },
                required=["expression", "substitutions"]
            )
        )
        
        # Tool 객체 생성
        tool = genai.protos.Tool(
            function_declarations=[
                solve_equation_func,
                calculate_derivative_func,
                calculate_integral_func,
                kinematics_solver_func,
                simplify_expression_func,
                evaluate_expression_func
            ]
        )
        
        return [tool]
    
    def _execute_function(self, function_call) -> Dict[str, Any]:
        """함수 호출을 실행하고 결과를 반환합니다."""
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        if function_name not in self.tool_functions:
            return {"success": False, "error": f"알 수 없는 함수: {function_name}"}
        
        try:
            # 함수 실행
            func = self.tool_functions[function_name]
            result = func(**function_args)
            
            # CalculationResult 객체인 경우 딕셔너리로 변환
            if isinstance(result, CalculationResult):
                return result.to_dict()
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_image(self, image: Union[str, Path, Image.Image, bytes]) -> Image.Image:
        """다양한 형식의 이미지를 PIL Image로 로드합니다."""
        if isinstance(image, Image.Image):
            return image
        elif isinstance(image, bytes):
            return Image.open(io.BytesIO(image))
        elif isinstance(image, (str, Path)):
            path = Path(image)
            if path.exists():
                return Image.open(path)
            else:
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {path}")
        else:
            raise ValueError(f"지원하지 않는 이미지 형식: {type(image)}")
    
    def analyze_and_solve(self, image: Union[str, Path, Image.Image, bytes], 
                          additional_context: str = "") -> str:
        """
        이미지를 분석하고 물리 문제를 풀이합니다.
        
        Args:
            image: 분석할 이미지 (파일 경로, PIL Image, 또는 bytes)
            additional_context: 추가 맥락 정보 (선택)
        
        Returns:
            풀이 결과 문자열
        """
        try:
            # 이미지 로드
            pil_image = self._load_image(image)
            
            # 프롬프트 구성
            prompt = "이 이미지에 있는 물리 문제를 분석하고 풀어줘. 필요한 경우 도구를 사용해서 정확한 계산을 해줘."
            if additional_context:
                prompt += f"\n\n추가 정보: {additional_context}"
            
            # Gemini에 이미지와 프롬프트 전송
            response = self.model.generate_content(
                [prompt, pil_image],
                tool_config={"function_calling_config": {"mode": "AUTO"}}
            )
            
            # Function Call 처리
            final_response = self._process_response(response)
            
            return final_response
            
        except FileNotFoundError as e:
            return f"❌ 이미지 로드 오류: {str(e)}"
        except Exception as e:
            error_msg = str(e)
            # Rate Limit / Quota 오류 처리
            if "429" in error_msg or "quota" in error_msg.lower():
                return """⚠️ **API 할당량 초과 오류**

Google Gemini API 요청 한도를 초과했습니다.

**해결 방법:**
1. **1-2분 기다린 후** 다시 시도해주세요 (무료 플랜은 분당 요청 제한이 있습니다)
2. [Google AI Studio](https://aistudio.google.com/)에서 **새 API 키**를 발급받아 사용하세요
3. [API 사용량 확인](https://ai.dev/rate-limit)에서 현재 사용량을 확인하세요

💡 **팁:** 무료 플랜은 분당 15회, 일일 1,500회 요청 제한이 있습니다."""
            # 인증 오류 처리
            elif "401" in error_msg or "API key" in error_msg.lower() or "invalid" in error_msg.lower():
                return """❌ **API 키 오류**

API 키가 유효하지 않습니다. 다음을 확인해주세요:
1. API 키가 올바르게 입력되었는지 확인
2. [Google AI Studio](https://aistudio.google.com/)에서 새 키 발급
3. 키에 불필요한 공백이 없는지 확인"""
            else:
                return f"❌ 분석 중 오류 발생: {error_msg}"
    
    def _process_response(self, response) -> str:
        """응답을 처리하고 Function Call이 있으면 실행합니다."""
        
        # 최대 반복 횟수 (무한 루프 방지)
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 응답에서 파트 확인
            if not response.candidates:
                return "응답을 받지 못했습니다."
            
            candidate = response.candidates[0]
            
            # Function Call 확인
            function_calls = []
            text_parts = []
            
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call.name:
                    function_calls.append(part.function_call)
                elif hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            
            # Function Call이 없으면 텍스트 반환
            if not function_calls:
                return "\n".join(text_parts) if text_parts else "응답이 비어있습니다."
            
            # Function Call 실행
            function_responses = []
            for fc in function_calls:
                result = self._execute_function(fc)
                function_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fc.name,
                            response={"result": result}
                        )
                    )
                )
            
            # Function Response를 모델에 전달
            response = self.model.generate_content(
                [
                    genai.protos.Content(
                        role="user",
                        parts=[genai.protos.Part(text="이전 문제를 계속 풀어줘")]
                    ),
                    genai.protos.Content(
                        role="model",
                        parts=candidate.content.parts
                    ),
                    genai.protos.Content(
                        role="function",
                        parts=function_responses
                    )
                ],
                tool_config={"function_calling_config": {"mode": "AUTO"}}
            )
        
        return "최대 반복 횟수를 초과했습니다."
    
    def start_chat(self):
        """새 채팅 세션을 시작합니다."""
        self.chat = self.model.start_chat(
            history=[],
            enable_automatic_function_calling=True
        )
        self.chat_history = []
    
    def send_message(self, message: str, image: Optional[Union[str, Path, Image.Image, bytes]] = None) -> str:
        """
        메시지를 보내고 응답을 받습니다.
        
        Args:
            message: 사용자 메시지
            image: 선택적 이미지
            
        Returns:
            AI 응답
        """
        if self.chat is None:
            self.start_chat()
        
        try:
            # 콘텐츠 구성
            content = [message]
            if image is not None:
                pil_image = self._load_image(image)
                content.append(pil_image)
            
            # 메시지 전송
            response = self.chat.send_message(content)
            
            # Function Call이 있는 경우 자동 처리됨 (enable_automatic_function_calling=True)
            response_text = response.text
            
            # 히스토리 저장
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            error_msg = f"오류가 발생했습니다: {str(e)}"
            return error_msg
    
    def solve_text_problem(self, problem: str) -> str:
        """
        텍스트 물리 문제를 풀이합니다.
        
        Args:
            problem: 물리 문제 텍스트
            
        Returns:
            풀이 결과
        """
        prompt = f"""다음 물리 문제를 풀어줘. 필요한 경우 도구를 사용해서 정확한 계산을 해줘.

문제: {problem}

풀이를 단계별로 자세히 설명해줘."""
        
        try:
            response = self.model.generate_content(
                prompt,
                tool_config={"function_calling_config": {"mode": "AUTO"}}
            )
            
            return self._process_response(response)
            
        except Exception as e:
            error_msg = str(e)
            # Rate Limit / Quota 오류 처리
            if "429" in error_msg or "quota" in error_msg.lower():
                return """⚠️ **API 할당량 초과 오류**

Google Gemini API 요청 한도를 초과했습니다.

**해결 방법:**
1. **1-2분 기다린 후** 다시 시도해주세요
2. [Google AI Studio](https://aistudio.google.com/)에서 **새 API 키**를 발급받아 사용하세요

💡 **팁:** 무료 플랜은 분당 15회 요청 제한이 있습니다."""
            # 인증 오류 처리
            elif "401" in error_msg or "API key" in error_msg.lower():
                return "❌ **API 키 오류**: API 키가 유효하지 않습니다."
            else:
                return f"❌ 풀이 중 오류 발생: {error_msg}"
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """채팅 히스토리를 반환합니다."""
        return self.chat_history
    
    def clear_history(self):
        """채팅 히스토리를 초기화합니다."""
        self.chat_history = []
        self.chat = None


# ===== 테스트 함수 =====
def test_agent():
    """에이전트 테스트"""
    print("=" * 60)
    print("🧪 PhysicsSolverBot 에이전트 테스트")
    print("=" * 60)
    
    try:
        agent = PhysicsSolverAgent()
        print("✅ 에이전트 초기화 성공\n")
        
        # 텍스트 문제 풀이 테스트
        test_problems = [
            "초기 속도 0 m/s로 출발한 물체가 10 m/s²의 가속도로 5초간 이동했을 때 최종 속도는?",
            "x² + 5x + 6 = 0 을 풀어줘",
            "x³ + 2x를 x에 대해 미분하면?"
        ]
        
        for i, problem in enumerate(test_problems, 1):
            print(f"\n📝 테스트 {i}: {problem}")
            print("-" * 50)
            
            result = agent.solve_text_problem(problem)
            print(f"답변:\n{result}")
            print()
        
    except ValueError as e:
        print(f"❌ API 키 오류: {e}")
        print("💡 .env 파일에 GOOGLE_API_KEY를 설정해주세요.")
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")


if __name__ == "__main__":
    test_agent()
