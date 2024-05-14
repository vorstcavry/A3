##~   LAUNCH CODE | BY: ANXETY   ~##

import os
import re
import time
import json
import requests
from datetime import timedelta


#  ================= DETECT ENV =================
def detect_environment():
    free_plan = (os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3) <= 20)
    environments = {
        'COLAB_GPU': ('Google Colab', "/root" if free_plan else "/content"),
        'KAGGLE_URL_BASE': ('Kaggle', "/kaggle/working/content")
    }

    for env_var, (environment, path) in environments.items():
        if env_var in os.environ:
            return environment, path, free_plan

env, root_path, free_plan = detect_environment()
webui_path = f"{root_path}/sdw"
#  ----------------------------------------------

def load_settings():
    SETTINGS_FILE = f'{root_path}/settings.json'
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        return settings

settings = load_settings()
ngrok_token = settings['ngrok_token']
zrok_token = settings['zrok_token']
commandline_arguments = settings['commandline_arguments']


# ======================== TUNNEL ========================
import cloudpickle as pickle

def get_public_ip(version='ipv4'):
    try:
        url = f'https://api64.ipify.org?format=json&{version}=true'
        response = requests.get(url)
        data = response.json()
        public_ip = data['ip']
        return public_ip
    except Exception as e:
        print(f"Error getting public {version} address:", e)

public_ipv4 = get_public_ip(version='ipv4')

tunnel_class = pickle.load(open(f"{root_path}/new_tunnel", "rb"), encoding="utf-8")
tunnel_port= 1769
tunnel = tunnel_class(tunnel_port)
tunnel.add_tunnel(command="cl tunnel --url localhost:{port}", name="cl", pattern=re.compile(r"[\w-]+\.trycloudflare\.com"))
tunnel.add_tunnel(command="lt --port {port}", name="lt", pattern=re.compile(r"[\w-]+\.loca\.lt"), note="Password : " + "\033[32m" + public_ipv4 + "\033[0m" + " rerun cell if 404 error.")

''' add zrok tunnel '''
if zrok_token:
    get_ipython().system('zrok enable {zrok_token} &> /dev/null')
    tunnel.add_tunnel(command="zrok share public http://localhost:{port}/ --headless", name="zrok", pattern=re.compile(r"[\w-]+\.share\.zrok\.io"))
# ======================== TUNNEL ========================


# automatic fixing path V2
get_ipython().system('sed -i \'s|"tagger_hf_cache_dir": ".*"|"tagger_hf_cache_dir": "{webui_path}/models/interrogators/"|\' {webui_path}/config.json')
get_ipython().system('sed -i \'s|"additional_networks_extra_lora_path": ".*"|"additional_networks_extra_lora_path": "{webui_path}/models/Lora/"|\' {webui_path}/config.json')
get_ipython().system('sed -i \'s|"ad_extra_models_dir": ".*"|"ad_extra_models_dir": "{webui_path}/models/adetailer/"|\' {webui_path}/config.json')
# ---
get_ipython().system('sed -i \'s/"sd_checkpoint_hash": ".*"/"sd_checkpoint_hash": ""/g; s/"sd_model_checkpoint": ".*"/"sd_model_checkpoint": ""/g; s/"sd_vae": ".*"/"sd_vae": "None"/g\' {webui_path}/config.json')


with tunnel:
    get_ipython().run_line_magic('cd', '{webui_path}')
    commandline_arguments += f" --port=1769"

    if ngrok_token:
        commandline_arguments += ' --ngrok ' + ngrok_token
    if env != "Google Colab":
        commandline_arguments += f" --encrypt-pass=1769 --api"

    get_ipython().system('COMMANDLINE_ARGS="{commandline_arguments}" python launch.py')

    start_colab = float(open(f'{webui_path}/static/colabTimer.txt', 'r').read())
    time_since_start = str(timedelta(seconds=time.time()-start_colab)).split('.')[0]
    print(f"\n⌚️ \033[0mYou have been conducting this session for - \033[33m{time_since_start}\033[0m\n\n")

