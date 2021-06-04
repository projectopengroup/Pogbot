#!/bin/bash

rm -rf ./index.py
rm -rf ./cogs/commands.py
rm -rf ./cogs/customize.py
rm -rf ./cogs/events.py
rm -rf ./cogs/fun.py
rm -rf ./cogs/games.py
rm -rf ./cogs/madden.py
rm -rf ./cogs/moderator.py
rm -rf ./cogs/music.py
rm -rf ./cogs/setup.py
rm -rf ./utils/pogesquelle.py
rm -rf ./utils/pogfunctions.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/index.py
cd cogs
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/commands.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/customize.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/events.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/fun.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/games.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/madden.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/moderator.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/music.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/cogs/setup.py
cd ..
cd utils
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/utils/pogesquelle.py
wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/utils/pogfunctions.py
cd ..
python3 index.py