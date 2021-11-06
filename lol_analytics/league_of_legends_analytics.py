import obspython as obs
from config import config
import requests

def script_description():
    return (
        f'League of Legends Gameplay Analytics Extensions\n\n'
        f'This script will poll for updated information from the Riot Games API once per minute to update overlays without user intervention\n' 
        f'for the purposes of recording and analyzing personal gameplay.\n\n'
        f'Make sure that your config.py file is placed in the same directory as the primary script.'
    )

def get_source_text(src):
    src_settings = obs.obs_source_get_settings(src)
    text = obs.obs_data_get_string(src_settings, 'text')
    obs.obs_data_release(src_settings)
    return text

def set_source_text(src, string):
    src_settings = obs.obs_source_get_settings(src)
    obs.obs_data_set_string(src_settings, 'text', string)
    obs.obs_source_update(src, src_settings)
    obs.obs_data_release(src_settings)

def lol_rank():
    srcs = obs.obs_enum_sources()
    for src in srcs:
        if obs.obs_source_get_id(src) == 'text_gdiplus_v2' and obs.obs_source_get_name(src) == 'Current RANK':
            try:
                summoner_info = f'lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}?api_key={API_KEY}'
                r = requests.get(f'{RG_BASE_URL}/{summoner_info}', headers=HEADERS)
                if r.status_code == 200:
                    summoner_id = r.json()['id']
                    ranked_info = f'lol/league/v4/entries/by-summoner/{summoner_id}?api_key={API_KEY}'
                    my_rank = requests.get(f'{RG_BASE_URL}/{ranked_info}', headers=HEADERS)
                    if my_rank.status_code == 200:
                        response = my_rank.json()[0]
                        rank = (
                            f'{response["tier"]} {response["rank"]} - {response["leaguePoints"]} LP\n'
                            f'Wins: {response["wins"]} - Losses: {response["losses"]}'
                        )
                        set_source_text(src, rank)
            except Exception as e:
                print(f'Error: {e}')
                raise
    obs.source_list_release(srcs)

API_KEY = config['api_key']
SUMMONER_NAME = config['summoner_name']
HEADERS = {'Content-Type': 'application/json'}
RG_BASE_URL = 'https://na1.api.riotgames.com'

obs.timer_add(lol_rank, 60000)