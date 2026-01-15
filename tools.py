"""
PhysicsSolverBot - SymPy 기반 수학/물리 계산 도구
"""

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass


@dataclass
class CalculationResult:
    """계산 결과를 담는 데이터 클래스"""
    success: bool
    text: str  # 깔끔한 텍스트 형식
    latex: str  # LaTeX 형식
    details: Dict[str, Any]  # 상세 정보
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "text": self.text,
            "latex": self.latex,
            "details": self.details,
            "error": self.error
        }


def _parse_expression(expr_str: str) -> sp.Expr:
    """
    문자열을 SymPy 표현식으로 파싱합니다.
    암시적 곱셈(예: 2x → 2*x)을 지원합니다.
    """
    transformations = standard_transformations + (implicit_multiplication_application,)
    return parse_expr(expr_str, transformations=transformations)


def _extract_variables(expr: sp.Expr) -> List[sp.Symbol]:
    """표현식에서 변수(Symbol)들을 추출합니다."""
    return list(expr.free_symbols)


def _find_main_variable(expr: sp.Expr) -> sp.Symbol:
    """
    표현식에서 주요 변수를 찾습니다.
    기본적으로 'x'를 우선시하고, 없으면 첫 번째 변수를 반환합니다.
    """
    symbols = _extract_variables(expr)
    if not symbols:
        raise ValueError("방정식에 변수가 없습니다.")
    
    # x를 우선시
    for sym in symbols:
        if str(sym) == 'x':
            return sym
    
    # x가 없으면 알파벳 순서로 첫 번째 반환
    return sorted(symbols, key=lambda s: str(s))[0]


def solve_equation(equation_str: str) -> CalculationResult:
    """
    주어진 방정식을 풀어 해를 반환합니다.
    
    Args:
        equation_str: 방정식 문자열 
                     예: '2*x + 4 = 10', 'x**2 - 4 = 0', '2x + 4 = 10'
    
    Returns:
        CalculationResult: 해와 풀이 과정을 담은 결과 객체
        
    Examples:
        >>> result = solve_equation('2*x + 4 = 10')
        >>> print(result.text)
        "방정식 2*x + 4 = 10 의 해: x = 3"
    """
    try:
        # 입력값 검증
        if not equation_str or not equation_str.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="방정식이 입력되지 않았습니다."
            )
        
        equation_str = equation_str.strip()
        
        # 등호가 있는 경우 분리
        if "=" in equation_str:
            parts = equation_str.split("=")
            if len(parts) != 2:
                return CalculationResult(
                    success=False,
                    text="",
                    latex="",
                    details={},
                    error="방정식 형식이 올바르지 않습니다. '=' 기호는 하나만 사용해주세요."
                )
            
            left_str, right_str = parts[0].strip(), parts[1].strip()
            
            try:
                left_expr = _parse_expression(left_str)
                right_expr = _parse_expression(right_str)
            except Exception as parse_error:
                return CalculationResult(
                    success=False,
                    text="",
                    latex="",
                    details={},
                    error=f"수식 파싱 오류: {str(parse_error)}"
                )
            
            # 좌변 - 우변 = 0 형태로 변환
            expr = left_expr - right_expr
            original_eq = f"{left_str} = {right_str}"
        else:
            # = 0 으로 가정
            try:
                expr = _parse_expression(equation_str)
            except Exception as parse_error:
                return CalculationResult(
                    success=False,
                    text="",
                    latex="",
                    details={},
                    error=f"수식 파싱 오류: {str(parse_error)}"
                )
            original_eq = f"{equation_str} = 0"
        
        # 주요 변수 찾기
        try:
            variable = _find_main_variable(expr)
        except ValueError as e:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=str(e)
            )
        
        # 방정식 풀기
        solutions = sp.solve(expr, variable)
        
        if not solutions:
            return CalculationResult(
                success=False,
                text=f"방정식 {original_eq} 의 해를 찾을 수 없습니다.",
                latex=sp.latex(sp.Eq(_parse_expression(equation_str.split("=")[0]) if "=" in equation_str else expr, 
                                     _parse_expression(equation_str.split("=")[1]) if "=" in equation_str else 0)),
                details={"equation": original_eq, "variable": str(variable)},
                error="해가 존재하지 않거나 찾을 수 없습니다."
            )
        
        # 결과 포맷팅
        var_name = str(variable)
        
        if len(solutions) == 1:
            sol = solutions[0]
            text_result = f"방정식 {original_eq} 의 해:\n  {var_name} = {sol}"
            latex_solutions = f"{var_name} = {sp.latex(sol)}"
        else:
            sol_strs = [f"  {var_name} = {sol}" for sol in solutions]
            text_result = f"방정식 {original_eq} 의 해:\n" + "\n".join(sol_strs)
            latex_solutions = ", ".join([f"{var_name} = {sp.latex(sol)}" for sol in solutions])
        
        # LaTeX 방정식 표현
        if "=" in equation_str:
            latex_eq = f"{sp.latex(left_expr)} = {sp.latex(right_expr)}"
        else:
            latex_eq = f"{sp.latex(expr)} = 0"
        
        return CalculationResult(
            success=True,
            text=text_result,
            latex=f"$${latex_eq}$$\n\n**해:** ${latex_solutions}$",
            details={
                "equation": original_eq,
                "variable": var_name,
                "solutions": [str(sol) for sol in solutions],
                "solutions_simplified": [str(sp.simplify(sol)) for sol in solutions],
                "num_solutions": len(solutions)
            }
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"방정식 풀이 중 오류 발생: {str(e)}"
        )


