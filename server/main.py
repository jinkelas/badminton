from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import random

app = FastAPI()

# 處理跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 選手列表
players = [
    {"name": "黑桃K", "level": 10},
    {"name": "同花順", "level": 7},
    {"name": "Full House", "level": 7},
    {"name": "砲灰", "level": 4},
]

# 排點路由
@app.get("/generate_schedule/{selected_players}")
def generate_schedule(selected_players: str = Path(..., title="Selected Players")):
    try:
        # 將字串轉換為選手名字的列表
        selected_players_list = selected_players.split(',')

        # 檢查選手數量是否為偶數，因為雙打比賽需要兩個人一組
        if len(selected_players_list) % 2 != 0:
            raise HTTPException(status_code=400, detail="選手數量必須為偶數")

        # 隨機排序選手
        random.shuffle(selected_players_list)

        # 生成對戰組合
        schedule = []
        for i in range(0, len(selected_players_list), 4):
            team1 = [{"name": name, "level": get_player_level(name)} for name in selected_players_list[i:i+2]]
            team2 = [{"name": name, "level": get_player_level(name)} for name in selected_players_list[i+2:i+4]]
            match = {"team1": team1, "team2": team2}
            schedule.append(match)

        return {"schedule": schedule}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_player_level(player_name: str) -> int:
    # 根據選手名字在 players 列表中找到對應的級數
    for player in players:
        if player["name"] == player_name:
            return player["level"]
    return 1  # 如果找不到，默認級數為 1
