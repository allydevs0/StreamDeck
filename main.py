import sys
import threading
import requests
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout, QComboBox
from PyQt5.QtGui import QPixmap
from flask import Flask, request, jsonify, render_template
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
import qrcode
from PIL import Image
import psutil

app = Flask(__name__)

languages = {
    'en': {
        'mute': 'Mute',
        'volume': 'Volume',
        'volume_label': 'Volume: {}%',
        'qr_code': 'Scan to control volume',
        'status_unmuted': 'Status: Unmuted',
        'other_action_executed': 'Executed Other Action',
        'volume_set': 'Volume Set to: {}%'
    },
    'pt': {
        'mute': 'Mudo',
        'volume': 'Volume',
        'volume_label': 'Volume: {}%',
        'qr_code': 'Escaneie para controlar o volume',
        'status_unmuted': 'Estado: Desmutado',
        'other_action_executed': 'Executou Outra Ação',
        'volume_set': 'Volume Setado em: {}%'
    }
}

current_language = 'en'


def find_and_terminate_flask_processes():
    for process in psutil.process_iter():
        if "flask" in process.name().lower():
            process.terminate()

# Calling the function to find and terminate previous Flask processes
find_and_terminate_flask_processes()

def set_volume(level):
    CoInitialize()  # Initialize the COM library
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        # Convert volume level to a float and calculate linear volume (0.0 to 1.0)
        volume_level = float(level) / 100.0
        volume.SetMasterVolumeLevelScalar(volume_level, None)
    finally:
        CoUninitialize()  # Release the COM library

@app.route('/')
def index():
    print("Received request for index page")
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    print("Received POST request for action")
    data = request.json
    print("Received data:", data)
    button_pressed = data['button']
    response = ""
    
    if button_pressed == 'mute':
        response = languages[current_language]['status_unmuted']
    elif button_pressed == 'other_action':
        response = languages[current_language]['other_action_executed']
    elif button_pressed == 'volume':
        volume_level = data['level']
        set_volume(volume_level)
        response = languages[current_language]['volume_set'].format(volume_level)
    
    return jsonify({'message': response}), 200

def handle_action(button, level=None):
    data = {'button': button}
    if level is not None:
        data['level'] = level

    response = requests.post('http://127.0.0.1:9992/action', json=data)
    if response.status_code == 200:
        data = response.json()
        message = data['message']
        print(message)

def run_flask():
    app.run(host='0.0.0.0', port=9992)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Volume Control")
        layout = QVBoxLayout()

        # Language Selector
        self.language_selector = QComboBox()
        self.language_selector.addItems(['English', 'Português'])
        self.language_selector.currentIndexChanged.connect(self.change_language)

        # Mute Button
        self.mute_button = QPushButton(languages[current_language]['mute'])
        self.mute_button.clicked.connect(lambda: handle_action('mute'))

        # Volume Slider
        self.volume_slider = QSlider()
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        # Volume Label
        self.volume_label = QLabel(languages[current_language]['volume_label'].format(50))

        # Add widgets to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.mute_button)

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)

        # Get local IP address and port
        ip = socket.gethostbyname(socket.gethostname())
        port = 9992
        url = f"http://{ip}:{port}"

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("temp_qr_code.png")

        # Convert to QPixmap
        qr_pixmap = QPixmap("temp_qr_code.png")
        qr_label = QLabel()
        qr_label.setPixmap(qr_pixmap)

        layout.addWidget(self.language_selector)
        layout.addLayout(button_layout)
        layout.addLayout(volume_layout)
        layout.addWidget(qr_label)

        self.setLayout(layout)

    def change_language(self, index):
        global current_language
        if index == 0:
            current_language = 'en'
        else:
            current_language = 'pt'
        
        self.mute_button.setText(languages[current_language]['mute'])
        self.volume_label.setText(languages[current_language]['volume_label'].format(self.volume_slider.value()))

    def change_volume(self, value):
        self.volume_label.setText(languages[current_language]['volume_label'].format(value))
        handle_action('volume', level=value)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
