import obspython as obs
from utils.utils import Summoner, get_lol_rank, update_match_history, live_matchup
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def script_description():
    return (
        f'League of Legends Gameplay Analytics Extensions\n\n'
        f'This script will poll for updated information from the Riot Games API once per minute to update overlays without user intervention\n' 
        f'for the purposes of recording and analyzing personal gameplay.\n\n'
        f'Make sure that your environment variables are set before running this script.'
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


def rank():
    try:
        summoner = Summoner('PianIan')
    except requests.exceptions.ConnectionError:
        print('API is unavailable.')
    srcs = obs.obs_enum_sources()
    for src in srcs:
        if obs.obs_source_get_id(src) == 'text_gdiplus_v2' and obs.obs_source_get_name(src) == 'Current Rank':
            rank = get_lol_rank(summoner)
            set_source_text(src, rank)
    obs.source_list_release(srcs)


def matchup():
    try:
        summoner = Summoner('PianIan')
    except requests.exceptions.ConnectionError:
        print('API is unavailable.')
    srcs = obs.obs_enum_sources()
    for src in srcs:
        if obs.obs_source_get_id(src) == 'text_gdiplus_v2' and obs.obs_source_get_name(src) == 'Matchup':
            text = live_matchup(summoner)
            set_source_text(src, text)
    obs.source_list_release(srcs)


def match_history():
    try:
        summoner = Summoner('PianIan')
    except requests.exceptions.ConnectionError:
        print("Riot Games API is currently unavailable.")
    update_match_history(summoner)


obs.timer_add(rank, 60000)
obs.timer_add(matchup, 90000)
obs.timer_add(match_history, 300000)