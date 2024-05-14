import os
import json
import time
import ipywidgets as widgets
from ipywidgets import widgets, Layout, Label, Button, VBox, HBox
from IPython.display import display, HTML, Javascript, clear_output


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

get_ipython().system('mkdir -p {root_path}')
#  ----------------------------------------------


# ==================== CSS JS ====================
# custom background images V1.5
import argparse
parser = argparse.ArgumentParser(description='This script processes an background image.')
parser.add_argument('-i', '--image', type=str, help='URL of the image to process', metavar='')
parser.add_argument('-o', '--opacity', type=float, help='Opacity level for the image, between 0 and 1', metavar='', default=0.3)
parser.add_argument('-b', '--blur', type=str, help='Blur level for the image', metavar='', default=0)
parser.add_argument('-y', type=int, help='Y coordinate for the image in px', metavar='', default=0)
parser.add_argument('-x', type=int, help='X coordinate for the image in px', metavar='', default=0)
parser.add_argument('-s', '--scale', type=int, help='Scale image in %%', metavar='', default=100)
parser.add_argument('-m', '--mode', action='store_true', help='Removes repetitive image tiles')
parser.add_argument('-t', '--transparent', action='store_true', help='Makes input/selection fields 35%% more transparent')
parser.add_argument('-bf', '--blur-fields', type=str, help='Background blur level for input/selection fields', metavar='', default=2)
args = parser.parse_args()
"""---"""
url_img = args.image
opacity_img = args.opacity
blur_img = args.blur
y_img = args.y
x_img = args.x
scale_img = args.scale
blur_fields = args.blur_fields

## ---
""" WTF KAGGLE - WHAT THE FUCK IS THE DIFFERENCE OF 35 PIXELS!?!?!? """
fix_heigh_img = "-810px" if env == "Kaggle" else "-775px"

""" transperent fields """
t_bg_alpha = "1" if not args.transparent else "0.65"

""" mode img - repeats """
mode_img = "repeat" if not args.mode else "no-repeat"
## ---

container_background = f'''
<style>
:root {{
  /* for background container*/
  --img_background: url({url_img});
  --img_opacity: {opacity_img};
  --img_blur: {blur_img}px;
  --image_y: {y_img}px;
  --image_x: {x_img}px;
  --img_scale: {scale_img}%;
  --img_mode: {mode_img};
  --img_height_dif: {fix_heigh_img};

  /* for fields */
  --bg-field-color: rgba(28, 28, 28, {t_bg_alpha}); /* -> #1c1c1c */
  --bg-field-color-hover: rgba(38, 38, 38, {t_bg_alpha}); /* -> #262626; */
  --bg-field-blur-level: {blur_fields}px;
}}
'''

display(HTML(container_background))
# ---

