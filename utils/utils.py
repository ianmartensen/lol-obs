import sqlite3
import requests
from datetime import datetime
import time
import os
import urllib3
import math
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Summoner:
    def __init__(self, name):
        self.name = name
        self.encrypted_summoner_id = None
        self.account_id = None
        self.ppuid = None

        headers = {
            'Content-Type': 'application/json',
            'X-Riot-Token': os.environ.get('API_KEY')
        }
        r = requests.get(url=f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.name}', headers=headers)
        if r.status_code == 200:
            r = r.json()
            self.encrypted_summoner_id = r['id']
            self.account_id = r['accountId']
            self.ppuid = r['puuid']

        
def get_lol_rank(summoner):
    rg_platform_url = 'https://na1.api.riotgames.com'
    headers = {
        'Content-Type': 'application/json',
        'X-Riot-Token': os.environ.get('API_KEY')
    }
    my_rank = requests.get(f'{rg_platform_url}/lol/league/v4/entries/by-summoner/{summoner.encrypted_summoner_id}', headers=headers)
    if my_rank.status_code == 200:
        response = my_rank.json()[0]
        rank = (
            f'{response["tier"]} {response["rank"]} - {response["leaguePoints"]} LP\n'
            f'Wins: {response["wins"]} - Losses: {response["losses"]}'
        )
    else:
        rank = 'Rank Unavailable'
    return rank


