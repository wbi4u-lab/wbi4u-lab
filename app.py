import os
from flask import Flask, render_template, request, jsonify, Response
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드 및 제미나이 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# 교육 전문가 페르소나 설정 (교실밖의 지적인 평어체 유지)
PERSONAS = {
    "lesson": "당신은 교육 이론과 현장 실무에 모두 능통한 교육과정 전문가다. 교사가 수업 주제를 제시하면, 인문학적 성찰과 학생의 주도성을 끌어내는 구체적이고 실현 가능한 수업과정안을 제안하라. 답변은 항상 전문적이고 지적인 '평어체(한다, 이다)'로 작성하며, 사실에 근거한 명확한 교육적 논리를 포함하라.",
    "management": "당신은 다년간의 풍부한 현장 경험을 가진 학급운영 및 생활지도 전문가다. 학급 내 갈등이나 운영 문제에 대해 감정적 위로보다는, 학생의 성장과 교육적 회복에 초점을 맞춘 실무적이고 지혜로운 해결책을 제시하라. 답변은 항상 단호하면서도 품격 있는 '평어체(한다, 이다)'로 작성하라.",
    "rights": "당신은 교육 관련 법, 제도, 규정에 매우 능통하며 현장 상담 경력이 풍부한 교권 보호 전문가다. 교권 침해 사안에 대해 객관적인 법령과 매뉴얼에 근거하여 실질적인 대응 절차를 차분하게 안내하라. 출처가 불명확한 조언은 엄격히 배제하며, 답변은 신뢰감을 주는 '평어체(한다, 이다)'를 유지하라.",
    "ai_edu": "당신은 AI의 작동 원리를 깊이 이해하고 확고한 기술 윤리적 관점을 가진 에듀테크 철학자다. 교육에 AI를 도입할 때 단순한 도구적 설명을 넘어, 그것이 학습자에게 미치는 영향과 인문학적 쟁점을 함께 짚어내는 균형 잡힌 시각을 제시하라. 답변은 지적이고 논리적인 '평어체(한다, 이다)'로 작성하라."
}

@app.route('/')
def index():
    # 대문 페이지: 연구소의 얼굴
    return render_template('index.html')

@app.route('/classroom_tool.html')
def classroom_tool():
    # 교육 전문가 도구: 지적인 상담의 장
    return render_template('classroom_tool.html')

@app.route('/digital_watch.html')
def digital_watch():
    # 디지털 워치: 실무적인 편의 도구
    return render_template('digital_watch.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message')
    mode = data.get('mode', 'lesson')
    
    base_instruction = PERSONAS.get(mode, PERSONAS["lesson"])
    # 볼드체(**) 방지 및 순수 텍스트 구성 지침 추가
    system_instruction = f"{base_instruction} 단, 답변을 출력할 때 ** 기호(마크다운 볼드체)는 절대 사용하지 마라. 순수한 텍스트로만 형태를 구성하라."
    
    def generate():
        try:
            model = genai.GenerativeModel(
                model_name="models/gemini-2.5-flash", 
                system_instruction=system_instruction
            )
            response = model.generate_content(user_message, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # 에러 발생 시 사용자에게 품격 있게 전달하기 위해 에러 내용만 전송
            # 상세한 429 에러 등은 프론트엔드(HTML)의 catch 문에서 처리됨
            yield f"Error: {str(e)}"
            
    return Response(generate(), content_type='text/plain; charset=utf-8')

if __name__ == '__main__':
    # 렌더 배포 환경에 맞게 호스트와 포트 설정 가능 (로컬 테스트용 debug=True)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

