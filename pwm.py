#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

def print_hex(bits):
    hex_str = ''
    while len(bits) % 8 != 0:
        bits.insert(0,0)
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        if len(byte) == 8:
            hex_str += '{:02x}'.format(int(''.join(map(str, byte)), 2))
    return hex_str

fn = "samples/CAME_433.92M_250k.cu8" # d7923f
#fn = "samples/g002_433.92M_250k.cu8" # d7923f
#fn = "samples/Button1_433.83M_250k.cu8" # 0473
#fn = "samples/Button2_433.83M_250k.cu8" # 0873

data = np.fromfile(fn, dtype="uint8")
fs = 250000

if 0:
	data = data[0::2] + 1j * data[1::2]
	plt.specgram(data, NFFT=1024, Fs=fs)
	plt.title(fn)
	plt.xlabel("Time")
	plt.ylabel("Frequency")
	plt.show()

i = ( data[0::2] - 127.5 ) / 128 # Imaginary
q = ( data[1::2] - 127.5 ) / 128 # Real
amplitude = np.sqrt(i**2 + q**2)
threshold = np.mean(amplitude) * 3
binary_signal = amplitude > threshold

if 0:
	print("Threshold: ", threshold)
	plt.axhline(y=threshold, color='yellow', linestyle='-')
	plt.plot(i, label='I')
	plt.plot(q, label='Q')
	plt.plot(amplitude, label='Amplitude')
	plt.plot(binary_signal, label='Binary')
	plt.grid(True)
	plt.tight_layout()
	plt.show()
# https://github.com/psa-jforestier/rtl_433_tests/tree/master/tests/Came/TOP432
# Decode the Pulse Width Modulation (PWM) signal
# - 0 is encoded as 320 us gap and 640 us pulse,
# - 1 is encoded as 640 us gap and 320 us pulse.
# The device sends a 4 times the packet when a button on the remote control is pressed.
# A transmission starts with a 320 us pulse. At the end of the packet, there is a minimum of 36 periods of 320us between messages (11520us)
bits = []
count = duration = start_signal = 0
current_level = binary_signal[0]
sample_time = 1 / fs * 1000000
for level in binary_signal:
    if level == current_level:
        count += 1
    else:
        duration = count * sample_time
        if current_level:
            #print('Pulse duration:', duration)
            if 160 < duration and duration < 480: # center 320
                if start_signal: # do not count first pulse
                    bits.append(1)
                    #print('Added 1 ', duration)
                start_signal = 1
            elif 480 <= duration and duration < 800: # center 640:
                bits.append(0)
                #print('Added 0 ', duration)
        #else:
        #	print('Gap duration:', duration)
        if 10000 <= duration and bits: # gap
            print('HEX: ', print_hex(bits))
            bits = []; start_signal = 0
        count = 1
        current_level = level
print('HEX: ', print_hex(bits))
