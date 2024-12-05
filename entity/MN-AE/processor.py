import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import requests
import time
import json

# 샘플링 주파수와 버퍼 크기
fs = 44100
buffer_size = 1024
noise_frequencies = [50, 100]

# 그래프 설정
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

# 첫 번째 그래프: 입력 신호
ax1.set_title("Input Signal (dB)")
input_line, = ax1.plot([], [], color="blue", label="Input Signal (dB)")
ax1.set_xlim(0, 200)
ax1.set_ylim(-150, 0)
ax1.set_ylabel("dB Level")
ax1.legend()

# 두 번째 그래프: 처리된 신호 (소음 상쇄 후)
ax2.set_title("Processed Output Signal (Noise Reduction Applied)")
output_line, = ax2.plot([], [], color="green", label="Processed Output Signal (dB)")
ax2.set_xlim(0, 200)
ax2.set_ylim(-150, 0)
ax2.set_ylabel("dB Level")
ax2.legend()

# 세 번째 그래프: 입력과 출력 차이 및 반대 위상
ax3.set_title("Difference (Input - Processed Output) and Opposite Phase Signal (dB)")
difference_line, = ax3.plot([], [], color="red", label="Difference (dB)")
opposite_phase_line, = ax3.plot([], [], color="orange", label="Opposite Phase Signal (dB)")
ax3.set_xlim(0, 200)
ax3.set_ylim(-50, 0)
ax3.set_ylabel("dB Difference")
ax3.legend()

# MN-CSE 설정
SENSOR_NOISEDATA_URL = "http://localhost:8081/cse-mn/NoiseDetectionSensor/NoiseData/la"
PROCESSOR_NOISEDATA_URL = "http://localhost:8081/cse-mn/NoiseCancellationSystem/NoiseData"
PROCESSOR_AVERAGE_URL = "http://localhost:8081/cse-mn/NoiseCancellationSystem/Average"

SENSOR_HEADERS = {
    "X-M2M-Origin": "CSensor",
    "X-M2M-RI": "retrieve_cin",
    "X-M2M-RVI": "3",
    "Accept": "application/json",
    "Content-Type": "application/json;ty=4"
}

PROCESSOR_HEADERS = {
    "X-M2M-Origin": "CAdmin",
    "X-M2M-RI": "create_cin",
    "X-M2M-RVI": "3",
    "Accept": "application/json",
    "Content-Type": "application/json;ty=4"
}

# 주파수 분석 및 소음 제거 함수 (반대 위상 생성)
def frequency_based_noise_reduction(data, noise_freqs, reduction_factor=0.5):
    # 푸리에 변환을 통해 주파수 분석
    freqs = np.fft.fftfreq(len(data), 1/fs)
    fft_data = np.fft.fft(data)
    
    # 특정 주파수에서의 성분을 찾아서 상쇄
    opposite_phase_signal = np.zeros_like(fft_data)
    for freq in noise_freqs:
        freq_bin = np.argmin(np.abs(freqs - freq))  # 해당 주파수의 인덱스 찾기
        # 역위상 신호 생성
        opposite_phase_signal[freq_bin] = -fft_data[freq_bin] * reduction_factor  # 역위상 적용
    
    # 역푸리에 변환을 통해 반대 위상 신호 복원
    opposite_phase_data = np.fft.ifft(opposite_phase_signal)
    
    # 소음 제거된 신호 계산 (상쇄된 신호)
    # processed_data = np.real(fft_data) - np.real(opposite_phase_data)
    processed_data = np.real(fft_data) - np.real(opposite_phase_data)
    
    return processed_data, opposite_phase_data

