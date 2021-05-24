# For use on AWS only. If you're looking for project code, see index.py.
# Quick and dirty update script.
import os
os.remove('index.py')
os.system('wget https://raw.githubusercontent.com/projectopengroup/Pogbot/main/index.py')
os.system('python3 index.py')