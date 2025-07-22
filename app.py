from flask import Flask, request, jsonify, render_template
import requests
import json
import math
import os
from datetime import datetime, time, timedelta

app = Flask(__name__)

# 카카오 로컬 API 키 (환경 변수에서 읽어옴)
KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')

def get_coords_from_address(address):
    """
    주소를 입력받아 카카오 로컬 API를 통해 위도, 경도 좌표를 반환합니다.
    """
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={address}"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result['documents']:
            x = float(result['documents'][0]['x'])  # 경도
            y = float(result['documents'][0]['y'])  # 위도
            return y, x
    except requests.exceptions.RequestException as e:
        print(f"카카오 API 요청 오류: {e}")
    except (KeyError, IndexError):
        print("주소로부터 좌표를 찾을 수 없습니다.")
    return None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    두 지점의 위도, 경도를 받아 거리를 킬로미터(km) 단위로 반환합니다.
    """
    R = 6371  # 지구의 반지름 (km)
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def find_courts(search_date, target_region, target_time):
    """
    아이엠그라운드에서 조건에 맞는 풋살장을 찾아 그룹화하여 반환합니다.
    """
    url = "https://www.iamground.kr/futsal/s/_f.php"
    payload = {
        "limit": 200,
        "offset": 0,
        "from": "full_info",
        "search_date": search_date,
    }
    if target_region:
        payload["search_word"] = target_region

    print("Sending payload to iamground.kr:", payload)

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()

        # API 응답 전체를 파일로 저장 (디버깅용)
        with open("iamground_raw_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Raw API response saved to iamground_raw_response.json")

        courts_dict = {}
        center_lat, center_lon = None, None
        if target_region:
            center_lat, center_lon = get_coords_from_address(target_region)

        for court in data.get("list", []):
            is_in_target_region_by_name = False
            if target_region and target_region in court.get("fAddress", ""):
                is_in_target_region_by_name = True

            is_nearby_geographically = False
            if center_lat and center_lon:
                court_lat = float(court.get("latitude", 0))
                court_lon = float(court.get("longitude", 0))
                if court_lat and court_lon:
                    # '근처 동네'를 포함하기 위한 더 넓은 반경 (예: 5km)
                    NEARBY_RADIUS_KM = 5.0
                    if haversine_distance(center_lat, center_lon, court_lat, court_lon) <= NEARBY_RADIUS_KM:
                        is_nearby_geographically = True
            
            # 이름으로 일치하거나 지리적으로 가까운 경우 포함
            if not is_in_target_region_by_name and not is_nearby_geographically:
                continue

            court_name = court.get("fName")
            court_address = court.get("fAddress")
            # 이름과 주소를 키로 사용하여 동일한 구장을 식별
            court_key = (court_name, court_address)

            if court_key not in courts_dict:
                courts_dict[court_key] = {
                    "name": court_name,
                    "address": court_address,
                    "latitude": court.get("latitude"),
                    "longitude": court.get("longitude"),
                    "available_times": []
                }

            # 시간 정보 추가
            for reservation in court.get("reserv", []):
                # search_date 필터링 추가
                if search_date and reservation.get("start_date") != search_date:
                    continue

                current_res_time_str = reservation.get("start_time")
                match_type = ""

                if target_time:
                    try:
                        # target_time과 reservation 시간을 time 객체로 변환
                        target_time_obj = datetime.strptime(target_time, "%H:%M").time()
                        res_time_obj = datetime.strptime(current_res_time_str, "%H:%M").time()

                        # 시간 차이 계산 (timedelta 사용)
                        # 날짜가 다르더라도 시간만 비교하기 위해 임의의 동일한 날짜를 사용
                        dummy_date = datetime(2000, 1, 1)
                        time_diff = abs(datetime.combine(dummy_date, target_time_obj) - datetime.combine(dummy_date, res_time_obj))

                        # 정확히 일치하는 경우
                        if time_diff == timedelta(minutes=0):
                            match_type = "exact"
                        # 근방 시간대 (예: ±30분)
                        elif time_diff <= timedelta(minutes=30):
                            match_type = "nearby"
                        else:
                            continue # 30분 이상 차이나면 건너뜀
                    except ValueError:
                        # 시간 형식 파싱 오류 시 건너뜀
                        continue
                else:
                    # target_time이 없으면 모든 시간 슬롯을 포함
                    match_type = "any"

                # target_time이 있는데 match_type이 설정되지 않았다면 (필터링된 경우) 건너뜀
                if target_time and not match_type:
                    continue

                time_slot = {
                    "date": reservation.get("start_date"),
                    "time": f'{reservation.get("start_time")} - {reservation.get("end_time")}',
                    "price": reservation.get("unit_price"),
                    "match_type": match_type # 매치 타입 추가
                }
                # 동일한 시간 정보가 이미 추가되었는지 확인하여 중복 방지
                if time_slot not in courts_dict[court_key]["available_times"]:
                    courts_dict[court_key]["available_times"].append(time_slot)
        
        # 딕셔너리의 값들을 리스트로 변환하여 반환
        return list(courts_dict.values())
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []
    except json.JSONDecodeError:
        (print("JSON 파싱 오류"))
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

    if time:
        # time이 HH:MM:SS 형식으로 들어올 경우 HH:MM으로 자름
        if len(time) > 5:
            time = time[:5]
        # HH:MM 형식인 경우 그대로 사용

    courts = find_courts(search_date, region, time)
    return jsonify(courts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
