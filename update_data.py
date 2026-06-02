import urllib.request
import json
import os
from datetime import datetime

# 1. Đường dẫn nguồn dữ liệu thống kê trận đấu (Có thể thay bằng URL API của trang tin tức)
DATA_SOURCE_URL = "https://raw.githubusercontent.com/openfootball/world-cup/master/2026/v2/matches.json"

def fetch_and_analyze():
    try:
        # Tải dữ liệu từ nguồn tin tức/thống kê
        with urllib.request.urlopen(DATA_SOURCE_URL) as response:
            raw_data = json.loads(response.read().decode())
            
        # Các biến dùng để gom nhóm thống kê phong độ
        team_stats = {}
        processed_matches = []
        
        # Hàm hỗ trợ khởi tạo dữ liệu cho một đội tuyển
        def init_team(name):
            if name not in team_stats:
                team_stats[name] = {"Đội Tuyển": name, "Trận": 0, "Điểm": 0, "Tổng Bàn Thắng": 0, "Tổng Phạt Góc": 0, "Tổng Thẻ Vàng": 0}

        # Duyệt qua toàn bộ lịch đấu từ nguồn tin tức để phân tích
        for match in raw_data.get("matches", []):
            team1 = match["team1"]
            team2 = match["team2"]
            init_team(team1)
            init_team(team2)
            
            status = "Đã kết thúc" if match.get("score1") is not None else "Chưa diễn ra"
            
            match_info = {
                "Vòng": match.get("round", "Vòng Bảng"),
                "Bảng": match.get("group", "-"),
                "Ngày Giờ (VN)": match["date"],
                "Đội Nhà": team1,
                "Đội Khách": team2,
                "Trạng Thái": status,
                "Bàn Nhà": match.get("score1", ""),
                "Bàn Khách": match.get("score2", ""),
                # Giả lập số liệu phạt góc, thẻ phạt thu thập từ trang tin tức
                "Góc Nhà": match.get("corners1", 5), 
                "Góc Khách": match.get("corners2", 4),
                "Thẻ Vàng Nhà": match.get("cards1", 1),
                "Thẻ Vàng Khách": match.get("cards2", 2)
            }
            
            # Nếu trận đấu đã kết thúc, tự động cộng dồn chỉ số phong độ
            if status == "Đã kết thúc":
                s1, s2 = int(match["score1"]), int(match["score2"])
                team_stats[team1]["Trận"] += 1
                team_stats[team2]["Trận"] += 1
                team_stats[team1]["Tổng Bàn Thắng"] += s1
                team_stats[team2]["Tổng Bàn Thắng"] += s2
                
                # Tính điểm số
                if s1 > s2:
                    team_stats[team1]["Điểm"] += 3
                elif s1 < s2:
                    team_stats[team2]["Điểm"] += 3
                else:
                    team_stats[team1]["Điểm"] += 1
                    team_stats[team2]["Điểm"] += 1
                    
            processed_matches.append(match_info)
            
        # Đóng gói toàn bộ thành một database JSON tinh gọn
        final_database = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matches": processed_matches,
            "analytics": list(team_stats.values())
        }
        
        # Ghi đè vào file data.json để Web hiển thị
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(final_database, f, ensure_ascii=False, indent=4)
            
        print("Cập nhật dữ liệu từ trang tin tức thành công!")
    except Exception as e:
        print(f"Lỗi khi cào dữ liệu: {e}")

if __name__ == "__main__":
    fetch_and_analyze()