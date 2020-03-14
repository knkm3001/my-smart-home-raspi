import pigpio
import time

GPIO = 17 # PWMがつかえるピン
FREQ = 38 # kHz

def exec_infrared_code(code):
    """
    postされた赤外線コードのデータをもとに実行
    """

    T = int(code['base_time'])
    
    pi = pigpio.pi()
    pi.wave_clear()

    # Create wave
    marks_wid = {}
    spaces_wid = {}
    wave = []

    for signal in code['signal']:
        
        if  type(signal) is list: # リーダー部,繰り返し指示部などの外れ値の処理
            wf = carrier(GPIO, FREQ, T*signal[0])
            pi.wave_add_generic(wf)
            wave.append(pi.wave_create())
            pi.wave_add_generic([pigpio.pulse(0, 0, T*signal[1])])
            wave.append(pi.wave_create())
        
        else: # 16進数の信号部の処理

            # 2進数に変換して0,1ごとのことなる信号にエンコード
            binary_signal = zero_padding_x2b(signal)
            for binary_val in binary_signal:
                if binary_val == '1':
                    sec_arr = [T,T*3]
                else:
                    sec_arr = [T,T]
    
                for j,sec in enumerate(sec_arr):
                    if j == 1: # Space
                        if sec not in spaces_wid:
                            pi.wave_add_generic([pigpio.pulse(0, 0, sec)])
                            spaces_wid[sec] = pi.wave_create()
                        wave.append(spaces_wid[sec])
                    else: # Mark
                        if sec not in marks_wid:
                            wf = carrier(GPIO, FREQ, sec)
                            pi.wave_add_generic(wf)
                            marks_wid[sec] = pi.wave_create()
                        wave.append(marks_wid[sec])
            
    pi.wave_chain(wave)
    while pi.wave_tx_busy():
        time.sleep(0.1)
    pi.wave_clear()
    pi.stop()


def carrier(gpio, frequency, micros):
    """
    Generate carrier square wave.

    irrp.py から拝借
    """
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros/cycle))
    on = int(round(cycle / 2.0))
    sofar = 0
    for c in range(cycles):
        target = int(round((c+1)*cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1<<gpio, 0, on))
        wf.append(pigpio.pulse(0, 1<<gpio, off))
    return wf


def zero_padding_x2b(hexadecimal_data):
    """
    16進数表記の文字列を2進数に変換。

    このとき0埋めを行うが、もとの2進数とはかならずしも一致しない。
    なぜかというと、もとの2進数の桁数がわかる方法は現状存在せず、
    変換した2進数の文字列は自動的に変換前の2進数の桁数を満たすある4桁の値になってしまうため。
    つまり桁数が1~3つふえてしまう。

    ex.1 もとの2進数が4の倍数の桁数ならば、この関数で変換した2進数の値と一致
            00001111 ->  0f ->     00001111 桁数一致
    ex.2 もとの2進数が4の倍数でなければ、この関数で変換した2進数の値と一致
          0000001111 -> 00f -> 000000001111 12桁 2つ増える
    """

    holder = len(hexadecimal_data)*4
    palam = '0'+str(holder)+'b'
    return format(int(hexadecimal_data, 16), palam)
