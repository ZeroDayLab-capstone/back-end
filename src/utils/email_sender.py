import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_reset_code_email(to_email: str, code: str) -> bool:
    subject = "🔐 비밀번호 재설정 인증코드"
    body = f"아래 인증코드를 입력하세요:\n\n✅ 인증코드: {code}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print("\n🛑 이메일 전송 실패 로그 🛑")
        print("에러 종류:", type(e).__name__)
        print("에러 메시지:", str(e))
        return False

# 테스트용 단독 실행 코드
if __name__ == "__main__":
    result = send_reset_code_email("test@example.com", "123456")
    print("전송 결과:", result)
