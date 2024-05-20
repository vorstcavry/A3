# -*- coding: utf-8 -*-
"""gradio.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u02l4Irjj4m8UZPIH7NmI_XnS86Dd_w7
"""

# Commented out IPython magic to ensure Python compatibility.

import os
import re
import time
import json
import requests
from datetime import timedelta

commandline_arguments = "--listen --enable-insecure-extension-access --theme dark --no-half-vae --disable-console-progressbars --disable-safe-unpickle --no-hashing --opt-sdp-attention --gradio" #@param{type:"string"}
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

    if env != "Google Colab":
        commandline_arguments += f" --encrypt-pass=1769 --api"

    get_ipython().system('COMMANDLINE_ARGS="{commandline_arguments}" python launch.py')
