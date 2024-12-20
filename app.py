from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import hashlib
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
import datetime
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
#sqllite
import sqlite3 as sql

#import pyshorteners

app = Flask(__name__)
csrf = CSRFProtect()
load_dotenv()
# SMTP 서버 설정
# SMTP_SERVER = os.getenv('SMTP_SERVER')
# SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # 발신자 이메일
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')       # 발신자 이메일 비밀번호
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # 시크릿 키 설정
SAVE_PATH = os.getenv('SAVE_PATH')
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=5)  # 토큰 만료 시간 설정 (1시간)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['SESSION_COOKIE_SECURE'] = True
SERVER_URL = os.getenv('SERVER_URL')
SERVER_PORT = os.getenv('SERVER_PORT')
SERVER = f'{SERVER_URL}:{SERVER_PORT}'
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
temporary_tokens = {}
# app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_ENABLED'] = False
# csrf.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 입력폼에서 아이디와 비밀번호를 받아옴
        user_id = request.form['id']
        password = request.form['pw']
        
        admin_id = os.getenv('ADMIN_ID')
        admin_password = os.getenv('ADMIN_PASSWORD')

        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # 사용자 인증
        if user_id == admin_id and password == admin_password:
            # 로그인 성공 시 세션에 사용자 정보 저장
            session['username'] = user_id
            return redirect(url_for('send_email_mainform', username=user_id))
        else:
            flash("아이디 또는 비밀번호가 잘못되었습니다.")
            return render_template('index.html')
    else:
        # GET 요청일 경우 세션 확인
        if 'username' in session:
            return redirect(url_for('send_email_mainform', username=session['username']))
        return render_template('index.html')

# 로그아웃 시 토큰 삭제
@app.route('/logout', methods = ['GET','POST'])
def logout():
    session.pop('username', None)
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('access_token_cookie')
    return response

@app.route('/send_email_mainform/<username>', methods=['GET', 'POST'])
def send_email_mainform(username):
    if request.method == 'POST': 
        data = request.get_json()  # JSON 데이터 수신

        if not data:
            return jsonify({"message": "유효하지 않은 요청 데이터입니다."}), 400
        
        selected_users = data['selected_users']  # ["email1|name1", "email2|name2", ...]
        email_title = data['email_title']
        email_content = data['email_content']
        email_link = data['email_link']
        print(selected_users)
        print(email_title)
        print(email_content)
        if not selected_users:
            return jsonify({"message": "수신자 정보가 없습니다."}), 400

        # CSS 추가 (p 태그의 margin 제거)
        email_content_with_css = f"""
        <html>
            <head>
                <style>
                    p, h1, h2, h3, h4, h5, h6 {{ margin: 0px; }}
                </style>
            </head>
            <body>
                {email_content}
            </body>
        </html>
        """

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

                for user_data in selected_users:
                    try:
                        email, name = user_data.split('|')

                        phishing_url = f"{SERVER}/spam_warning/search?email="+email #.split('@')[0]                       
                        personalized_content = email_content_with_css + f"""
                            <p> <a href="{phishing_url}">
                            {email_link}</a> </p> 
                        """

                        # 이메일 메시지 작성
                        print(personalized_content)
                        print(f"phishing_url: ${phishing_url}")
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_ADDRESS
                        msg['To'] = email
                        msg['Subject'] = email_title
                        msg.attach(MIMEText(personalized_content, 'html'))
                        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
                    except Exception as user_error:
                        print(f"수신자 {user_data} 처리 중 오류 발생: {user_error}")
                        continue  # 현재 사용자의 메일 전송 실패 시 다음 사용자로 진행

            return jsonify({"message": "이메일 전송 성공!"}), 200
        except Exception as e:
            return jsonify({"message": f"이메일 전송 실패: {str(e)}"}), 500
    else:
        name = session.get('username', username)
        return render_template('email_mainform.html', name=name)

# # 사용자 데이터를 파일에 저장할 함수
# def save_data_to_file():
#     global global_count, users_info
#     with open(SAVE_PATH+'user_data.txt', 'w') as f:
#         f.write(f"{global_count}\n")
#         for user, data in users_info.items():
#             record_line = ",".join(data['record'])
#             f.write(f"{user}/{data['counts']}/{record_line}\n")

# # 파일에서 사용자 데이터를 불러오는 함수
# def load_data_from_file():
#     global global_count, users_info
#     if os.path.exists(SAVE_PATH+'user_data.txt'):
#         with open(SAVE_PATH+'user_data.txt', 'r') as f:
#             lines = f.readlines()
#             if lines:
#                 global_count = int(lines[0].strip())
#                 for line in lines[1:]:
#                     parts = line.strip().split('/')
#                     if len(parts) == 3:
#                         user, count, records = parts
#                         users_info[user] = {
#                             'counts': int(count),
#                             'record': records.split(',') if records else []
#                         }

# # 접속 기록을 저장할 리스트
# global_count = 0
# users_info = {}

# load_data_from_file()
# @app.route('/spam_warning/search', methods=['GET'])
# def search_spam_warning():
#     global global_count, user_counts, access_records
#     # 쿼리 스트링에서 'user_id' 파라미터를 받아오기
#     mail = request.args.get('mail')
#     check = 'check' in request.args
    
#     # 쿼리스트링에서 'check'과 'user_id' 외의 다른 파라미터가 있으면 오류 처리
#     invalid_params = [key for key in request.args.keys() if key not in ['check', 'mail']]
#     if invalid_params:
#         return f"Invalid parameters: {', '.join(invalid_params)}", 404
    