CSS = '''
<style>
/* General Styles */
.header {
    font-family: cursive;
    font-size: 20px;
    font-weight: bold;
    color: #ff8cee;
    margin-bottom: 15px;
    user-select: none;
    cursor: default;
    display: inline-block;
}

hr {
    border-color: grey;
    background-color: grey;
    opacity: 0.25;
}

a {
  text-decoration: none;
  color: inherit;
}


/* Container style */

.container {
    position: relative;
    background-color: #232323;
    width: 1080px;
    padding: 10px 15px;
    border-radius: 15px;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.3);
    margin-bottom: 5px;
    overflow: hidden;
}

.container::after {
    position: absolute;
    top: 5px;
    right: 10px;
    content: "Vorst Cavry";
    font-weight: bold;
    font-size: 24px;
    color: rgba(0, 0, 0, 0.2);
}

/* background img */
.container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: var(--img_background);
    background-size: var(--img_scale);
    background-repeat: var(--img_mode);
    opacity: var(--img_opacity);
    mix-blend-mode: screen;
    pointer-events: none;
    filter: blur(var(--img_blur));
    z-index: -1;
}

.image_1::before {
    background-position: var(--image_x) calc(-120px - var(--image_y));
}
.image_2::before {
    background-position: var(--image_x) calc(-290px - var(--image_y));
}
.image_3::before {
    background-position: var(--image_x) calc(-430px - var(--image_y));
}
.image_4::before {
    background-position: var(--image_x) calc(var(--img_height_dif) - var(--image_y));
}

.container_custom_downlad {
    height: 55px;
    transition: all 0.5s;
}

.container_custom_downlad.expanded {
    height: 270px;
}


/* Element text style */

.widget-html,
.widget-button,
.widget-text label,
.widget-checkbox label,
.widget-dropdown label,
.widget-dropdown select,
.widget-text input[type="text"] {
    font-family: cursive;
    font-size: 14px;
    color: white !important;
    user-select: none;
}

.widget-text input[type="text"]::placeholder {
    color: grey;
}


/* Input field styles */

.widget-dropdown select,
.widget-text input[type="text"] {
    height: 30px;
    background-color: var(--bg-field-color);
    border: 1px solid #262626;
    border-radius: 10px;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5);
    transition: all 0.3s ease-in-out;
    backdrop-filter: blur(var(--bg-field-blur-level));
}

.widget-dropdown select:focus,
.widget-text input[type="text"]:focus {
    border-color: #006ee5;
}

.widget-dropdown select:hover,
.widget-text input[type="text"]:hover {
    transform: scale(1.003);
    background-color: var(--bg-field-color-hover);
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}

.widget-dropdown option {
    background-color: #1c1c1c;
}


/* Slider Checkbox style */

.widget-checkbox input[type="checkbox"] {
    appearance: none;
    position: relative;
    top: 4px; /* Why is he taller?! */
    width: 40px;
    height: 20px;
    border: none;
    border-radius: 10px;
    background-color: #20b2aa;
    cursor: pointer;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3);
    transition: background-color 0.3s ease;
}
.widget-checkbox input[type="checkbox"]:checked {
    background-color: #2196F3;
}

.widget-checkbox input[type="checkbox"]:before {
    content: '';
    position: absolute;
    top: 50%;
    left: 3px;
    width: 16px;
    height: 16px;
    border-radius: inherit;
    background-color: white;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
    transform: translateY(-50%);
    transition: left 0.3s ease;
}
.widget-checkbox input[type="checkbox"]:checked:before {
    left: 21px;
}


/* Button styles */

.button_save {
    font-size: 15px;
    font-weight: bold;
    width: 120px;
    height: 35px;
    border-radius: 15px;
    background-image: radial-gradient(circle at top left, cyan 10%, blue 90%);
    background-size: 200% 200%;
    background-position: left bottom;
    transition: background 0.5s ease-in-out, transform 0.3s ease;
}

.button_save:hover {
    cursor: pointer;
    background-image: radial-gradient(circle at top left, purple 10%, violet 90%);
    background-size: 200% 200%;
    background-position: right bottom;
    transform: translateY(1px);
}

.button_ngrok {
    font-size: 12px;
    height: 30px;
    border-radius: 10px;
    padding: 1px 12px;
    background-image: radial-gradient(circle at top left, cyan 10%, blue 90%);
    background-size: 200% 200%;
    background-position: left bottom;
    transition: background 0.5s ease-in-out, transform 0.3s ease;
    white-space: nowrap;
}

.button_ngrok:hover  {
    cursor: pointer;
    background-image: radial-gradient(circle at top left, purple 10%, violet 90%);
    background-size: 200% 200%;
    background-position: right bottom;
    transform: translateY(1px);
}

.button_save:active,
.button_ngrok:active {
    filter: brightness(0.75) !important;
}

/* Removes ugly stroke from widget buttons. */
.jupyter-widgets.lm-Widget:focus {
    outline: none;
}


/* Popup style of `INFO` window */

.info {
    position: absolute;
    top: -5px;
    right: 95px;
    color: grey;
    font-family: cursive;
    font-size: 14px;
    font-weight: normal;
    user-select: none;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
    display: inline-block;
}

.popup {
    position: absolute;
    top: 120px;
    z-index: 999;
    width: auto;
    padding: 10px;
    text-align: center;
    background-color: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 8px;
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
    opacity: 0;
    color: #fff;
    font-size: 16px;
    font-family: cursive;
    user-select: none;
    cursor: default;
    pointer-events: none;
    transform: rotate(-5deg);
    transition: top 0.3s ease-in-out, opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.sample {
    display: inline-block;
    margin-top: 25px;
    padding: 10px 100px;
    background-color: rgba(255, 255, 255, 0.2);
    color: #c6e2ff;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.2), inset 0 0 25px rgba(255, 255, 255, 0.2);
}

.info.showed {
    opacity: 1;
    pointer-events: auto;
}

.info:hover + .popup {
    top: 35px;
    opacity: 1;
    pointer-events: initial;
    transform: rotate(0deg);
}


/* Animation of elements */

.container,
.button_save {
    animation-name: showedWidgets;
    animation-duration: 1s;
    animation-fill-mode: forwards;
}

.container.hide,
.button_save.hide {
    animation-name: hideWidgets;
    animation-duration: 0.5s;
    animation-fill-mode: forwards;
}

@keyframes showedWidgets {
    0% {
        transform: translate3d(-65%, 15%, 0) scale(0) rotate(15deg);
        filter: blur(25px) grayscale(1) brightness(0.3);
        opacity: 0;
    }
    100% {
        transform: translate3d(0, 0, 0) scale(1) rotate(0deg);
        filter: blur(0) grayscale(0) brightness(1);
        opacity: 1;
    }
}

@keyframes hideWidgets {
    0% {
        transform: translate3d(0, 0, 0) scale(1) rotate3d(1, 0, 0, 0deg);
        filter: blur(0) grayscale(0) brightness(1);
        opacity: 1;
    }
    100% {
        transform: translate3d(0, 5%, 0) scale(0.9) rotate3d(1, 0, 0, 90deg);
        filter: blur(15px) grayscale(1) brightness(0.5);
        opacity: 0;
    }
}
</style>

<!-- TOGGLE 'CustomDL' SCRIPT -->
<script>
function toggleContainer() {
    let downloadContainer = document.querySelector('.container_custom_downlad');
    let info = document.querySelector('.info');

    downloadContainer.classList.toggle('expanded');
    info.classList.toggle('showed');
}
</script>
'''

