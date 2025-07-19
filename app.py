
from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)

def find_courts(search_date, target_region, target_time):
    """
    아이엠그라운드에서 조건에 맞는 풋살장을 찾아 반환합니다.
    """
    url = "https://www.iamground.kr/futsal/s/_f.php"
    payload = {
        "limit": 100, # 더 많은 결과를 가져오기 위해 limit 증가
        "offset": 0,
        "from": "full_info",
        "search_date": search_date,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()

        available_courts = []
        for court in data.get("list", []):
            # 지역 필터링
            if target_region and target_region not in court.get("fAddress", ""):
                continue

            # 시간 필터링
            for reservation in court.get("reserv", []):
                if not target_time or reservation.get("start_time") == target_time:
                    available_courts.append({
                        "name": court.get("fName"),
                        "address": court.get("fAddress"),
                        "time": f'{reservation.get("start_time")} - {reservation.get("end_time")}',
                        "price": reservation.get("unit_price")
                    })
                    if target_time: # 특정 시간을 찾으면 다음 구장으로
                        break
        return available_courts

    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []
    except json.JSONDecodeError:
        print("JSON 파싱 오류")
        return []

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """검색 조건에 따라 풋살장을 검색하고 결과를 반환합니다."""
    search_date = request.form.get('search_date')
    region = request.form.get('region')
    time = request.form.get('time')

    # 시간 포맷 정리 (예: 18:00)
    if time:
        time = time + ":00" if len(time) == 5 else time

    courts = find_courts(search_date, region, time)
    return jsonify(courts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