#     # 'check' 파라미터가 있을 때 모든 유저의 진입 기록을 보여주기
#     if check:
#         summary_info = {} # time stamper
#         for user, info in users_info.items():
#             summary_info[user] = {
#                 'counts' : info['counts'],
#                 'first stamp' : min(info['record']),
#                 'last stamp' : max(info['record']),
#             }
#         return render_template('check_user_counts.html', summary_info=summary_info, global_count=global_count, users_info=users_info)
    
#     if mail:
#         # 해당 유저의 카운트 증가
#         if mail not in users_info:
#             users_info[mail] = {'counts':0, 'record':[]}
#         users_info[mail]['counts'] += 1
#         timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         users_info[mail]['record'].append(timestamp)
#         # 전체 카운트 증가
#         global_count += 1
#         save_data_to_file()
        
#     # 결과를 출력할 템플릿으로 전달
#     return render_template('search_spam_warning.html')

#########sqlite사용 부분############

def init_db():
    with sql.connect(SAVE_PATH + 'data.db') as conn:
        cursor = conn.cursor()
        # 카운팅용 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_counts (
                email TEXT PRIMARY KEY,
                counts INTEGER DEFAULT 0
            )
        ''')
        # 접속 기록용 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                timestamp TEXT NOT NULL
                
            )
        ''')

        
        conn.commit()


def save_user_count(email):
    with sql.connect(SAVE_PATH + 'data.db') as conn:
        cursor = conn.cursor()
        
        # 이메일별 카운팅 업데이트
        cursor.execute('SELECT counts FROM user_counts WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            count = result[0] + 1
            cursor.execute('UPDATE user_counts SET counts = ? WHERE email = ?', (count, email))
        else:
            cursor.execute('INSERT INTO user_counts (email, counts) VALUES (?, ?)', (email, 1))
        
        conn.commit()

def save_user_log(email):
    with sql.connect(SAVE_PATH + 'data.db') as conn:
        cursor = conn.cursor()
        
        # 현재 시간 생성
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('INSERT INTO user_logs (email, timestamp) VALUES (?, ?)', (email, timestamp))
        
        conn.commit()

def get_global_count():
    with sql.connect(SAVE_PATH + 'data.db') as conn:
        cursor = conn.cursor()

        # 전체 사용자 카운트 가져오기
        cursor.execute('SELECT SUM(counts) FROM user_counts')
        result = cursor.fetchone()

        return result[0] if result and result[0] else 0
    
# Flask route 수정
@app.route('/spam_warning/search', methods=['GET'])
def search_spam_warning():
    email = request.args.get('email')
    check = 'check' in request.args

    invalid_params = [key for key in request.args.keys() if key not in ['check', 'email']]
    if invalid_params:
        return f"Invalid parameters: {', '.join(invalid_params)}", 404

    if check:
        all_users = get_user_data()  # 사용자 데이터 가져오기
        summary_info = {
            user[0]: {  
                'counts': user[1],  # 접속 횟수
                'first stamp': min(log[1] for log in all_users['logs'] if log[0] == user[0]),  # 첫 접속 시간
                'last stamp': max(log[1] for log in all_users['logs'] if log[0] == user[0])  # 마지막 접속 시간
            }
            for user in all_users['counts']  # 'counts'에서 사용자 정보를 가져옵니다.
        }
        
        users_info = {
            user[0]: {  
                'record': [log[1] for log in all_users['logs'] if log[0] == user[0]]  # 접속 기록
            }
            for user in all_users['counts']  # 'counts'에서 사용자 정보를 가져옵니다.
        }
        return render_template('check_user_counts.html', users_info=users_info, summary_info=summary_info, global_count=get_global_count())

    if email:      
        save_user_log(email)
        save_user_count(email)

    return render_template('search_spam_warning.html')

def get_user_data(email=None):
    with sql.connect(SAVE_PATH + 'data.db') as conn:
        cursor = conn.cursor()
        
        if email:
            # 특정 이메일의 카운트 및 접속 기록 가져오기
            cursor.execute('SELECT counts FROM user_counts WHERE email = ?', (email,))
            count_result = cursor.fetchone()
            cursor.execute('SELECT timestamp FROM user_logs WHERE email = ?', (email,))
            log_results = cursor.fetchall()
            
            return {
                'email': email,
                'count': count_result[0] if count_result else 0,
                'logs': [log[0] for log in log_results]
            }
        else:
            # 모든 이메일의 데이터 가져오기
            cursor.execute('SELECT * FROM user_counts')
            counts = cursor.fetchall()
            
            cursor.execute('SELECT email, timestamp FROM user_logs')
            logs = cursor.fetchall()
            
            return {
                'counts': counts,
                'logs': logs
            }

@app.route('/preview_test', methods=['GET'])
def preview_test(id="admin"):
    # 원본 URL 설정
    original_url = f"{SERVER}/spam_warning/search?email="+id
    
    try:
        phishing_url = original_url

        return jsonify({
            "original_url": original_url,
            "phishing_url": phishing_url
        })
    except Exception as e:
        return jsonify({
            "error": "그냥 실패했습니다.",
            "details": str(e)
        }), 500
        
@app.route('/send_phishing_mail/<email_addr>', methods=['GET'])
def send_phishing_mail(email_addr):
    """
         주석!!!
    """
    if not email_addr:
        return jsonify({"message": "mail 파라미터가 필요합니다."}), 400

    try:
        original_url = f"{SERVER}/spam_warning/search?email={email_addr}"  # URL 포맷
        phishing_url = original_url
        return jsonify({
            "original_url": original_url,
            "phishing_url": phishing_url
        })
    except Exception as e:
        return jsonify({
            "error": "그냥 매우 실패했습니다.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)