def calculate_derivative(expression: str, variable: str = "x", order: int = 1) -> CalculationResult:
    """
    주어진 표현식의 미분을 계산합니다.
    
    Args:
        expression: 미분할 수식 문자열 (예: 'x**2 + 3*x', 'sin(x)', 'x^3')
        variable: 미분할 변수 (기본값: 'x')
        order: 미분 차수 (기본값: 1, 2차 미분은 2)
    
    Returns:
        CalculationResult: 미분 결과를 담은 객체
        
    Examples:
        >>> result = calculate_derivative('x**2 + 3*x')
        >>> print(result.text)
        "d/dx (x² + 3x) = 2x + 3"
    """
    try:
        # 입력값 검증
        if not expression or not expression.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="수식이 입력되지 않았습니다."
            )
        
        if not variable or not variable.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="미분할 변수가 지정되지 않았습니다."
            )
        
        if order < 1:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="미분 차수는 1 이상이어야 합니다."
            )
        
        expression = expression.strip()
        variable = variable.strip()
        
        # 수식 파싱
        try:
            expr = _parse_expression(expression)
        except Exception as parse_error:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=f"수식 파싱 오류: {str(parse_error)}"
            )
        
        var = sp.Symbol(variable)
        
        # 미분 계산
        derivative = sp.diff(expr, var, order)
        simplified = sp.simplify(derivative)
        
        # 텍스트 포맷팅
        if order == 1:
            diff_notation = f"d/d{variable}"
            latex_notation = f"\\frac{{d}}{{d{variable}}}"
        else:
            diff_notation = f"d^{order}/d{variable}^{order}"
            latex_notation = f"\\frac{{d^{order}}}{{d{variable}^{order}}}"
        
        text_result = f"{diff_notation} ({expr}) = {simplified}"
        latex_result = f"$${latex_notation} \\left( {sp.latex(expr)} \\right) = {sp.latex(simplified)}$$"
        
        return CalculationResult(
            success=True,
            text=text_result,
            latex=latex_result,
            details={
                "original": str(expr),
                "variable": variable,
                "order": order,
                "derivative": str(derivative),
                "simplified": str(simplified),
                "latex_derivative": sp.latex(simplified)
            }
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"미분 계산 중 오류 발생: {str(e)}"
        )