display(HTML(CSS))
# ==================== CSS JS ====================


# ==================== WIDGETS ====================
# --- global widgets ---
style = {'description_width': 'initial'}
layout = widgets.Layout(min_width='1047px')

HR = widgets.HTML('<hr>')

# --- MODEL ---
model_header = widgets.HTML('<div class="header">Model Selection<div>')
model_options = ['none',
                 '1.Anime (by XpucT) + INP',
                 '2.BluMix [Anime] [V7] + INP',
                 '3.Cetus-Mix [Anime] [V4] + INP',
                 '4.Counterfeit [Anime] [V3] + INP',
                 '5.CuteColor [Anime] [V3]',
                 '6.Dark-Sushi-Mix [Anime]',
                 '7.Deliberate [Realism] [V6] + INP',
                 '8.Meina-Mix [Anime] [V11] + INP',
                 '9.Mix-Pro [Anime] [V4] + INP']
# ---
Model_widget = widgets.Dropdown(options=model_options, value='4.Counterfeit [Anime] [V3] + INP', description='Model:', style=style, layout=layout)
Model_Num_widget = widgets.Text(description='Model Number:', placeholder='Enter the model numbers to be downloaded using comma/space.', style=style, layout=layout)
Inpainting_Model_widget = widgets.Checkbox(value=False, description='Inpainting Models', style=style)

''' Display Model'''
all_model_box = widgets.VBox([model_header, Model_widget, Model_Num_widget, Inpainting_Model_widget]).add_class("container").add_class("image_1")
display(all_model_box)

# --- VAE ---
vae_header = widgets.HTML('<div class="header" >VAE Selection</div>')
vae_options = ['none',
               '1.Anime.vae',
               '2.Anything.vae',
               '3.Blessed2.vae',
               '4.ClearVae.vae',
               '5.WD.vae']
Vae_widget = widgets.Dropdown(options=vae_options, value='3.Blessed2.vae', description='Vae:', style=style, layout=layout)
Vae_Num_widget = widgets.Text(description='Vae Number:', placeholder='Enter the vae numbers to be downloaded using comma/space.', style=style, layout=layout)

''' Display Vae'''
all_vae_box= widgets.VBox([vae_header, Vae_widget, Vae_Num_widget]).add_class("container").add_class("image_2")
display(all_vae_box)

# --- ADDITIONAL ---
additional_header = widgets.HTML('<div class="header">Additional</div>')
latest_webui_widget = widgets.Checkbox(value=True, description='Update WebUI', style=style)
latest_exstensions_widget = widgets.Checkbox(value=True, description='Update Extensions', style=style)
detailed_download_widget = widgets.Dropdown(options=['off', 'on'], value='off', description='Detailed Download:', style=style)
latest_changes_widget = HBox([latest_webui_widget, latest_exstensions_widget, detailed_download_widget], layout=widgets.Layout(justify_content='space-between'))
controlnet_options = ['none', 'ALL', '1.canny',
                      '2.openpose', '3.depth',
                      '4.normal_map', '5.mlsd',
                      '6.lineart', '7.soft_edge',
                      '8.scribble', '9.segmentation',
                      '10.shuffle', '11.tile',
                      '12.inpaint', '13.instruct_p2p']
