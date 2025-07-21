# Python 3.10을 기반 이미지로 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 환경 변수 (API 키는 외부에서 주입될 것임)
# KAKAO_API_KEY는 Elastic Beanstalk 환경 변수에서 제공

# 컨테이너가 5000번 포트를 노출하도록 설정
EXPOSE 5000

# 애플리케이션 실행 (gunicorn 사용)
# 5000번 포트로 외부 요청을 받음
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