def calculate_integral(
    expression: str, 
    variable: str = "x",
    lower_bound: Optional[str] = None, 
    upper_bound: Optional[str] = None
) -> CalculationResult:
    """
    주어진 표현식의 적분을 계산합니다.
    
    Args:
        expression: 적분할 수식 문자열 (예: 'x**2', 'sin(x)', '1/x')
        variable: 적분할 변수 (기본값: 'x')
        lower_bound: 정적분의 하한 (선택, 예: '0')
        upper_bound: 정적분의 상한 (선택, 예: '1')
    
    Returns:
        CalculationResult: 적분 결과를 담은 객체
        
    Examples:
        >>> result = calculate_integral('x**2')  # 부정적분
        >>> print(result.text)
        "∫ x² dx = x³/3 + C"
        
        >>> result = calculate_integral('x**2', lower_bound='0', upper_bound='1')  # 정적분
        >>> print(result.text)
        "∫₀¹ x² dx = 1/3"
    """
    try:
        # 입력값 검증
        if not expression or not expression.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="수식이 입력되지 않았습니다."
            )
        
        if not variable or not variable.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="적분할 변수가 지정되지 않았습니다."
            )
        
        expression = expression.strip()
        variable = variable.strip()
        
        # 수식 파싱
        try:
            expr = _parse_expression(expression)
        except Exception as parse_error:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=f"수식 파싱 오류: {str(parse_error)}"
            )
        
        var = sp.Symbol(variable)
        
        # 정적분 또는 부정적분 판단
        is_definite = lower_bound is not None and upper_bound is not None
        
        if is_definite:
            # 정적분
            try:
                lower = _parse_expression(lower_bound.strip())
                upper = _parse_expression(upper_bound.strip())
            except Exception as bound_error:
                return CalculationResult(
                    success=False,
                    text="",
                    latex="",
                    details={},
                    error=f"적분 범위 파싱 오류: {str(bound_error)}"
                )
            
            integral = sp.integrate(expr, (var, lower, upper))
            simplified = sp.simplify(integral)
            
            # 텍스트 포맷팅
            text_result = f"∫[{lower_bound}, {upper_bound}] ({expr}) d{variable} = {simplified}"
            latex_result = f"$$\\int_{{{sp.latex(lower)}}}^{{{sp.latex(upper)}}} {sp.latex(expr)} \\, d{variable} = {sp.latex(simplified)}$$"
            
            integral_type = "definite"
        else:
            # 부정적분
            integral = sp.integrate(expr, var)
            simplified = sp.simplify(integral)
            
            # 텍스트 포맷팅 (적분 상수 C 추가)
            text_result = f"∫ ({expr}) d{variable} = {simplified} + C"
            latex_result = f"$$\\int {sp.latex(expr)} \\, d{variable} = {sp.latex(simplified)} + C$$"
            
            integral_type = "indefinite"
        
        return CalculationResult(
            success=True,
            text=text_result,
            latex=latex_result,
            details={
                "original": str(expr),
                "variable": variable,
                "type": integral_type,
                "integral": str(integral),
                "simplified": str(simplified),
                "latex_integral": sp.latex(simplified),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            }
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"적분 계산 중 오류 발생: {str(e)}"
        )


def simplify_expression(expression: str) -> CalculationResult:
    """
    수식을 간소화합니다.
    
    Args:
        expression: 간소화할 수식 문자열
    
    Returns:
        CalculationResult: 간소화된 결과
    """
    try:
        if not expression or not expression.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="수식이 입력되지 않았습니다."
            )
        
        expression = expression.strip()
        
        try:
            expr = _parse_expression(expression)
        except Exception as parse_error:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=f"수식 파싱 오류: {str(parse_error)}"
            )
        
        simplified = sp.simplify(expr)
        
        text_result = f"{expr} = {simplified}"
        latex_result = f"$${sp.latex(expr)} = {sp.latex(simplified)}$$"
        
        return CalculationResult(
            success=True,
            text=text_result,
            latex=latex_result,
            details={
                "original": str(expr),
                "simplified": str(simplified),
                "latex_original": sp.latex(expr),
                "latex_simplified": sp.latex(simplified)
            }
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"수식 간소화 중 오류 발생: {str(e)}"
        )


