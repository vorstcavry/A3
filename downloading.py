import os
import re
import time
import json
import shutil
import zipfile
import requests
import subprocess
from datetime import timedelta
from subprocess import getoutput
from urllib.parse import unquote
from IPython.utils import capture
from IPython.display import clear_output


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


# ================ LIBRARIES V2 ================
flag_file = f"{root_path}/libraries_installed.txt"

if not os.path.exists(flag_file):
    print("💿 Installing the libraries, it's going to take a while:\n")

    install_lib = {
        "gdown": "pip install -U gdown",
        "aria2": "apt-get update && apt -y install aria2",
        "localtunnel": "npm install -g localtunnel &> /dev/null",
        "insightface": "pip install insightface",
    }

    # Dictionary of additional libraries specific to certain environments
    additional_libs = {
        "Google Colab": {
            "xformers": "pip install xformers==0.0.25 --no-deps",
            "gradio": "pip install gradio_client==0.2.7"
        },
        "Kaggle": {
            "xformers": "pip install -q xformers==0.0.23.post1 triton==2.1.0",
            "torch": "pip install -q torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2 --extra-index-url https://download.pytorch.org/whl/cu121"
        }
    }

    # If the current environment has additional libraries, update the install_lib dictionary
    if env in additional_libs:
        install_lib.update(additional_libs[env])

    # Loop through libraries and execute install commands
    for index, (package, install_cmd) in enumerate(install_lib.items(), start=1):
        print(f"\r[{index}/{len(install_lib)}] \033[32m>>\033[0m Installing \033[33m{package}\033[0m..." + " "*35, end='')
        subprocess.run(install_cmd, shell=True, capture_output=True)

    # Additional manual installation steps for specific packages
    with capture.capture_output() as cap:
        get_ipython().system('curl -s -OL https://github.com/DEX-1101/sd-webui-notebook/raw/main/res/new_tunnel --output-dir {root_path}')
        get_ipython().system('curl -s -Lo /usr/bin/cl https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x /usr/bin/cl')
        get_ipython().system('curl -sLO https://github.com/openziti/zrok/releases/download/v0.4.23/zrok_0.4.23_linux_amd64.tar.gz && tar -xzf zrok_0.4.23_linux_amd64.tar.gz -C /usr/bin && rm -f zrok_0.4.23_linux_amd64.tar.gz')

    del cap

    clear_output()

    # Save file install lib
    with open(flag_file, "w") as f:
        f.write(">W<'")

    print("🍪 Libraries are installed!" + " "*35)
    time.sleep(2)
    clear_output()


