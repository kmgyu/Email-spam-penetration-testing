import sqlite3

# 데이터베이스 파일 생성
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_counts (
    email TEXT PRIMARY KEY,
    counts INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_logs (
    email TEXT,
    timestamp TEXT
)
''')

# 샘플 데이터 삽입
cursor.execute("INSERT INTO user_counts (email, counts) VALUES ('test2@example.com', 1)")
cursor.execute("INSERT INTO user_logs (email, timestamp) VALUES ('test2@example.com', '2024-12-15 07:01:40')")
cursor.execute("INSERT INTO user_logs (email, timestamp) VALUES ('test2@example.com', '2024-12-11 02:05:52')")

# 변경사항 커밋 및 종료
conn.commit()
conn.close()