def evaluate_expression(expression: str, substitutions: Dict[str, float]) -> CalculationResult:
    """
    수식에 값을 대입하여 계산합니다.
    
    Args:
        expression: 계산할 수식 문자열
        substitutions: 변수와 값의 딕셔너리 (예: {'x': 2, 'y': 3})
    
    Returns:
        CalculationResult: 계산 결과
    """
    try:
        if not expression or not expression.strip():
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="수식이 입력되지 않았습니다."
            )
        
        if not substitutions:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="대입할 값이 없습니다."
            )
        
        expression = expression.strip()
        
        try:
            expr = _parse_expression(expression)
        except Exception as parse_error:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=f"수식 파싱 오류: {str(parse_error)}"
            )
        
        # 심볼 생성 및 대입
        subs = {sp.Symbol(k): v for k, v in substitutions.items()}
        result = expr.subs(subs)
        
        # 수치 평가
        if result.is_number:
            numerical = float(result.evalf())
            # 정수인 경우 정수로 표시
            if numerical == int(numerical):
                numerical = int(numerical)
        else:
            numerical = str(result)
        
        # 대입 문자열 생성
        subs_str = ", ".join([f"{k} = {v}" for k, v in substitutions.items()])
        
        text_result = f"{expr} 에서 {subs_str} 일 때:\n결과 = {numerical}"
        latex_result = f"$${sp.latex(expr)}$$ \n\n{subs_str} 일 때: **{numerical}**"
        
        return CalculationResult(
            success=True,
            text=text_result,
            latex=latex_result,
            details={
                "expression": str(expr),
                "substitutions": substitutions,
                "result": numerical
            }
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"수식 계산 중 오류 발생: {str(e)}"
        )


