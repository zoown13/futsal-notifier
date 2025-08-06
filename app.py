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

def find_courts(search_date, target_time, distance_limit, time_range_minutes, target_region=None, lat=None, lon=None):
    """
    아이엠그라운드의 새로운 API를 사용하여 조건에 맞는 풋살장을 찾아 그룹화하여 반환합니다.
    """
    url = "https://prod-api.iamground.kr/api/v1/stadiums"
    all_courts_data = []
    page = 0
    size = 50  # 한 번에 50개씩 요청

    center_lat, center_lon = None, None
    if lat and lon:
        center_lat, center_lon = float(lat), float(lon)
    elif target_region:
        center_lat, center_lon = get_coords_from_address(target_region)

    if not center_lat or not center_lon:
        print("좌표를 얻을 수 없어 검색을 중단합니다.")
        return []

    while True:
        start_date_obj = datetime.strptime(search_date, "%Y-%m-%d")
        end_date_obj = start_date_obj + timedelta(days=1)
        search_start_at_str = start_date_obj.strftime("%Y-%m-%d 00:00")
        search_end_at_str = end_date_obj.strftime("%Y-%m-%d 00:00")

        params = {
            "stadium_type": "FUT",
            "search_start_at": search_start_at_str,
            "search_end_at": search_end_at_str,
            "search_longitude": center_lon,
            "search_latitude": center_lat,
            "page": page,
            "size": size
        }
        print("Sending GET request to iamground.kr API:", params)

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json().get('data', {})
            current_list = data.get('list', [])

            if not current_list:
                break

            courts_within_distance = []
            all_courts_in_page_are_outside_limit = True

            for court_data in current_list:
                court_lat = court_data.get("latitude")
                court_lon = court_data.get("longitude")
                if court_lat and court_lon:
                    distance = haversine_distance(center_lat, center_lon, float(court_lat), float(court_lon))
                    if distance <= distance_limit:
                        # 개선 1: 구장 이름 조합 및 데이터 정제
                        facility_name = court_data.get("facility_name", "")
                        stadium_name = court_data.get("stadium_name", "")
                        full_name = f"{facility_name} ({stadium_name})" if stadium_name else facility_name
                        court_data["full_name"] = full_name
                        court_data["is_indoor_bool"] = court_data.get("is_indoor") == "Y"
                        
                        courts_within_distance.append(court_data)
                        all_courts_in_page_are_outside_limit = False

            all_courts_data.extend(courts_within_distance)

            if all_courts_in_page_are_outside_limit:
                print(f"페이지 {page}의 모든 경기장이 {distance_limit}km를 초과하여 검색을 중단합니다.")
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return []
        except json.JSONDecodeError:
            print("JSON 파싱 오류")
            return []

    # 개선 2: 고유 ID(id)를 기준으로 구장을 그룹화
    courts_dict = {}
    for court in all_courts_data:
        court_id = court.get("id")
        if court_id not in courts_dict:
            courts_dict[court_id] = {
                "id": court_id,
                "name": court.get("full_name"),
                "address": court.get("address"),
                "latitude": court.get("latitude"),
                "longitude": court.get("longitude"),
                "is_indoor": court.get("is_indoor_bool"),
                "available_times": []
            }

        for reservation in court.get("schedule_list", []):
            start_at_str = reservation.get("start_at", "")
            if not start_at_str or search_date not in start_at_str:
                continue

            current_res_time_str = start_at_str.split(' ')[1]
            match_type = ""

            if target_time:
                try:
                    target_time_obj = datetime.strptime(target_time, "%H:%M").time()
                    res_time_obj = datetime.strptime(current_res_time_str, "%H:%M").time()
                    dummy_date = datetime(2000, 1, 1)
                    time_diff = abs(datetime.combine(dummy_date, target_time_obj) - datetime.combine(dummy_date, res_time_obj))

                    if time_diff == timedelta(minutes=0):
                        match_type = "exact"
                    elif time_diff <= timedelta(minutes=time_range_minutes):
                        match_type = "nearby"
                    else:
                        continue
                except (ValueError, IndexError):
                    continue
            else:
                match_type = "any"

            if target_time and not match_type:
                continue

            time_slot = {
                "date": start_at_str.split(' ')[0],
                "time": f'{current_res_time_str} - {reservation.get("end_time")}',
                "price": reservation.get("match_price"),
                "match_type": match_type
            }
            if time_slot not in courts_dict[court_id]["available_times"]:
                courts_dict[court_id]["available_times"].append(time_slot)

    return list(courts_dict.values())

@app.route('/search', methods=['POST'])
def search():
    """검색 조건에 따라 풋살장을 검색하고 결과를 반환합니다."""
    search_date = request.form.get('search_date')
    region = request.form.get('region')
    time = request.form.get('time')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    # 개선 3: 사용자가 선택한 검색 반경 값 (기본값 5km)
    distance_limit = request.form.get('distance_limit', 5, type=int)

    if time and len(time) > 5:
        time = time[:5]

    time_range_minutes = request.form.get('time_range_minutes', 30, type=int)
    courts = find_courts(search_date, time, distance_limit, time_range_minutes, target_region=region, lat=lat, lon=lon)
    return jsonify(courts)

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
