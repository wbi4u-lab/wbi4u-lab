import os
from flask import Flask, render_template, request, Response, abort
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경 변수 및 제미나이 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Flask 앱 설정 (templates 폴더를 명시적으로 지정)
app = Flask(__name__, template_folder='templates')

# 3. 교육 전문가 페르소나 설정
PERSONAS = {
    "lesson": "당신은 교육과정 전문가다. 전문적이고 지적인 '평어체'로 답변하라.",
    "management": "당신은 학급운영 전문가다. 실무적이고 지혜로운 '평어체' 해결책을 제시하라.",
    "rights": "당신은 교권 보호 전문가다. 객관적 법령에 근거하여 '평어체'로 안내하라.",
    "ai_edu": "당신은 에듀테크 철학자다. 지적이고 논리적인 '평어체'로 작성하라."
}

# 4. 라우팅 설정: 메인 대문
@app.route('/')
def index():
    return render_template('index.html')

# 5. 라우팅 설정: 자동 경로 시스템 (Auto-Routing)
@app.route('/<path:filename>')
def auto_serve(filename):
    # 파일명에서 .html 확장자 처리
    target_file = filename if filename.endswith('.html') else f"{filename}.html"
    
    # templates 폴더 내 실제 파일 존재 여부 확인
    template_full_path = os.path.join(app.template_folder, target_file)
    
    if os.path.exists(template_full_path):
        return render_template(target_file)
    else:
        # 파일이 없으면 품격 있게 404 반환
        return abort(404)

# 6. 인공지능 대화 로직
@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message')
    mode = data.get('mode', 'lesson')
    
    # 볼드체 사용 금지 지침 포함
    system_instruction = PERSONAS.get(mode, PERSONAS["lesson"]) + " 단, 답변 시 마크다운 볼드체(**)는 절대 사용하지 마라."
    
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
            yield f"Error: {str(e)}"
            
    return Response(generate(), content_type='text/plain; charset=utf-8')

# 7. 서버 실행 설정
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