def kinematics_solver(known_values: Dict[str, float], find: str) -> CalculationResult:
    """
    1차원 등가속도 운동 문제를 풉니다.
    
    변수들:
        - v0: 초기 속도 (m/s)
        - v: 최종 속도 (m/s)
        - a: 가속도 (m/s²)
        - t: 시간 (s)
        - s: 변위 (m)
    
    Args:
        known_values: 알려진 값들의 딕셔너리 (예: {'v0': 0, 'a': 10, 't': 5})
        find: 구하고자 하는 변수 ('v0', 'v', 'a', 't', 's' 중 하나)
    
    Returns:
        CalculationResult: 계산 결과
    """
    try:
        if not known_values:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error="알려진 값이 없습니다."
            )
        
        valid_vars = {'v0', 'v', 'a', 't', 's'}
        if find not in valid_vars:
            return CalculationResult(
                success=False,
                text="",
                latex="",
                details={},
                error=f"'{find}'는 유효하지 않은 변수입니다. 사용 가능: {valid_vars}"
            )
        
        v0, v, a, t, s = sp.symbols('v0 v a t s')
        
        # 등가속도 운동 방정식들
        equations = [
            sp.Eq(v, v0 + a * t),                              # v = v0 + at
            sp.Eq(s, v0 * t + sp.Rational(1, 2) * a * t**2),   # s = v0*t + 0.5*a*t²
            sp.Eq(v**2, v0**2 + 2 * a * s),                    # v² = v0² + 2as
            sp.Eq(s, (v0 + v) / 2 * t)                         # s = (v0 + v)/2 * t
        ]
        
        equation_names = [
            "v = v₀ + at",
            "s = v₀t + ½at²",
            "v² = v₀² + 2as",
            "s = (v₀ + v)t / 2"
        ]
        
        symbol_map = {'v0': v0, 'v': v, 'a': a, 't': t, 's': s}
        unit_map = {'v0': 'm/s', 'v': 'm/s', 'a': 'm/s²', 't': 's', 's': 'm'}
        
        # 알려진 값 대입
        substitutions = {symbol_map[k]: val for k, val in known_values.items() if k in symbol_map}
        target = symbol_map[find]
        
        # 각 방정식에서 해 찾기
        for eq, eq_name in zip(equations, equation_names):
            substituted = eq.subs(substitutions)
            if target in substituted.free_symbols and len(substituted.free_symbols) == 1:
                solutions = sp.solve(substituted, target)
                if solutions:
                    # 물리적으로 유효한 해 선택
                    valid_solutions = []
                    for sol in solutions:
                        try:
                            sol_val = float(sol)
                            if find == 't' and sol_val < 0:
                                continue
                            valid_solutions.append(sol_val)
                        except:
                            continue
                    
                    if valid_solutions:
                        result_val = valid_solutions[0]
                        unit = unit_map[find]
                        
                        # 알려진 값 문자열
                        known_str = ", ".join([f"{k} = {v} {unit_map.get(k, '')}" for k, v in known_values.items()])
                        
                        text_result = f"등가속도 운동 문제 풀이\n"
                        text_result += f"주어진 값: {known_str}\n"
                        text_result += f"사용 공식: {eq_name}\n"
                        text_result += f"결과: {find} = {result_val:.4g} {unit}"
                        
                        latex_result = f"**사용 공식:** ${sp.latex(eq)}$\n\n"
                        latex_result += f"**결과:** ${find} = {result_val:.4g}$ {unit}"
                        
                        return CalculationResult(
                            success=True,
                            text=text_result,
                            latex=latex_result,
                            details={
                                "known_values": known_values,
                                "find": find,
                                "equation_used": eq_name,
                                "result": result_val,
                                "unit": unit
                            }
                        )
        
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={"known_values": known_values, "find": find},
            error="주어진 값으로는 해를 구할 수 없습니다. 더 많은 정보가 필요합니다."
        )
        
    except Exception as e:
        return CalculationResult(
            success=False,
            text="",
            latex="",
            details={},
            error=f"운동학 계산 중 오류 발생: {str(e)}"
        )


# ===== 테스트 함수 =====
def test_tools():
    """도구 테스트"""
    print("=" * 60)
    print("🧪 PhysicsSolverBot 도구 테스트")
    print("=" * 60)
    
    # 1. 방정식 풀이 테스트
    print("\n📐 방정식 풀이 테스트:")
    test_equations = [
        "2*x + 4 = 10",
        "x**2 - 4 = 0",
        "x^2 + 5x + 6 = 0",
        "2x + 4 = 10"  # 암시적 곱셈
    ]
    for eq in test_equations:
        result = solve_equation(eq)
        print(f"  {eq}")
        if result.success:
            print(f"    → {result.text.split(chr(10))[-1]}")
        else:
            print(f"    → 오류: {result.error}")
    
    # 2. 미분 테스트
    print("\n📈 미분 테스트:")
    test_derivatives = [
        ("x**2 + 3*x", "x", 1),
        ("sin(x)", "x", 1),
        ("x**3", "x", 2),
    ]
    for expr, var, order in test_derivatives:
        result = calculate_derivative(expr, var, order)
        if result.success:
            print(f"  {result.text}")
        else:
            print(f"  오류: {result.error}")
    
    # 3. 적분 테스트
    print("\n📊 적분 테스트:")
    result = calculate_integral("x**2", "x")
    if result.success:
        print(f"  부정적분: {result.text}")
    
    result = calculate_integral("x**2", "x", "0", "1")
    if result.success:
        print(f"  정적분: {result.text}")
    
    # 4. 운동학 테스트
    print("\n🚀 운동학 테스트:")
    result = kinematics_solver({'v0': 0, 'a': 10, 't': 5}, 'v')
    if result.success:
        print(f"  {result.text}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료")


if __name__ == "__main__":
    test_tools()
