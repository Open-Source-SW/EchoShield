import requests
import json
import sounddevice as sd
import numpy as np

# MN-CSE로 데이터 전송을 위한 URL
MN_CSE_URL = "http://localhost:8081/cse-mn/NoiseDetectionSensor/NoiseData"
SEND_HEADERS = {
    "X-M2M-Origin": "CSensor",
    "X-M2M-RI": "create_cin",
    "X-M2M-RVI": "3",
    "Content-Type": "application/json;ty=4"
}

# 샘플링 주파수와 버퍼 크기
fs = 44100
buffer_size = 1024
noise_frequencies = [50, 100]  # 노이즈 주파수 설정
buffer = np.zeros(buffer_size)  # 버퍼 초기화

def send_audio_to_mn_cse(audio_buffer):
    """
    MN-CSE로 음향 데이터를 전송합니다.
    """
    payload = {
        "m2m:cin": {
            "con": json.dumps(audio_buffer.tolist())  # NumPy 배열을 JSON으로 변환
        }
    }
    try:
        response = requests.post(MN_CSE_URL, headers=SEND_HEADERS, json=payload)
        if response.status_code == 201:
            print("[INFO] Audio data sent to MN-CSE successfully.")
        else:
            print(f"[ERROR] Failed to send audio data: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error sending audio data: {e}")

def generate_noise_data():
    """
    노이즈 데이터를 생성합니다.
    """
    global buffer
    try:
        input_stream = sd.InputStream(channels=1, samplerate=fs, blocksize=buffer_size)
        input_stream.start()

        audio_data, _ = input_stream.read(buffer_size)
        audio_data = np.clip(audio_data[:, 0], -1, 1)  # 한 채널만 사용

        # 버퍼에 새 데이터 추가
        buffer = np.roll(buffer, -buffer_size)
        buffer[-buffer_size:] = audio_data

        input_stream.stop()
        input_stream.close()

    except sd.PortAudioError as e:
        print(f"[ERROR] PortAudioError: {e}")
        buffer = np.zeros(buffer_size)  # 문제 발생 시 빈 데이터를 반환

    return buffer

def sensor_operation():
    global input_stream
    try:
        while True:
            print("[INFO] Sensor activated. sending noise data.")
            noise_data = generate_noise_data()  # 1초 간의 노이즈 데이터 생성
            send_audio_to_mn_cse(noise_data)  # 생성된 데이터를 MN-CSE로 전송

    except KeyboardInterrupt:
        print("[INFO] Sensor operation interrupted by user. Exiting.")
        input_stream.stop()
        input_stream.close()


if __name__ == "__main__":
    sensor_operation()