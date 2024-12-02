from flask import Flask, render_template, request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

app = Flask(__name__)

# SMTP 서버 설정
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'dage8044@gmail.com'  # 발신자 이메일
EMAIL_PASSWORD = 'fisupsylmjwhskso'       # 발신자 이메일 비밀번호

@app.route('/')
def index():
    return render_template('email_form.html') 

@app.route('/send_email', methods=['POST'])
def send_email():
    recipient = request.form['recipient']
    customer_name = request.form['customer_name']
    product_name = request.form['product_name']
    payment_time = request.form['payment_time']
    order_number = request.form['order_number']
    payment_method = request.form['payment_method']
    amount = request.form['amount']

    # 이메일 메시지 작성
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = f"[COOPANG 결제] 결제가 완료되었습니다."

    # HTML 템플릿 로드 및 데이터 삽입
    html_content = render_template('email_template.html', 
                                   customer_name=customer_name,
                                   product_name=product_name,
                                   payment_time=payment_time,
                                   order_number=order_number,
                                   payment_method=payment_method,
                                   amount=amount)
    msg.attach(MIMEText(html_content, 'html'))

    # SMTP 서버를 통해 이메일 전송
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return "이메일 전송 성공!"
    except Exception as e:
        return f"이메일 전송 실패: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
