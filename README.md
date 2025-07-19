# 풋살장 예약 알리미 (futsal-notifier)

'iamground.kr' 웹사이트에서 특정 조건에 맞는 풋살장 예약 정보를 스크래핑하여 사용자에게 보여주는 Flask 기반 웹 애플리케이션입니다.

## 주요 기능

- **풋살장 검색**: 날짜, 지역, 시간을 기준으로 예약 가능한 풋살장을 검색합니다.
- **향상된 지역 검색**: 입력된 지역명과 일치하는 풋살장뿐만 아니라, 해당 지역의 중심으로부터 5km 이내의 지리적으로 가까운 풋살장도 함께 검색합니다.
- **유연한 시간 검색**: 특정 시간을 검색할 때, 정확히 일치하는 시간대와 ±30분 이내의 근방 시간대를 구분하여 보여줍니다.
- **실시간 정보 제공**: 'iamground.kr'의 최신 예약 정보를 직접 조회하여 보여줍니다.
- **간편한 웹 인터페이스**: 사용자가 쉽게 검색 조건을 입력하고 결과를 확인할 수 있는 웹 페이지를 제공합니다.

## 기술 스택

- **Backend**: Flask, requests, datetime (Python 표준 라이브러리)
- **Frontend**: HTML, CSS, JavaScript
- **외부 API**: Kakao Local API (지역 좌표 변환), iamground.kr API (풋살장 정보)

## 파일 구조

```
futsal-notifier/
├── app.py              # Flask 애플리케이션 (풋살장 검색 및 필터링 로직 포함)
├── scraper.py          # (현재 사용되지 않음) 풋살장 정보 스크래핑 스크립트
├── requirements.txt    # Python 의존성 파일
├── templates/
│   └── index.html      # 메인 웹 페이지 (검색 UI 및 결과 표시)
└── README.md           # 프로젝트 설명 파일
```

## 실행 방법

1.  **저장소 복제**
    ```bash
    git clone https://github.com/your-username/futsal-notifier.git
    cd futsal-notifier
    ```

2.  **가상 환경 생성 및 활성화**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```

3.  **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Kakao Local API 키 설정**
    `app.py` 파일 내 `KAKAO_API_KEY` 변수에 본인의 카카오 개발자 계정에서 발급받은 REST API 키를 입력해야 합니다.
    ```python
    KAKAO_API_KEY = 'YOUR_KAKAO_REST_API_KEY'
    ```

5.  **Flask 애플리케이션 실행**
    ```bash
    python app.py
    ```

6.  웹 브라우저에서 `http://127.0.0.1:5000`으로 접속합니다.

## 개선 제안

-   **알림 기능 추가**: 특정 조건의 풋살장이 예약 가능할 때 사용자에게 이메일, SMS 등으로 알림을 보내는 기능을 추가할 수 있습니다.
-   **주기적인 데이터 업데이트 및 캐싱**: `iamground.kr` API 호출 횟수를 줄이기 위해 주기적으로 데이터를 가져와 캐싱하거나 데이터베이스에 저장하는 기능을 고려할 수 있습니다.
-   **사용자 인터페이스 개선**: 날짜 및 시간 선택을 위한 달력 및 시간 선택 위젯을 더욱 사용자 친화적으로 개선하고, 검색 결과를 필터링하거나 정렬하는 기능을 추가하여 사용자 편의성을 높일 수 있습니다.
-   **오류 처리 강화**: API 호출 실패 시 사용자에게 더 명확한 메시지를 제공하고, 네트워크 오류 등에 대한 견고한 처리를 추가합니다.
-   **성능 최적화**: 대량의 데이터를 처리할 때 검색 및 필터링 성능을 최적화하는 방법을 고려할 수 있습니다.