# ================= loading settings V4 =================
def load_settings(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return {}

settings = load_settings(f'{root_path}/settings.json')

variables = [
    'Model', 'Model_Num', 'Inpainting_Model',
    'Vae', 'Vae_Num',
    'latest_webui', 'latest_exstensions', 'detailed_download',
    'controlnet', 'controlnet_Num', 'commit_hash', 'optional_huggingface_token',
    'ngrok_token', 'zrok_token', 'commandline_arguments',
    'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'custom_file_urls'
]

locals().update({key: settings.get(key) for key in variables})


# ================= OTHER =================
try:
    start_colab
except:
    start_colab = int(time.time())-5

# CONFIG DIR
models_dir = f"{webui_path}/models/Stable-diffusion"
vaes_dir = f"{webui_path}/models/VAE"
embeddings_dir = f"{webui_path}/embeddings"
loras_dir = f"{webui_path}/models/Lora"
extensions_dir = f"{webui_path}/extensions"
control_dir = f"{webui_path}/models/ControlNet"
adetailer_dir = f"{webui_path}/models/adetailer"


# ================= MAIN CODE =================
if not os.path.exists(webui_path):
    start_install = int(time.time())
    print("⌚ Unpacking Stable Diffusion...", end='')
    with capture.capture_output() as cap:
        get_ipython().system('aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/vorstcavry/fast-repo/resolve/main/FULL_REPO.zip -o repo.zip')
        get_ipython().system('unzip -q -o repo.zip -d {webui_path}')
        get_ipython().system('rm -rf repo.zip')

        get_ipython().run_line_magic('cd', '{root_path}')
        os.environ["SAFETENSORS_FAST_GPU"]='1'
        os.environ["CUDA_MODULE_LOADING"]="LAZY"
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        os.environ["PYTHONWARNINGS"] = "ignore"
        get_ipython().system('aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/vorstcavry/test/resolve/main/colabTimer.txt -d /root/sdw/FULL_REPO/static -o colabTimer.txt')
        get_ipython().system('echo -n {start_colab} > /root/sdw/static/colabTimer.txt')
    del cap
    install_time = timedelta(seconds=time.time()-start_install)
    print("\r🚀 Ekstrak file selesai! For","%02d:%02d:%02d ⚡\n" % (install_time.seconds / 3600, (install_time.seconds / 60) % 60, install_time.seconds % 60), end='', flush=True)
else:
    print("🚀 All unpacked... Skip. ⚡")
    start_colab = float(open(f'{webui_path}/static/colabTimer.txt', 'r').read())
    time_since_start = str(timedelta(seconds=time.time()-start_colab)).split('.')[0]
    print(f"⌚️ You have been conducting this session for - \033[33m{time_since_start}\033[0m")


## Changes extensions and WebUi
if latest_webui or latest_exstensions:
    action = "Updating WebUI and Extensions" if latest_webui and latest_exstensions else ("WebUI Update" if latest_webui else "Update Extensions")
    print(f"⌚️ {action}...", end='', flush=True)
    with capture.capture_output() as cap:
        get_ipython().system('git config --global user.email "you@example.com"')
        get_ipython().system('git config --global user.name "Your Name"')

        ## Update Webui
        if latest_webui:
            get_ipython().run_line_magic('cd', '{webui_path}')
            get_ipython().system('git restore .')
            get_ipython().system('git pull -X theirs --rebase --autostash')

        ## Update extensions
        if latest_exstensions:
            get_ipython().system('{\'for dir in \' + webui_path + \'/extensions/*/; do cd \\"$dir\\" && git reset --hard && git pull; done\'}')

            # # My Chinese friend, you broke the images again in the latest update... >W<'
            # %cd {webui_path}/extensions/Encrypt-Image
            # !git reset --hard 376358d8854472b9ea50e9fc8800367d1ca51137 # stable commit :3
    del cap
    print(f"\r✨ {action} Selesai!")


# === FIXING EXTENSIONS ===
vorstcavry_repos = "https://huggingface.co/vorstcavry/fast-repo/resolve/main"

with capture.capture_output() as cap:
    # --- Umi-Wildcard ---
    get_ipython().system("sed -i '521s/open=\\(False\\|True\\)/open=False/' {webui_path}/extensions/Umi-AI-Wildcards/scripts/wildcard_recursive.py  # Closed accordion by default")

    # --- Encrypt-Image ---
    get_ipython().system("sed -i '9,37d' {webui_path}/extensions/Encrypt-Image/javascript/encrypt_images_info.js # Removes the weird text in webui")

    # --- Additional-Networks ---
    get_ipython().system('wget -O {webui_path}/extensions/additional-networks/scripts/metadata_editor.py {vorstcavry_repos}/extensions/Additional-Networks/fix/metadata_editor.py  # Fixing an error due to old style')
del cap


## Version switching
if commit_hash:
    print('⏳ Time machine activation...', end="", flush=True)
    with capture.capture_output() as cap:
        get_ipython().run_line_magic('cd', '{webui_path}')
        get_ipython().system('git config --global user.email "you@example.com"')
        get_ipython().system('git config --global user.name "Your Name"')
        get_ipython().system('git reset --hard {commit_hash}')
    del cap
    print(f"\r⌛️ The time machine has been activated! Current commit: \033[34m{commit_hash}\033[0m")


## Downloading model and stuff | oh yeah~ I'm starting to misunderstand my own code ( almost my own ;3 )
print("📦 Downloading models and stuff...", end='')
model_list = {
    "1.Anime (by XpucT) + INP": [
        {"url": "https://huggingface.co/XpucT/Anime/resolve/main/Anime_v2.safetensors", "name": "Anime_v2.safetensors"},
        {"url": "https://huggingface.co/XpucT/Anime/resolve/main/Anime_v2-inpainting.safetensors", "name": "Anime_v2-inpainting.safetensors"}
    ],
    "2.BluMix [Anime] [V7] + INP": [
        {"url": "https://civitai.com/api/download/models/361779", "name": "BluMix_v7.safetensors"},
        {"url": "https://civitai.com/api/download/models/363850", "name": "BluMix_v7-inpainting.safetensors"}
    ],
    "3.Cetus-Mix [Anime] [V4] + INP": [
        {"url": "https://civitai.com/api/download/models/130298", "name": "CetusMix_V4.safetensors"},
        {"url": "https://civitai.com/api/download/models/139882", "name": "CetusMix_V4-inpainting.safetensors"}
    ],
    "4.Counterfeit [Anime] [V3] + INP": [
        {"url": "https://civitai.com/api/download/models/125050", "name": "Counterfeit_V3.safetensors"},
        {"url": "https://civitai.com/api/download/models/137911", "name": "Counterfeit_V3-inpainting.safetensors"}
    ],
    "5.CuteColor [Anime] [V3]": [
        {"url": "https://civitai.com/api/download/models/138754", "name": "CuteColor_V3.safetensors"}
    ],
    "6.Dark-Sushi-Mix [Anime]": [
        {"url": "https://civitai.com/api/download/models/101640", "name": "DarkSushiMix_2_5D.safetensors"},
        {"url": "https://civitai.com/api/download/models/56071", "name": "DarkSushiMix_colorful.safetensors"}
    ],
    "7.Deliberate [Realism] [V6] + INP": [
        {"url": "https://huggingface.co/XpucT/Deliberate/resolve/main/Deliberate_v6.safetensors", "name": "Deliberate_v6.safetensors"},
        {"url": "https://huggingface.co/XpucT/Deliberate/resolve/main/Deliberate_v6-inpainting.safetensors", "name": "Deliberate_v6-inpainting.safetensors"}
    ],
    "8.Meina-Mix [Anime] [V11] + INP": [
        {"url": "https://civitai.com/api/download/models/119057", "name": "MeinaMix_V11.safetensors"},
        {"url": "https://civitai.com/api/download/models/120702", "name": "MeinaMix_V11-inpainting.safetensors"}
    ],
    "9.Mix-Pro [Anime] [V4] + INP": [
        {"url": "https://civitai.com/api/download/models/125668", "name": "MixPro_V4.safetensors"},
        {"url": "https://civitai.com/api/download/models/139878", "name": "MixPro_V4-inpainting.safetensors"}
    ]
}

# 1-4 (fp16/cleaned)
vae_list = {
    "1.Anime.vae": [
        {"url": "https://civitai.com/api/download/models/131654", "name": "Anime.vae.safetensors"},
        {"url": "https://civitai.com/api/download/models/131658", "name": "vae-ft-mse.vae.safetensors"}
    ],
    "2.Anything.vae": [{"url": "https://civitai.com/api/download/models/131656", "name": "Anything.vae.safetensors"}],
    "3.Blessed2.vae": [{"url": "https://civitai.com/api/download/models/142467", "name": "Blessed2.vae.safetensors"}],
    "4.ClearVae.vae": [{"url": "https://civitai.com/api/download/models/133362", "name": "ClearVae_23.vae.safetensors"}],
    "5.WD.vae": [{"url": "https://huggingface.co/NoCrypt/resources/resolve/main/VAE/wd.vae.safetensors", "name": "WD.vae.safetensors"}]
}

controlnet_list = {
    "1.canny": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny_fp16.safetensors", "name": "control_v11p_sd15_canny_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_canny_fp16.yaml", "name": "control_v11p_sd15_canny_fp16.yaml"}
    ],
    "2.openpose": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose_fp16.safetensors", "name": "control_v11p_sd15_openpose_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_openpose_fp16.yaml", "name": "control_v11p_sd15_openpose_fp16.yaml"}
    ],
    "3.depth": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth_fp16.safetensors", "name": "control_v11f1p_sd15_depth_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11f1p_sd15_depth_fp16.yaml", "name": "control_v11f1p_sd15_depth_fp16.yaml"},
        {"url": "https://huggingface.co/NagisaNao/models/resolve/main/ControlNet_v11/control_v11p_sd15_depth_anything_fp16.safetensors", "name": "control_v11p_sd15_depth_anything_fp16.safetensors"}
    ],
    "4.normal_map": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_normalbae_fp16.safetensors", "name": "control_v11p_sd15_normalbae_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_normalbae_fp16.yaml", "name": "control_v11p_sd15_normalbae_fp16.yaml"}
    ],
    "5.mlsd": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_mlsd_fp16.safetensors", "name": "control_v11p_sd15_mlsd_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_mlsd_fp16.yaml", "name": "control_v11p_sd15_mlsd_fp16.yaml"}
    ],
    "6.lineart": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart_fp16.safetensors", "name": "control_v11p_sd15_lineart_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15s2_lineart_anime_fp16.safetensors", "name": "control_v11p_sd15s2_lineart_anime_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_lineart_fp16.yaml", "name": "control_v11p_sd15_lineart_fp16.yaml"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15s2_lineart_anime_fp16.yaml", "name": "control_v11p_sd15s2_lineart_anime_fp16.yaml"}
    ],
    "7.soft_edge": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_softedge_fp16.safetensors", "name": "control_v11p_sd15_softedge_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_softedge_fp16.yaml", "name": "control_v11p_sd15_softedge_fp16.yaml"}
    ],
    "8.scribble": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_scribble_fp16.safetensors", "name": "control_v11p_sd15_scribble_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_scribble_fp16.yaml", "name": "control_v11p_sd15_scribble_fp16.yaml"}
    ],
    "9.segmentation": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_seg_fp16.safetensors", "name": "control_v11p_sd15_seg_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_seg_fp16.yaml", "name": "control_v11p_sd15_seg_fp16.yaml"}
    ],
    "10.shuffle": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11e_sd15_shuffle_fp16.safetensors", "name": "control_v11e_sd15_shuffle_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11e_sd15_shuffle_fp16.yaml", "name": "control_v11e_sd15_shuffle_fp16.yaml"}
    ],
    "11.tile": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors", "name": "control_v11f1e_sd15_tile_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11f1e_sd15_tile_fp16.yaml", "name": "control_v11f1e_sd15_tile_fp16.yaml"}
    ],
    "12.inpaint": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors", "name": "control_v11p_sd15_inpaint_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_inpaint_fp16.yaml", "name": "control_v11p_sd15_inpaint_fp16.yaml"}
    ],
    "13.instruct_p2p": [
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11e_sd15_ip2p_fp16.safetensors", "name": "control_v11e_sd15_ip2p_fp16.safetensors"},
        {"url": "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11e_sd15_ip2p_fp16.yaml", "name": "control_v11e_sd15_ip2p_fp16.yaml"}
    ]
}

