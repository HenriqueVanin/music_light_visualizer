import pyaudio
import numpy as np
import serial
import time
import struct
import pyaudio
import wave
import audioop

arduino = serial.Serial('COM9', 115200, timeout=.1)

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

np.set_printoptions(suppress=True)  # don't use scientific notation

RATE = 6410  # time resolution of the recording device (Hz)
CHUNK = int(RATE / 20)  # number of data points to read at a time
#CHUNK2 = 3096  # number of data points to read at a time
CHUNK2 = CHUNK
p = pyaudio.PyAudio()  # start the PyAudio class

stream_vol = p.open(format=pyaudio.paInt16, channels=2, rate=RATE, input=True,
                frames_per_buffer=CHUNK)  # uses default input device
stream_freq = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                frames_per_buffer=CHUNK2)  # uses default input device
volume = 0
frequencia = 0

while True:
    data2 = np.fromstring(stream_freq.read(CHUNK2), dtype=np.int16)
    data2 = data2 * np.hanning(len(data2))  # smooth the FFT by windowing data
    fft = abs(np.fft.fft(data2).real)
    fft = fft[:int(len(fft) / 2)]  # keep only first half
    freq = np.fft.fftfreq(CHUNK2, 1.0 / RATE)
    freq = freq[:int(len(freq) / 2)]  # keep only first half
    freqPeak = freq[np.where(fft == np.max(fft))[0][0]] + 1

    freqPeak = freqPeak * 0.1275 - 9
    print("peak frequency: %d Hz" % freqPeak)
    if freqPeak < 0:
        arduino.write(struct.pack('>B', int(0)))
    elif freqPeak > 255:
        arduino.write(struct.pack('>B', int(255)))
    elif freqPeak <= 255 and freqPeak >= 0:
        arduino.write(struct.pack('>B', int(freqPeak)))

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream_vol.read(CHUNK)
        rms = audioop.rms(data, 2)    # here's where you calculate the volume

    rms = rms * 0.0255
    if rms > 255:
        arduino.write(struct.pack('>B', int(255)))

    elif rms <= 255:
        arduino.write(struct.pack('>B', int(rms)))

    print("volume: %d" % rms)


# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()