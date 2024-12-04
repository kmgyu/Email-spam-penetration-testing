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

app = Flask(__name__)
csrf = CSRFProtect()
load_dotenv()
# SMTP 서버 설정
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'dage8044@gmail.com'  # 발신자 이메일
EMAIL_PASSWORD = 'fisupsylmjwhskso'       # 발신자 이메일 비밀번호
app.config['SECRET_KEY'] = 'root'  # 시크릿 키 설정
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=5)  # 토큰 만료 시간 설정 (1시간)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

# 보안을 위한 jwttoken 사용하기
jwt = JWTManager(app)
temporary_tokens = {}
app.config['WTF_CSRF_ENABLED'] = True
csrf.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 입력폼에서 아이디와 비밀번호를 받아옴
        user_id = request.form['id']
        password = request.form['pw']
        
        admin_id = os.getenv('ADMIN_ID')
        admin_password = os.getenv('ADMIN_PASSWORD')
        print(user_id, password)
        print(admin_id, admin_password)

        # 데이터베이스에서 사용자 정보를 검색
        if user_id == admin_id and password == admin_password:
            # 로그인 성공 시 세션에 사용자 정보 저장
            session['username'] = user_id
            return redirect(url_for('send_email_mainform', username=user_id))
        else:
            # 실패 시 에러 메시지와 함께 로그인 화면 반환
            return render_template('index.html', error="아이디 또는 비밀번호가 잘못되었습니다.")
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

@app.route('/send_email', methods=['POST'])
def send_email():
    selected_users = request.form['selected_users']
    users = json.loads(selected_users)  # ["email1|name1", "email2|name2", ...]

    product_name = request.form['product_name']
    payment_time = request.form['payment_time']
    order_number = request.form['order_number']
    payment_method = request.form['payment_method']
    amount = request.form['amount']

    # SMTP 서버를 통해 이메일 전송
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            for user_data in users:
                email, name = user_data.split('|')

                # 이메일 메시지 작성
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = email
                msg['Subject'] = f"[COOPANG 결제] 결제가 완료되었습니다."

                html_content = render_template(
                    'email_template.html',
                    customer_name=name,
                    product_name=product_name,
                    payment_time=payment_time,
                    order_number=order_number,
                    payment_method=payment_method,
                    amount=amount
                )
                msg.attach(MIMEText(html_content, 'html'))
                server.send_message(msg)

        return "이메일 전송 성공!"
    except Exception as e:
        return f"이메일 전송 실패: {str(e)}"

@app.route('/send_email_mainform/<username>', methods=['GET', 'POST'])
def send_email_mainform(username):
    if request.method == 'POST': 
        data = request.get_json()  # JSON 데이터 수신
        selected_users = data['selected_users']  # ["email1|name1", "email2|name2", ...]
        email_title = data['email_title']
        email_content = data['email_content']
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
            # SMTP 서버를 통해 이메일 전송
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

                for user_data in selected_users:
                    email, name = user_data.split('|')

                    # 이메일 메시지 작성
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_ADDRESS
                    msg['To'] = email
                    msg['Subject'] = email_title
                    msg.attach(MIMEText(email_content_with_css, 'html'))
                    server.send_message(msg)

            return "이메일 전송 성공!"
        except Exception as e:
            return f"이메일 전송 실패: {str(e)}"
    else:
        name = session.get('username')
        return render_template('email_mainform.html', name=name)



if __name__ == '__main__':
    app.run(debug=True)