# ---
controlnet_widget = widgets.Dropdown(options=controlnet_options, value='none', description='ControlNet:', style=style, layout=layout)
controlnet_Num_widget = widgets.Text(description='ControlNet Number:', placeholder='Enter the ControlNet model numbers to be downloaded using comma/space.', style=style, layout=layout)
commit_hash_widget = widgets.Text(description='Commit Hash:', style=style, layout=layout)
optional_huggingface_token_widget = widgets.Text(description='HuggingFace Token:', style=style, layout=layout)
ngrok_token_widget = widgets.Text(description='Ngrok Token:', style=style, layout=widgets.Layout(width='1047px'))
ngrock_button = widgets.HTML('<a href="https://dashboard.ngrok.com/get-started/your-authtoken" target="_blank">Get Ngrok Token</a>').add_class("button_ngrok")
ngrok_widget = widgets.HBox([ngrok_token_widget, ngrock_button], style=style, layout=layout)
zrok_token_widget = widgets.Text(description='Zrok Token:', style=style, layout=widgets.Layout(width='1047px'))
zrok_button = widgets.HTML('<a href="https://colab.research.google.com/drive/1d2sjWDJi_GYBUavrHSuQyHTDuLy36WpU" target="_blank">Reg Zrok Token</a>').add_class("button_ngrok")
zrok_widget = widgets.HBox([zrok_token_widget, zrok_button], style=style, layout=layout)
# ---
commandline_arguments_options = "--listen --enable-insecure-extension-access --theme dark --no-half-vae --disable-console-progressbars --xformers"
commandline_arguments_widget = widgets.Text(description='Arguments:', value=commandline_arguments_options, style=style, layout=layout)

''' Display Additional'''
additional_widget_list = [additional_header, latest_changes_widget, HR, controlnet_widget, controlnet_Num_widget, commit_hash_widget, optional_huggingface_token_widget, ngrok_widget, zrok_widget, HR, commandline_arguments_widget]
if free_plan and env == "Google Colab": # remove ngrok from colab
    additional_widget_list.remove(ngrok_widget)
# ```
all_additional_box = widgets.VBox(additional_widget_list).add_class("container").add_class("image_3")
display(all_additional_box)

# --- CUSTOM DOWNLOAD ---
custom_download_header_popup = widgets.HTML('''
<style>
/* Term Colors */
.sample_label {color: #dbafff;}
.braces {color: #ffff00;}
.extension {color: #eb934b;}
.file_name {color: #ffffd8;}
</style>

<div class="header" style="cursor: pointer;" onclick="toggleContainer()">Custom Download</div>
<!-- PopUp Window -->
<div class="info">INFO</div>
<div class="popup">
    Separate multiple URLs with a comma/space. For a <span class="file_name">custom name</span> file/extension, specify it with <span class="braces">[]</span>
    after the URL without spaces.
    <span style="color: #ff9999">For files, be sure to specify</span> - <span class="extension">Filename Extension.</span>
    <div class="sample">
        <span class="sample_label">Example for File:</span>
        https://civitai.com/api/download/models/229782<span class="braces">[</span><span class="file_name">Detailer</span><span class="extension">.safetensors</span><span class="braces">]</span>
        <br>
        <span class="sample_label">Example for Extension:</span>
        https://github.com/hako-mikan/sd-webui-regional-prompter<span class="braces">[</span><span class="file_name">Regional-Prompter</span><span class="braces">]</span>
    </div>
</div>
''')
# ---
Model_url_widget = widgets.Text(description='Model:', style=style, layout=layout)
Vae_url_widget = widgets.Text(description='Vae:', style=style, layout=layout)
LoRA_url_widget = widgets.Text(description='LoRa:', style=style, layout=layout)
Embedding_url_widget = widgets.Text(description='Embedding:', style=style, layout=layout)
Extensions_url_widget = widgets.Text(description='Extensions:', style=style, layout=layout)
custom_file_urls_widget = widgets.Text(description='File (txt):', style=style, layout=layout)

''' Display CustomDl'''
all_custom_box = widgets.VBox([
    custom_download_header_popup, Model_url_widget, Vae_url_widget, LoRA_url_widget, Embedding_url_widget, Extensions_url_widget, custom_file_urls_widget
    ]).add_class("container").add_class("image_4").add_class("container_custom_downlad")
display(all_custom_box)

# --- Save Button ---
save_button = widgets.Button(description='Save').add_class("button_save")
display(save_button)


# ============ Load / Save - Settings V2 ============
SETTINGS_FILE = f'{root_path}/settings.json'

settings_keys = [
    'Model', 'Model_Num', 'Inpainting_Model',
    'Vae', 'Vae_Num',
    'latest_webui', 'latest_exstensions', 'detailed_download',
    'controlnet', 'controlnet_Num', 'commit_hash', 'optional_huggingface_token',
    'ngrok_token', 'zrok_token', 'commandline_arguments',
    'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'custom_file_urls'
]

def save_settings():
    settings = {key: globals()[f"{key}_widget"].value for key in settings_keys}
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            for key in settings_keys:
                globals()[f"{key}_widget"].value = settings.get(key)

def save_data(button):
    save_settings()

    # --- uhh - hide... ---
    widgets_list = [all_model_box, all_vae_box, all_additional_box, all_custom_box, save_button]
    for widget in widgets_list:
        widget.add_class("hide")
    time.sleep(0.5)

    widgets.Widget.close_all()

settings = load_settings()
save_button.on_click(save_data)

