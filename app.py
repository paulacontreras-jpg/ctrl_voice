import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator
 
# ---------- Configuración de la página ----------
st.set_page_config(page_title="Comando Neón · Control por Voz", page_icon="🎙️", layout="centered")
 
# ---------- Estilos (temática ciberpunk / neón) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600&display=swap');
 
    html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
 
    .stApp {
        background:
            radial-gradient(circle at 20% 10%, rgba(255, 0, 200, 0.18), transparent 40%),
            radial-gradient(circle at 80% 90%, rgba(0, 229, 255, 0.18), transparent 40%),
            #0b0b1a;
        color: #e6e6ff;
    }
 
    .hero {
        text-align: center;
        padding: 26px 18px;
        border: 2px solid #00e5ff;
        border-radius: 18px;
        background: rgba(10, 10, 30, 0.75);
        box-shadow: 0 0 18px #00e5ff, inset 0 0 18px rgba(255, 0, 200, 0.25);
        margin-bottom: 26px;
    }
    .hero h1 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.1rem;
        margin: 0;
        color: #fff;
        text-shadow: 0 0 8px #ff00c8, 0 0 18px #ff00c8, 0 0 32px #00e5ff;
    }
    .hero p { margin: 10px 0 0; font-size: 1.15rem; color: #b8f4ff; }
 
    .panel {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-left: 5px solid #ff00c8;
        padding: 6px 14px;
        margin: 22px 0 12px;
        font-size: 1rem;
        text-shadow: 0 0 8px #00e5ff;
    }
 
    /* Imagen con borde neón */
    [data-testid="stImage"] img {
        border-radius: 50%;
        border: 3px solid #ff00c8;
        box-shadow: 0 0 20px #ff00c8, 0 0 40px rgba(0, 229, 255, 0.5);
    }
 
    .stMarkdown p { color: #d8d8ff; }
 
    .footer {
        text-align: center;
        margin-top: 34px;
        font-size: .85rem;
        color: #7a7aa8;
        letter-spacing: 1px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ---------- Lógica MQTT (sin cambios) ----------
def on_publish(client, userdata, result):  # create function for callback
    print("el dato ha sido publicado \n")
    pass
 
 
def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)
 
 
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message
 
# ---------- Encabezado ----------
st.markdown(
    """
    <div class="hero">
        <h1>🎙️ COMANDO NEÓN</h1>
        <p>Habla y tu voz se convierte en una orden:<br>
        el texto que dictes se envía al instante a tus dispositivos por MQTT.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
 
image = Image.open('voice_ctrl.jpg')
 
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image(image, width=200)
 
# ---------- Panel de voz ----------
st.markdown('<div class="panel">▶ Toca el botón y habla</div>', unsafe_allow_html=True)
 
stt_button = Button(label="🎤 INICIAR ESCUCHA", width=200, button_type="success")
 
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))
 
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)
 
if result:
    if "GET_TEXT" in result:
        st.markdown('<div class="panel">📡 Comando recibido</div>', unsafe_allow_html=True)
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl", message)
 
    try:
        os.mkdir("temp")
    except:
        pass
 
# ---------- Pie de página ----------
st.markdown(
    f'<div class="footer">⚡ CANAL MQTT: voice_ctrl · BROKER: {broker}:{port}</div>',
    unsafe_allow_html=True,
)