extension_repo = []
prefixes = {
    "model": models_dir,
    "vae": vaes_dir,
    "lora": loras_dir,
    "embed": embeddings_dir,
    "extension": extensions_dir,
    "control": control_dir,
    "adetailer": adetailer_dir
}

get_ipython().system('mkdir -p {models_dir} {vaes_dir} {loras_dir} {embeddings_dir} {extensions_dir} {control_dir} {adetailer_dir}')

url = ""
hf_token = optional_huggingface_token if optional_huggingface_token else "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"
user_header = f"\"Authorization: Bearer {hf_token}\""

''' main download code '''

def handle_manual(url):
    original_url = url
    url = url.split(':', 1)[1]
    file_name = re.search(r'\[(.*?)\]', url)
    file_name = file_name.group(1) if file_name else None
    if file_name:
        url = re.sub(r'\[.*?\]', '', url)

    for prefix, dir in prefixes.items():
        if original_url.startswith(f"{prefix}:"):
            if prefix != "extension":
                manual_download(url, dir, file_name=file_name)
            else:
                extension_repo.append((url, file_name))

def manual_download(url, dst_dir, file_name):
    basename = url.split("/")[-1] if file_name is None else file_name
    header_option = f"--header={user_header}"

    print("\033[32m---"*45 + f"\n\033[33mURL: \033[34m{url}\n\033[33mSAVE DIR: \033[34m{dst_dir}\n\033[33mFILE NAME: \033[34m{file_name}\033[32m\n~~~\033[0m")
    # print(url, dst_dir, file_name)

    # I do it at my own risk..... Fucking CivitAi >:(
    civitai_token = "62c0c5956b2f9defbd844d754000180b"
    if 'civitai' in url and civitai_token:
        url = f"{url}?token={civitai_token}"

    # -- GDrive --
    if 'drive.google' in url:
        if 'folders' in url:
            get_ipython().system('gdown --folder "{url}" -O {dst_dir} --fuzzy -c')
        else:
            if file_name:
               get_ipython().system('gdown "{url}" -O {dst_dir}/{file_name} --fuzzy -c')
            else:
               get_ipython().system('gdown "{url}" -O {dst_dir} --fuzzy -c')
    # -- Huggin Face --
    elif 'huggingface' in url:
        if '/blob/' in url:
            url = url.replace('/blob/', '/resolve/')
        if file_name:
            get_ipython().system('aria2c {header_option} --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -c -j5 -x16 -s16 -k1M -c -d {dst_dir} -o {basename} {url}')
        else:
            parsed_link = f'\n{url}\n\tout={unquote(url.split("/")[-1])}'
            get_ipython().system('echo -e "{parsed_link}" | aria2c {header_option} --console-log-level=error --summary-interval=10 -i- -j5 -x16 -s16 -k1M -c -d "{dst_dir}" -o {basename}')
    # -- Other --
    elif 'http' in url or 'magnet' in url:
        if file_name:
            get_ipython().system('aria2c --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -j5 -x16 -s16 -k1M -c -d {dst_dir} -o {file_name} {url}')
        else:
            parsed_link = '"{}"'.format(url)
            get_ipython().system('aria2c --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -j5 -x16 -s16 -k1M -c -d {dst_dir} -Z {parsed_link}')

