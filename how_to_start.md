docker 시작하기

docker run -it [imagename] -p 8080:80 -p 3000:3000 /bin/bash

python app.py

.env 수정하기

cd /Email 까지 입력, Tab 버튼 누른 후 enter 버튼
vim .env
각 환경변수에 맞는 값을 수정할 수 있습니다.
ADMIN_ID=
ADMIN_PASSWORD=
EMAIL_ADDRESS= # 발신자 이메일
EMAIL_PASSWORD= # 발신자 이메일 비밀번호
SECRET_KEY=
SAVE_PATH=
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT=587
SERVER_URL=
SERVER_PORT=

Server Url은 ipconfig 등을 통해 나오는 IP로 수정해야 합니다. http:// 입력 필수
admin id는 서버 접속 시 아이디입니다. 비밀번호도 동일합니다.
admin password는 python의 hash 함수를 이용해 변환되어 저장됩니다.
smtp 서버 및 포트는 메일 전송 시 필요합니다.
save_path는 텍스트 파일로 로그 저장 시 요구되었습니다.
secret key는 암호화 시 키값으로 요구되는 값입니다. 수정하지 않는 것을 추천합니다.