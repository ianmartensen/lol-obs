# LoL OBS
This script is used as an [Open Broadcast Software](https://obsproject.com/) (OBS) extension for generating & displaying League of Legends Summoner information without the need to manually adjust OBS overlays.
The primary use case of this project is for recording personal gameplay and tracking stats of the game for VOD review later to help with improvement.

This script is still in development & not optimized.

## Getting Started

Make sure to download the latest version of [OBS](https://obsproject.com/) from their website.

OBS scripting requires `Python 3.6.x` in order to run. Please refer to the [OBS Scripting Documentation](https://obsproject.com/docs/scripting.html) for more information.

The Python 3.6.x installation will also need to have the `requests` module installed.

In CMD, navigate to your installation folder typically located here:
```shell
cd C:\Users\{Username}\AppData\Local\Programs\Python\Python36
```

Note: The above Python 3.6.x path will be the path needed for OBS as well under the `Python Settings` tab. 

Then you may pip install via:
```shell
python -m pip install requests
```

OBS will require a [Scene](https://obsproject.com/wiki/Sources-Guide#scene) with two separate [Sources](https://obsproject.com/wiki/Sources-Guide#game-capture) titled `Current Rank` and `Matchup`. The properties of theses elements can be adjust to your liking within OBS. It is recommended to scale the text by adjusting the font to the largest possible size and then downscale the overlayed text to fit your preferred area of the screen.

## Configuration
[Environment Variables](https://en.wikipedia.org/wiki/Environment_variable) should be set following the below sample

```shell
# Riot Games API Key
API_KEY = ''
# The location of your 'db' folder cloned from this repo, e.g -> C:\Users\{username}\Desktop\repos\lol_obs\db\match_history.db
MATCH_HISTORY = ''
STATS = ''
```

## Todo
1. Add configurable values to the script through the OBS UI so that adjustments don't need to be made in the code.
2. Add more statistics to track more detailed information.
3. Bug fix across the board to reduce likelyhood of OBS reporting a crash when it is closed.