def download(url):
    links_and_paths = url.split(',')

    for link_or_path in links_and_paths:
        link_or_path = link_or_path.strip()
        if not link_or_path:
            continue
        if any(link_or_path.startswith(prefix.lower()) for prefix in prefixes):
            handle_manual(link_or_path)
            continue

        url, dst_dir, file_name = link_or_path.split()
        manual_download(url, dst_dir, file_name)

    unpucking_zip_files()

## unpucking zip files
def unpucking_zip_files():
    directories = [models_dir, vaes_dir, embeddings_dir, loras_dir , extensions_dir, control_dir , adetailer_dir]

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".zip"):
                    zip_path = os.path.join(root, file)
                    extract_path = os.path.splitext(zip_path)[0]
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                    os.remove(zip_path)

''' submodels - added urls '''

submodels = []

def add_submodels(selection, num_selection, model_dict, dst_dir):
    if selection == "none":
        return []
    if selection == "ALL":
        all_models = []
        for models in model_dict.values():
            all_models.extend(models)
        selected_models = all_models
    else:
        selected_models = model_dict[selection]
        selected_nums = map(int, num_selection.replace(',', '').split())

        for num in selected_nums:
            if 1 <= num <= len(model_dict):
                name = list(model_dict)[num - 1]
                selected_models.extend(model_dict[name])

    unique_models = list({model['name']: model for model in selected_models}.values())

    for model in unique_models:
        model['dst_dir'] = dst_dir

    return unique_models