def update_match_history(summoner):
    match_id = sqlite3.connect(rf'{os.environ.get("MATCH_HISTORY")}')
    stats = sqlite3.connect(rf'{os.environ.get("STATS")}')
    stats_cur = stats.cursor()
    match_cur = match_id.cursor()

    match_cur = match_id.execute("CREATE TABLE IF NOT EXISTS match_history (match_id text PRIMARY KEY)")
    stats_cur.execute("""
        CREATE TABLE IF NOT EXISTS champion_stats (
            match_id text, 
            champion text, 
            my_lane text,
            game_result text,
            enemy_champion text,
            enemy_lane text,
            timestamp text
        )
    """)

    headers = {
        'Content-Type': 'application/json',
        'X-Riot-Token': os.environ.get('API_KEY')
    }
    rg_region_url = 'https://americas.api.riotgames.com'
    get_matches = requests.get(f'{rg_region_url}/lol/match/v5/matches/by-puuid/{summoner.ppuid}/ids?start=0&count=80', headers=headers).json()

    for i, match in enumerate(get_matches):
        match_cur.execute('INSERT OR IGNORE INTO match_history (match_id) VALUES (?)', (match,))
        match_id.commit()

        recorded_matches = stats_cur.execute('SELECT match_id FROM champion_stats').fetchall()
        recorded_matches = [m[0] for m in recorded_matches]

        if match in recorded_matches:
            pass
        else:
            match_details = requests.get(f'{rg_region_url}/lol/match/v5/matches/{get_matches[i]}', headers=headers).json()
            game_ts = datetime.fromtimestamp(int(match_details['info'].get('gameEndTimestamp', datetime.now().strftime(format='%Y-%m-%d %H:%M:%S'))) / 1000).strftime(format='%Y-%m-%d %H:%M:%S')

            for detail in match_details['info']['participants']:
                if detail['puuid'] == summoner.ppuid:
                    my_lane = detail['teamPosition'].lower()
                    champion = detail['championName'].lower()
                    result = detail['win']

            for enemy in match_details['info']['participants']:
                if enemy['teamPosition'].lower() == my_lane and enemy['puuid'] != summoner.ppuid:
                    enemy_champion = enemy['championName'].lower()
                    enemy_lane = enemy['teamPosition'].lower()

            stats_cur.execute("""
                INSERT INTO champion_stats (match_id, champion, my_lane, game_result, enemy_champion, enemy_lane, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", (match, champion, my_lane, result, enemy_champion, enemy_lane, game_ts))
            stats.commit()

        time.sleep(0.2)


def live_matchup(summoner):
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/playerlist', verify=False)
        response = response.json()
    except requests.exceptions.ConnectionError as e:
        return 'Waiting for game...'

    for player in response:
        if player['summonerName'] == summoner.name:
            my_lane = player['position']
            my_champion = player['championName'].lower()

    for enemy in response:
        if enemy['summonerName'] != summoner.name and enemy['position'] == my_lane:
            enemy_champion = enemy['position'].lower()

    stats = sqlite3.connect(rf'{os.environ.get("STATS")}')
    cur = stats.cursor()

    percentage = cur.execute("""
        SELECT COUNT(CASE WHEN game_result = 1 THEN 1 END) * 100.0 / COUNT(game_result) AS win_rate
        FROM champion_stats
        WHERE champion = :me
        AND enemy_champion = :enemy
        """, {'me': my_champion, 'enemy': enemy_champion}).fetchone()

    if len(percentage) == 0 or percentage[0] is None:
        return 'No Matchup Data Available.'
    else:
        return f'Matchup: {my_champion} vs. {enemy_champion} - winrate: {round(int(percentage[0]), 2)}%'


def get_active_champion(summoner):
    rg_platform_url = 'https://na1.api.riotgames.com'
    headers = {
        'Content-Type': 'application/json',
        'X-Riot-Token': os.environ.get('API_KEY')
    }

    r = requests.get(f'{rg_platform_url}/lol/spectator/v4/active-games/by-summoner/{summoner.encrypted_summoner_id}', headers=headers)
    players = r.json()
    if r.status_code == 404:
        return False
    elif r.status_code == 200:
        for player in players['participants']:
            if player['summonerId'] == summoner.encrypted_summoner_id:
                champion_id = player['championId']
                return get_champion_name(champion_id)
    
    return False


def get_champion_name(champion_id):
    champions = {
        1: 'Annie',
        2: 'Olaf',
        3: 'Galio',
        4: 'Twisted Fate',
        5: 'Xin Zhao',
        6: 'Urgot',
        7: 'LeBlanc',
        8: 'Vladimir',
        9: 'Fiddlesticks',
        10: 'Kayle',
        11: 'Master Yi',
        12: 'Alistar',
        13: 'Ryze',
        14: 'Sion',
        15: 'Sivir',
        16: 'Soraka',
        17: 'Teemo',
        18: 'Tristana',
        19: 'Warwick',
        20: 'Nunu & Willump',
        21: 'Miss Fortune',
        22: 'Ashe',
        23: 'Tryndamere',
        24: 'Jax',
        25: 'Morgana',
        26: 'Zilean',
        27: 'Singed',
        28: 'Evelynn',
        29: 'Twitch',
        30: 'Karthus',
        31: "Cho'Gath",
        32: 'Amumu',
        33: 'Rammus',
        34: 'Anivia',
        35: 'Shaco',
        36: 'Dr.Mundo',
        37: 'Sona',
        38: 'Kassadin',
        39: 'Irelia',
        40: 'Janna',
        41: 'Gangplank',
        42: 'Corki',
        43: 'Karma',
        44: 'Taric',
        45: 'Veigar',
        48: 'Trundle',
        50: 'Swain',
        51: 'Caitlyn',
        53: 'Blitzcrank',
        54: 'Malphite',
        55: 'Katarina',
        56: 'Nocturne',
        57: 'Maokai',
        58: 'Renekton',
        59: 'JarvanIV',
        60: 'Elise',
        61: 'Orianna',
        62: 'Wukong',
        63: 'Brand',
        64: 'LeeSin',
        67: 'Vayne',
        68: 'Rumble',
        69: 'Cassiopeia',
        72: 'Skarner',
        74: 'Heimerdinger',
        75: 'Nasus',
        76: 'Nidalee',
        77: 'Udyr',
        78: 'Poppy',
        79: 'Gragas',
        80: 'Pantheon',
        81: 'Ezreal',
        82: 'Mordekaiser',
        83: 'Yorick',
        84: 'Akali',
        85: 'Kennen',
        86: 'Garen',
        89: 'Leona',
        90: 'Malzahar',
        91: 'Talon',
        92: 'Riven',
        96: "Kog'Maw",
        98: 'Shen',
        99: 'Lux',
        101: 'Xerath',
        102: 'Shyvana',
        103: 'Ahri',
        104: 'Graves',
        105: 'Fizz',
        106: 'Volibear',
        107: 'Rengar',
        110: 'Varus',
        111: 'Nautilus',
        112: 'Viktor',
        113: 'Sejuani',
        114: 'Fiora',
        115: 'Ziggs',
        117: 'Lulu',
        119: 'Draven',
        120: 'Hecarim',
        121: "Kha'Zix",
        122: 'Darius',
        126: 'Jayce',
        127: 'Lissandra',
        131: 'Diana',
        133: 'Quinn',
        134: 'Syndra',
        136: 'AurelionSol',
        141: 'Kayn',
        142: 'Zoe',
        143: 'Zyra',
        145: "Kai'sa",
        147: "Seraphine",
        150: 'Gnar',
        154: 'Zac',
        157: 'Yasuo',
        161: "Vel'Koz",
        163: 'Taliyah',
        166: "Akshan",
        164: 'Camille',
        201: 'Braum',
        202: 'Jhin',
        203: 'Kindred',
        222: 'Jinx',
        223: 'TahmKench',
        234: 'Viego',
        235: 'Senna',
        236: 'Lucian',
        238: 'Zed',
        240: 'Kled',
        245: 'Ekko',
        246: 'Qiyana',
        254: 'Vi',
        266: 'Aatrox',
        267: 'Nami',
        268: 'Azir',
        350: 'Yuumi',
        360: 'Samira',
        412: 'Thresh',
        420: 'Illaoi',
        421: "Rek'Sai",
        427: 'Ivern',
        429: 'Kalista',
        432: 'Bard',
        497: 'Rakan',
        498: 'Xayah',
        516: 'Ornn',
        517: 'Sylas',
        526: 'Rell',
        518: 'Neeko',
        523: 'Aphelios',
        555: 'Pyke',
        875: "Sett",
        711: "Vex",
        777: "Yone",
        887: "Gwen",
        876: "Lillia"
    }

    for key, val in champions.items():
        if key == champion_id:
            return val

    return 'Invalid Champion ID'