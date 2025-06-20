from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import uuid
from tools.llm_api import *

from flask import send_from_directory, send_file, abort, jsonify
from agent_0527 import *
import os

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# 新增路由来处理 /factor_data 路径的请求
@app.route('/factor_data/<path:filename>')
def serve_factor_data(filename):
    return send_from_directory('factor_data', filename)

# 新增路由来处理 /files 路径的请求，用于下载Excel文件
@app.route('/files/<path:filename>')
def serve_files(filename):
    try:
        # 获取文件完整路径
        file_path = os.path.join('files', filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            app.logger.error(f"文件不存在: {file_path}")
            abort(404, description=f"文件 {filename} 不存在")
        
        # 检查是否是文件而不是目录
        if not os.path.isfile(file_path):
            app.logger.error(f"路径不是文件: {file_path}")
            abort(400, description="请求的不是文件")
        
        # 文件类型与MIME类型映射
        mime_types = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.txt': 'text/plain'
        }
        
        # 获取文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        
        # 设置MIME类型
        mimetype = mime_types.get(file_ext, 'application/octet-stream')
        
        # 添加自定义响应头确保跨源支持
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        try:
            # 使用send_file并设置as_attachment=True强制下载
            return send_file(
                file_path, 
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
                conditional=True  # 支持断点续传
            ), 200, headers
        except Exception as e:
            app.logger.error(f"发送文件时出错: {str(e)}")
            abort(500, description=f"发送文件时出错: {str(e)}")
            
    except Exception as e:
        app.logger.error(f"处理文件下载请求时出错: {str(e)}")
        return jsonify(error=str(e)), 500, {'Content-Type': 'application/json'}

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/reset_conversation', methods=['POST'])
def reset_conversation():
    """重置聊天对话记录"""
    try:
        global conversation, dt_agent, first_time
        
        # 重置简单对话记录
        conversation.clear()
        conversation.append({'role': 'system', 'content': '你是一个专业的医药学专家，请根据用户的问题，给出专业的回答。'})
        
        # 如果agent已经初始化，也重置agent的对话记录
        if not first_time and 'dt_agent' in globals():
            dt_agent.reset_conversation()
            print("Agent conversation reset successfully")
        
        print("Conversation reset successfully")
        return jsonify({"status": "success", "message": "对话记录已重置"}), 200
        
    except Exception as e:
        print(f"Error resetting conversation: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    print("WebSocket connection established successfully")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('ask_question')
def handle_question(data):
    try:
        user_id = str(uuid.uuid4()) 
        question = data['input']
        model = data.get('model', 'deepseek-chat')  # 默认使用 deepseek-chat
        
        print(f"Received question from {user_id}: {question}")
        print(f"Using model: {model}")
        
        get_llm_ans(question, model)
    except Exception as e:
        print(f"Error handling question: {str(e)}")
        socketio.emit('question_answer', {'content': f'Error: {str(e)}'})
        socketio.emit('stream_end')

first_time = True
def get_llm_ans(question, model):    
    try:
        main_model = model
        tool_model = model
        flash_model = model
        
        global first_time, dt_agent
        if first_time:
            print("Initializing agent for the first time")
            dt_agent = TCMAgent(
                main_model=main_model,
                tool_model=tool_model,
                flash_model=flash_model
            )
            first_time = False
        
        ans = ""
        for char in dt_agent.work_flow(question):
            socketio.emit('question_answer', {'content': char})
            ans += char
            print(char, end="", flush=True)
            
        print("\nResponse completed")
        socketio.emit('stream_end')
    except Exception as e:
        print(f"Error in get_llm_ans: {str(e)}")
        socketio.emit('question_answer', {'content': f'Error: {str(e)}'})
        socketio.emit('stream_end')



conversation = [{'role': 'system', 'content': '你是一个专业的医药学专家，请根据用户的问题，给出专业的回答。'}]
first_time = True
def get_llm_ans_direct(question, model):    
    try:
        conversation.append({'role': 'user', 'content': question})
        ans = ""
        for char in get_llm_answer_converse(conversation, model):
            socketio.emit('question_answer', {'content': char})
            ans += char
            print(char, end="", flush=True)
            
        print("\nResponse completed")
        socketio.emit('stream_end')
    except Exception as e:
        print(f"Error in get_llm_ans: {str(e)}")
        socketio.emit('question_answer', {'content': f'Error: {str(e)}'})
        socketio.emit('stream_end')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)


"""

flask run --host=0.0.0.0 --port=3000

"""