submodels += add_submodels(Model, Model_Num, model_list, models_dir)                                                   # model
submodels += add_submodels(Vae, Vae_Num, vae_list, vaes_dir)                                                           # vae
submodels += add_submodels(controlnet, "" if controlnet == "ALL" else controlnet_Num, controlnet_list, control_dir)    # controlnet

for submodel in submodels:
    if not Inpainting_Model and "inpainting" in submodel['name']:
        continue
    url += f"{submodel['url']} {submodel['dst_dir']} {submodel['name']}, "

''' file.txt - added urls '''

unique_urls = []

def process_file_download(file_url):
    files_urls = ""

    if file_url.startswith("http"):
        if "blob" in file_url:
            file_url = file_url.replace("blob", "raw")
        response = requests.get(file_url)
        lines = response.text.split('\n')
    else:
        with open(file_url, 'r') as file:
            lines = file.readlines()

    current_tag = None
    for line in lines:
        if any(f'# {tag}' in line.lower() for tag in prefixes):
            current_tag = next((tag for tag in prefixes if tag in line.lower()))

        urls = [url.split('#')[0].strip() for url in line.split(',')]  # filter urls
        for url in urls:
            if url.startswith("http") and url not in unique_urls:
                # handle_manual(f"{current_tag}:{url}")
                files_urls += f"{current_tag}:{url}, "
                unique_urls.append(url)

    return files_urls

# fix all possible errors/options and function call
file_urls = ""
if custom_file_urls:
    for custom_file_url in custom_file_urls.replace(',', '').split():
        if not custom_file_url.endswith('.txt'):
            custom_file_url += '.txt'
        if not custom_file_url.startswith('http'):
            if not custom_file_url.startswith(root_path):
                custom_file_url = f'{root_path}/{custom_file_url}'

        try:
            file_urls += process_file_download(custom_file_url)
        except FileNotFoundError:
            pass

# url prefixing
urls = [Model_url, Vae_url, LoRA_url, Embedding_url, Extensions_url]
prefixed_urls = [f"{prefix}:{url}" for prefix, url in zip(prefixes.keys(), urls) if url for url in url.replace(',', '').split()]
url += ", ".join(prefixed_urls) + ", " + file_urls

