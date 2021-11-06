# lol-obs
This script is used as an extension for generating League of Legends Summoner information without the need to manually adjust OBS overlays.
The primary use case is for recording personal gameplay and tracking stats of the game for VOD review later to help with improvement.

This script is still in development and not optimized.

## Requirements
OBS requires `Python 3.6.x` in order to run. Please refer to [OBS Scripting Documentation](https://obsproject.com/docs/scripting.html) for more information.

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

## Configuration
This file should be placed in the same directory as the primary script to be imported.

```python
config = {
    'api_key': '',
    'summoner_name': ''
}
```