
import requests
import json

# 아이엠그라운드 API 정보
url = "https://www.iamground.kr/futsal/s/_f.php"
search_date = "2025-07-21"  # 원하는 날짜로 변경 가능

# 서버에 전송할 데이터 (Form Data)
payload = {
    "limit": 20,
    "offset": 0,
    "from": "full_info",
    "search_date": search_date,
}

# POST 요청 보내기
try:
    response = requests.post(url, data=payload)
    response.raise_for_status()  # 오류가 발생하면 예외를 발생시킴

    # 응답을 JSON 형식으로 파싱
    data = response.json()

        # 원하는 조건 설정
    target_region = "서울"  # 예: "서울", "수원", "강남" 등
    target_time = "20:00"  # 예: "18:00", "20:00" 등

    available_courts = []
    for court in data.get("list", []):
        # 지역 필터링 (주소에 원하는 지역명이 포함되어 있는지 확인)
        if target_region in court.get("fAddress", ""):
            # 시간 필터링
            for reservation in court.get("reserv", []):
                if reservation.get("start_time") == target_time:
                    available_courts.append({
                        "name": court.get("fName"),
                        "address": court.get("fAddress"),
                        "time": f'{reservation.get("start_time")} - {reservation.get("end_time")}',
                        "price": reservation.get("unit_price")
                    })
                    # 해당 구장에서 원하는 시간을 찾았으면 다음 구장으로 넘어감
                    break

    # 결과 출력
    if available_courts:
        print(f"[{search_date} {target_time}] {target_region} 지역 예약 가능한 풋살장 목록:")
        for court in available_courts:
            print(f"- 구장: {court['name']} ({court['address']})")
            print(f"  시간: {court['time']}, 가격: {court['price']}원")
    else:
        print(f"[{search_date} {target_time}] {target_region} 지역에 예약 가능한 풋살장이 없습니다.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:
    print("Failed to decode JSON from the response.json.")
    print("Response text:", response.text)

