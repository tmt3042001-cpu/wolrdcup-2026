import urllib.request
import json
import os
from datetime import datetime

DATA_SOURCE_URL = "https://raw.githubusercontent.com/openfootball/world-cup/master/2026/v2/matches.json"

def get_fallback_data():
    # Lịch thi đấu mẫu chuẩn hóa 100%
    return {
        "matches": [
            {"round": "Vòng Bảng", "group": "A", "date": "2026-06-12 02:00", "team1": "Mexico", "team2": "Nam Phi", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None},
            {"round": "Vòng Bảng", "group": "A", "date": "2026-06-12 09:00", "team1": "Hàn Quốc", "team2": "Cộng hòa Séc", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None},
            {"round": "Vòng Bảng", "group": "B", "date": "2026-06-13 02:00", "team1": "Canada", "team2": "Bosnia", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None},
            {"round": "Vòng Bảng", "group": "D", "date": "2026-06-13 08:00", "team1": "Mỹ", "team2": "Paraguay", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None},
            {"round": "Vòng Bảng", "group": "B", "date": "2026-06-14 02:00", "team1": "Qatar", "team2": "Thụy Sĩ", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None},
            {"round": "Vòng Bảng", "group": "C", "date": "2026-06-14 05:00", "team1": "Brazil", "team2": "Maroc", "score1": None, "score2": None, "corners1": None, "corners2": None, "cards1": None, "cards2": None}
        ],
        "news": [
            {"time": "Mới cập nhật", "title": "Các đội tuyển đang gấp rút chuẩn bị cho trận khai mạc World Cup 2026."},
            {"time": "Hôm nay", "title": "Danh sách trọng tài chính điều khiển các trận vòng bảng chính thức được FIFA công bố."},
            {"time": "1 ngày trước", "title": "Người hâm mộ Mexico sẵn sàng lấp đầy chảo lửa Azteca trong ngày khai mạc."}
        ]
    }

def fetch_and_analyze():
    raw_data = None
    try:
        req = urllib.request.Request(DATA_SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = json.loads(response.read().decode())
            print("Đã tải dữ liệu thành công từ cổng thông tin trực tuyến!")
    except Exception as e:
        print(f"Không kết nối được nguồn trực tuyến ({e}). Kích hoạt dữ liệu dự phòng...")
        raw_data = get_fallback_data()
            
    if not isinstance(raw_data, dict) or "matches" not in raw_data:
        raw_data = get_fallback_data()

    team_stats = {}
    processed_matches = []
    now_time = datetime.now() # Lấy thời gian thực tại giây phút chạy code
    
    for match in raw_data.get("matches", []):
        t1, t2 = match["team1"], match["team2"]
        grp = match.get("group", "-")
        
        # BỘ LỌC THỜI GIAN THỰC KHẮT KHE: Nếu trận đấu diễn ra sau thời gian hiện tại -> Xóa bỏ toàn bộ tỷ số ảo
        try:
            match_date = datetime.strptime(match["date"], "%Y-%m-%d %H:%M")
            if match_date > now_time:
                match["score1"] = None
                match["score2"] = None
                match["corners1"] = None
                match["corners2"] = None
                match["cards1"] = None
                match["cards2"] = None
        except Exception:
            pass

        if t1 not in team_stats:
            team_stats[t1] = {"Đội Tuyển": t1, "Bảng": grp, "Trận": 0, "Điểm": 0, "Tổng Bàn Thắng": 0, "Tổng Phạt Góc": 0, "Tổng Thẻ Vàng": 0}
        if t2 not in team_stats:
            team_stats[t2] = {"Đội Tuyển": t2, "Bảng": grp, "Trận": 0, "Điểm": 0, "Tổng Bàn Thắng": 0, "Tổng Phạt Góc": 0, "Tổng Thẻ Vàng": 0}
            
        status = "Đã kết thúc" if match.get("score1") is not None else "Chưa diễn ra"
        
        match_info = {
            "Vòng": match.get("round", "Vòng Bảng"),
            "Bảng": grp,
            "Ngày Giờ (VN)": match["date"],
            "Đội Nhà": t1,
            "Đội Khách": t2,
            "Trạng Thái": status,
            "Bàn Nhà": match.get("score1", "") if match.get("score1") is not None else "",
            "Bàn Khách": match.get("score2", "") if match.get("score2") is not None else "",
            "Góc Nhà": match.get("corners1", 0) if match.get("corners1") is not None else 0, 
            "Góc Khách": match.get("corners2", 0) if match.get("corners2") is not None else 0,
            "Thẻ Vàng Nhà": match.get("cards1", 0) if match.get("cards1") is not None else 0,
            "Thẻ Vàng Khách": match.get("cards2", 0) if match.get("cards2") is not None else 0
        }
        
        if status == "Đã kết thúc":
            s1, s2 = int(match["score1"]), int(match["score2"])
            team_stats[t1]["Trận"] += 1
            team_stats[t2]["Trận"] += 1
            team_stats[t1]["Tổng Bàn Thắng"] += s1
            team_stats[t2]["Tổng Bàn Thắng"] += s2
            team_stats[t1]["Tổng Phạt Góc"] += match_info["Góc Nhà"]
            team_stats[t2]["Tổng Phạt Góc"] += match_info["Góc Khách"]
            team_stats[t1]["Tổng Thẻ Vàng"] += match_info["Thẻ Vàng Nhà"]
            team_stats[t2]["Tổng Thẻ Vàng"] += match_info["Thẻ Vàng Khách"]
            
            if s1 > s2:
                team_stats[t1]["Điểm"] += 3
            elif s1 < s2:
                team_stats[t2]["Điểm"] += 3
            else:
                team_stats[t1]["Điểm"] += 1
                team_stats[t2]["Điểm"] += 1
                
        processed_matches.append(match_info)
        
    final_database = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "matches": processed_matches,
        "analytics": list(team_stats.values()),
        "news": raw_data.get("news", [])
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_database, f, ensure_ascii=False, indent=4)
    print("Hệ thống đã ghi và đồng bộ dữ liệu chuẩn ra file data.json!")

if __name__ == "__main__":
    fetch_and_analyze()
