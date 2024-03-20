from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
import random
import logging
import os 

# 設定 logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# 處理跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

players = [
    {"name": "黑桃K", "level": 10, "games": 0, "match_time": None},
    {"name": "同花順", "level": 7, "games": 1, "match_time": None},
    {"name": "Full House", "level": 7, "games": 0, "match_time": None},
    {"name": "砲灰", "level": 4, "games": 0, "match_time": None},
]

playersinmatch = []

@app.get("/")
def read_root():
    port = int(os.environ.get("PORT", 8000))
    return {"message": "Hello, world!", "port": port}

# 取得選手列表
@app.get("/get_players", response_model=dict)
async def get_players():
    return {"players": players}

# 新增選手
@app.post("/add_player", response_model=dict)
async def add_player(player: dict):
    new_player = {
        "name": player["name"],
        "level": player["level"],
        "games": 0
    }
    players.append(new_player)
    return {"player": new_player}

# 刪除選手
@app.post("/remove_players", response_model=dict)
async def remove_players(selected_players: dict):
    selected_players_list = selected_players.get("selected_players", [])

    if not selected_players_list:
        raise HTTPException(status_code=400, detail="請提供要刪除的選手列表")

    removed_players = []
    for player_name in selected_players_list:
        removed_player = next((player for player in players if player["name"] == player_name), None)
        if removed_player:
            removed_players.append(removed_player)
        players[:] = [player for player in players if player["name"] != player_name]

    remaining_players = [player for player in players if player["name"] not in selected_players_list]

    return {"message": "選手已成功刪除", "removed_players": removed_players, "remaining_players": remaining_players}


# 排點路由
@app.post("/generate_schedule")
def generate_schedule(request_data: dict):
    try:
        logging.debug(players)
        selected_players = request_data.get("selected_players", [])
        schedule = request_data.get("existed_schedule", [])
        num_courts = int(request_data.get("num_courts", 1))
        logging.info(f"schedule:{schedule}")
        # 檢查選手數量是否為偶數，因為雙打比賽需要兩個人一組
        if len(selected_players) % 2 != 0:
            raise HTTPException(status_code=400, detail="選手數量必須為偶數")
        
        # 隨機排序選手
        random.shuffle(selected_players)

        # 加入playersinmatch
        for player in players:
            if player["name"] in selected_players:
                playersinmatch.append(player)
        # 移除player
        index = 0
        while index < len(players):
            if players[index]["name"] in selected_players:
                # 如果是偶數，刪除該元素
                del players[index]
            else:
                index += 1
        loops = num_courts - len(schedule)
        for i in range(loops):
            team1 = [
                {
                    "name": name,
                    "level": update_player_info(name)["level"],
                    "games": update_player_info(name)["games"],
                }
                for name in selected_players[i * 4 : i * 4 + 2]
            ]
            team2 = [
                {
                    "name": name,
                    "level": update_player_info(name)["level"],
                    "games": update_player_info(name)["games"],
                }
                for name in selected_players[i * 4 + 2 : i * 4 + 4]
            ]
            match = {"team1": team1, "team2": team2}
            schedule.append(match)
        logging.debug(playersinmatch)
        logging.debug(match)
        # 找出進入排點結果的選手
        selected_players_info = [player for player in playersinmatch if player["name"] in selected_players]
        return {"schedule": schedule, "selected_players": selected_players_info}
    except Exception as e:
        logging.error(f"Error in generate_schedule: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def update_player_info(player_name: str):
    for player in playersinmatch:
        if player["name"] == player_name:
            return {"level": player["level"], "games": player["games"]}
    return {"level": 1, "games": 1}

@app.post("/complete_match")
def complete_match(request_data: dict):
    try:
        logging.debug(playersinmatch)
        selected_matches = request_data.get("selected_matches", [])
        # 加入players
        current_time = datetime.now()
        for player in playersinmatch:
            for matches in selected_matches:
                logging.debug(f"matches{matches}")
                if player["name"] in matches:
                    player["match_time"] = current_time
                    player["games"]+=1
                    players.append(player)
        # 移除playersinmatch
        index = 0
        while index < len(playersinmatch):
            for matches in selected_matches:
                if playersinmatch[index]["name"] in matches:
                    # 如果是偶數，刪除該元素
                    del playersinmatch[index]
                else:
                    index += 1
        logging.debug(players)
        return {"players": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cancel_match")
def complete_match(request_data: dict):
    try:
        logging.debug(playersinmatch)
        selected_matches = request_data.get("selected_matches", [])
        # 加入players
        for player in playersinmatch:
            for matches in selected_matches:
                logging.debug(f"matches{matches}")
                if player["name"] in matches:
                    players.append(player)
        # 移除playersinmatch
        index = 0
        while index < len(playersinmatch):
            for matches in selected_matches:
                if playersinmatch[index]["name"] in matches:
                    # 如果是偶數，刪除該元素
                    del playersinmatch[index]
                else:
                    index += 1
        logging.debug(players)
        return {"message": "比賽已完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))