if detailed_download == "on":
    print("\n\n\033[33m# ====== Detailed Download ====== #\n\033[0m")
    download(url)
    print("\n\033[33m# =============================== #\n\033[0m")
else:
    with capture.capture_output() as cap:
        download(url)
    del cap

print("\r🏁 Download Complete!" + " "*15)


# Cleaning shit after downloading...
get_ipython().system('find {webui_path} \\( -type d \\( -name ".ipynb_checkpoints" -o -name ".aria2" \\) -o -type f -name "*.aria2" \\) -exec rm -r {{}} \\; >/dev/null 2>&1')

print("\r💢Menghapus dan mengoptimalkan proses...")

files_config = [
    "https://huggingface.co/spaces/vorstcavry/stable-diffusion-webui/resolve/main/config.json",
    "https://huggingface.co/spaces/vorstcavry/stable-diffusion-webui/resolve/main/ui-config.json"
]

with capture.capture_output() as cap:
    for file in files_config:
        get_ipython().system('aria2c --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -j5 -x16 -s16 -k1M -c -d {webui_path} {file}')
        get_ipython().system('rm -rf /root/sdw/extensions/openpose-editor-master')
        get_ipython().system('rm -rf /root/sdw/extensions/sd-webui-depth-lib-main')
        print("Dah itu aja sih")
del cap

## Install of Custom extensions
if len(extension_repo) > 0:
    print("✨ Installing custom extensions...", end='', flush=True)
    with capture.capture_output() as cap:
        for repo, repo_name in extension_repo:
            if not repo_name:
                repo_name = repo.split('/')[-1]
            get_ipython().system('cd {extensions_dir}                  && git clone {repo} {repo_name}                  && cd {repo_name}                  && git fetch')
    del cap
    print(f"\r📦 Installed '{len(extension_repo)}', Custom extensions!")


## List Models and stuff
if detailed_download == "off":
    print("\n\n\033[33mJika Kamu tidak melihat file yang diunduh, aktifkan fitur 'Unduhan Detail' di widget.")

if any(not file.endswith('.txt') for file in os.listdir(models_dir)):
    print("\n\033[33m➤ Models\033[0m")
    get_ipython().system("find {models_dir}/ -mindepth 1 ! -name '*.txt' -printf '%f\\n'")
if any(not file.endswith('.txt') for file in os.listdir(vaes_dir)):
    print("\n\033[33m➤ VAEs\033[0m")
    get_ipython().system("find {vaes_dir}/ -mindepth 1 ! -name '*.txt' -printf '%f\\n'")
if any(not file.endswith('.txt') and not os.path.isdir(os.path.join(embeddings_dir, file)) for file in os.listdir(embeddings_dir)):
    print("\n\033[33m➤ Embeddings\033[0m")
    get_ipython().system("find {embeddings_dir}/ -mindepth 1 -maxdepth 1 \\( -name '*.pt' -or -name '*.safetensors' \\) -printf '%f\\n'")
if any(not file.endswith('.txt') for file in os.listdir(loras_dir)):
    print("\n\033[33m➤ LoRAs\033[0m")
    get_ipython().system("find {loras_dir}/ -mindepth 1 ! -name '*.keep' -printf '%f\\n'")
print(f"\n\033[33m➤ Extensions\033[0m")
get_ipython().system("find {extensions_dir}/ -mindepth 1 -maxdepth 1 ! -name '*.txt' -printf '%f\\n'")
if any(not file.endswith(('.txt', '.yaml')) for file in os.listdir(control_dir)):
    print("\n\033[33m➤ ControlNet\033[0m")
    get_ipython().system("find {control_dir}/ -mindepth 1 ! -name '*.yaml' -printf '%f\\n' | sed 's/^[^_]*_[^_]*_[^_]*_\\(.*\\)_fp16\\.safetensors$/\\1/'")


# === OTHER ===
# Downlaod discord tags UmiWildcards
files_umi = [
    "https://huggingface.co/vorstcavry/fast-repo/resolve/main/extensions/UmiWildacrd/discord/200_pan_gen.txt",
    "https://huggingface.co/vorstcavry/fast-repo/resolve/main/extensions/UmiWildacrd/discord/150_bra_gen.txt"
]
save_dir_path = f"{webui_path}/extensions/Umi-AI-Wildcards/wildcards/discord"

with capture.capture_output() as cap:
    for file in files_umi:
        get_ipython().system('aria2c --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -j5 -x16 -s16 -k1M -c -d {save_dir_path} {file}')
del cap
