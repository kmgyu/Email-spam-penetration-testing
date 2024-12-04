from flask import Flask, render_template, request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json

app = Flask(__name__)

# SMTP 서버 설정
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'dage8044@gmail.com'  # 발신자 이메일
EMAIL_PASSWORD = 'fisupsylmjwhskso'       # 발신자 이메일 비밀번호

@app.route('/')
def index():
    return render_template('email_test.html')
    # return render_template('email_form.html') 

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

@app.route('/send_email_test', methods=['POST'])
def send_email_test():
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
    print(email_content_with_css)
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
    
if __name__ == '__main__':
    app.run(debug=True)
