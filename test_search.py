import requests

import json


# Flask 애플리케이션이 실행 중인 주소
FLASK_APP_URL = "http://127.0.0.1:5000/search"

# 검색할 데이터 (잠실 지역)
search_data = {
"search_date": "2025-07-21",  # 특정 날짜 필터링이 필요하면 여기에 'YYYY-MM-DD' 형식으로 입력
"region": "잠실",
"time": ""  # 특정 시간 필터링이 필요하면 여기에 'HH:MM' 형식으로 입력
}

try:
    response = requests.post(FLASK_APP_URL, data=search_data)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

    results = response.json()

    with open("jamsil_search_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("잠실 지역 검색 결과가 jamsil_search_results.json 에 저장되었습니다.")

except requests.exceptions.RequestException as e:
    print(f"요청 오류 발생: {e}")
    print("Flask 애플리케이션이 실행 중인지 확인해주세요.")
except json.JSONDecodeError:
    print("JSON 응답을 파싱하는 데 실패했습니다. API 응답을 확인해주세요.")