# 최신 신호 데이터 가져오기
def get_latest_noise_data():
    """
    Sensor/NoiseData에서 최신 신호 데이터를 조회합니다.
    """
    try:
        response = requests.get(SENSOR_NOISEDATA_URL, headers=SENSOR_HEADERS)
        if response.status_code == 200:
            latest_resource = response.json()
            noise_data = json.loads(latest_resource["m2m:cin"]["con"])
            return np.array(noise_data)
        else:
            print(f"[ERROR] Failed to get noise data: {response.status_code}")
            return np.zeros(buffer_size)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching noise data: {e}")
        return np.zeros(buffer_size)

# 상쇄 신호 생성 및 전송
def send_cancellation_signal(cancellation_signal):
    """
    상쇄 신호를 생성하고 MN-CSE에 저장합니다.
    """

    payload = {
        "m2m:cin": {
            "con": json.dumps(cancellation_signal.astype(str).tolist()) 
        }
    }
    try:
        response = requests.post(PROCESSOR_NOISEDATA_URL, headers=PROCESSOR_HEADERS, json=payload)
        if response.status_code == 201:
            print("[INFO] Cancellation signal sent successfully.")
        else:
            print(f"[ERROR] Failed to send cancellation signal: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error sending cancellation signal: {e}")

# 평균값 전송
def send_average_db(average_db):
    payload = {
        "m2m:cin": {
            "con": str(average_db)
        }
    }
    try:
        response = requests.post(PROCESSOR_AVERAGE_URL, headers=PROCESSOR_HEADERS, json=payload)
        if response.status_code == 201:
            print(f"[INFO] Average dB ({average_db:.2f}) sent successfully.")
        else:
            print(f"[ERROR] Failed to send average dB: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error sending average dB: {e}")

# 애니메이션 업데이트 함수
input_dB_list, output_dB_list, difference_dB_list, opposite_dB_list = [], [], [], []

## avg
average_dB_list = []
last_average_time = time.time()



def processor_operation(frame):
    global input_dB_list, output_dB_list, difference_dB_list, opposite_dB_list, buffer, last_average_time

    buffer = get_latest_noise_data()
    processed_data, opposite_phase_data = frequency_based_noise_reduction(buffer, noise_frequencies)

    send_cancellation_signal(opposite_phase_data)

    input_rms = np.sqrt(np.mean(buffer**2))
    input_dB = 20 * np.log10(input_rms + 1e-10)

    # 처리된 신호의 데시벨 계산
    processed_rms = np.sqrt(np.mean(processed_data**2))
    output_dB = 20 * np.log10(processed_rms + 1e-10)

    # 반대 위상 신호의 데시벨 계산
    opposite_rms = np.sqrt(np.mean(opposite_phase_data**2))
    opposite_dB = 20 * np.log10(opposite_rms + 1e-10)

    input_dB_list.append(input_dB)
    output_dB_list.append(output_dB)
    difference_dB_list.append(input_dB - output_dB)
    opposite_dB_list.append(opposite_dB)

    if time.time() - last_average_time >= 600:  # 10분 경과 확인
        average_dB = np.mean(input_dB_list[-(fs // buffer_size * 600):])  # 최근 10분 평균
        send_average_db(average_dB)
        last_average_time = time.time()

    x_data = range(len(input_dB_list))
    input_line.set_data(x_data, input_dB_list)
    output_line.set_data(x_data, output_dB_list)
    difference_line.set_data(x_data, difference_dB_list)
    opposite_phase_line.set_data(x_data, opposite_dB_list)

    # x축 범위 업데이트
    ax1.set_xlim(0, max(200, len(x_data)))
    ax2.set_xlim(0, max(200, len(x_data)))
    ax3.set_xlim(0, max(200, len(x_data)))

    # 콘솔 출력
    print(f"Input dB: {input_dB:.2f}, Output dB: {output_dB:.2f}, Opposite Phase dB: {opposite_dB:.2f}")

    return input_line, output_line, difference_line, opposite_phase_line


if __name__ == "__main__":
    ani = FuncAnimation(fig, processor_operation, interval=50, blit=True)
    plt.tight_layout()
    plt.show()
