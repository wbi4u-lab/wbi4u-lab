import os
from flask import Flask, render_template, request, Response, abort
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 및 제미나이 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# templates 폴더 위치를 명시적으로 지정
app = Flask(__name__, template_folder='templates')

PERSONAS = {
    "lesson": "당신은 교육과정 전문가다. 전문적이고 지적인 '평어체'로 답변하라.",
    "management": "당신은 학급운영 전문가다. 실무적이고 지혜로운 '평어체' 해결책을 제시하라.",
    "rights": "당신은 교권 보호 전문가다. 객관적 법령에 근거하여 '평어체'로 안내하라.",
    "ai_edu": "당신은 에듀테크 철학자다. 지적이고 논리적인 '평어체'로 작성하라."
}

@app.route('/')
def index():
    # 대문 페이지는 항상 index.html
    return render_template('index.html')

@app.route('/<path:filename>')
def auto_serve(filename):
    # .html 확장자가 없으면 붙여주는 유연함 발휘
    if not filename.endswith('.html'):
        target_file = filename + '.html'
    else:
        target_file = filename
        
    # 실제 templates 폴더에 파일이 존재하는지 지적으로 확인
    template_path = os.path.join(app.template_folder, target_file)
    if os.path.exists(template_path):
        return render_template(target_file)
    else:
        # 파일이 없으면 404 에러를 내보내어 혼선을 방지함
        abort(404)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message')
    mode = data.get('mode', 'lesson')
    
    system_instruction = PERSONAS.get(mode, PERSONAS["lesson"]) + " 단, 마크다운 볼드체(**)는 사용하지 마라."
    
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
