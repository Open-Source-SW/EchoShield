import numpy as np
from flask import Flask, request, jsonify
import sounddevice as sd
import requests
import json
import threading
import time

app = Flask(__name__)

class TextStyles:
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'  # Reset to default style


# 샘플링 주파수와 버퍼 크기
fs = 44100
buffer_size = 1024

PROCESSOR_NOISEDATA_URL = "http://localhost:8081/cse-mn/NoiseCancellationSystem/NoiseData/la"

PROCESSOR_HEADERS = {
    "X-M2M-Origin": "CAdmin",
    "X-M2M-RI": "retrieve_cin",
    "X-M2M-RVI": "3",
    "Accept": "application/json",
    "Content-Type": "application/json;ty=4"
}

# 스피커 상태 관리
speaker_active = False
speaker_thread = None

def get_latest_cancellation_signal():
    """
    MN-CSE의 NoiseData에서 최신 신호 데이터를 조회합니다.
    """
    try:
        response = requests.get(PROCESSOR_NOISEDATA_URL, headers=PROCESSOR_HEADERS)
        if response.status_code == 200:
            received_payload = response.json()
            cancellation_signal_str = json.loads(received_payload["m2m:cin"]["con"])  # 문자열 배열
            cancellation_signal = np.array(cancellation_signal_str, dtype=np.complex128)  # 복소수로 변환
            return cancellation_signal
        else:
            print(f"[ERROR] Failed to get cancellation data: {response.status_code}")
            return np.zeros(buffer_size)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching cancellation data: {e}")
        return np.zeros(buffer_size)

def play_cancellation_signal(signal):
    """
    상쇄 신호를 스피커로 출력합니다.
    """
    try:
        # 복소수 신호를 실수 신호로 변환
        real_signal = np.real(signal)  # 복소수의 실수 부분만 추출
        sd.play(real_signal, samplerate=fs)
        sd.wait()
    except Exception as e:
        print(f"[ERROR] Error playing signal: {e}")

def speaker_loop():
    """
    스피커 작업을 실행하는 루프. speaker_active 상태에 따라 동작.
    """
    global speaker_active
    while speaker_active:
        cancellation_signal = get_latest_cancellation_signal()
        play_cancellation_signal(cancellation_signal)
        time.sleep(1)  # 신호를 일정 주기로 가져오도록 대기

@app.route('/notification', methods=['POST'])
def notification():
    global speaker_active, speaker_thread
    try:
        data = request.json 
        con = json.loads(data["m2m:sgn"]["nev"]["rep"]["m2m:cin"]["con"])
        status = con.get("status")
        if status == "start":
            if not speaker_active:
                print(f"{TextStyles.BOLD}{TextStyles.GREEN}[INFO] Speaker is now being activated.{TextStyles.RESET}")
                speaker_active = True
                speaker_thread = threading.Thread(target=speaker_loop, daemon=True)
                speaker_thread.start()
            else:
                print("[INFO] Speaker is already active.")
        elif status == "stop":
            if speaker_active:
                print(f"{TextStyles.BOLD}{TextStyles.RED}[INFO] Speaker is now being deactivated.{TextStyles.RESET}")
                speaker_active = False
                if speaker_thread:
                    speaker_thread.join()  # 스레드 종료 대기
        else:
            print(f"[WARNING] Unrecognized status received: {status}")

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[ERROR] Error while processing notification: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)