import sys
import json
import argparse

p = argparse.ArgumentParser()
p.add_argument("-f", "--file", help="Filename", required=True)
p.add_argument('-i',"--id",    help="IR codes", default=None)
p.add_argument('-m',"--maker", help="IR codes", default=None)

args = p.parse_args()
FILE  = args.file
MAKER = args.maker
ID    = args.id


def zero_padding_b2x(binary_data):
    """
    2進数表記の文字列を16進数に変換。
    このときちゃんと0埋めする。

    ex.1    00001111 ->  0f
    ex.2   000001111 -> 00f
    """
    # binary_dataの文字数を収めきる4の倍数の値
    holder = len(binary_data)//4 if len(binary_data)%4 == 0 else len(binary_data)//4+1 
    palam = '0'+str(holder)+'x'
    return format(int(binary_data, 2), palam)



def specify_format_type(raw_code):
    """
    コマンドライン引数でメーカーが与えられてなかったらここで特定する
    """
    import collections

    c = collections.Counter([raw_code[i] for i in range(0,len(raw_code),2)])
    mode = c.most_common()[0][0]
    sum_e = 0
    cnt_e = 0
    for e in c.most_common():
        if 0.75*mode <= e[0] <= 1.5*mode:
            sum_e += e[0]*e[1] # 重み付けした各値の合計
            cnt_e += e[1]
    expected_T = round(sum_e/cnt_e,1)
    

    leader_part_microsec = raw_code[0] + raw_code[1]

    if 18 <= leader_part_microsec/expected_T <= 32: # NECは24T
        return 'NEC'
    elif 6 <= leader_part_microsec/expected_T < 18: # AEHAは12T
        return 'AEHA'
    elif 2 <= leader_part_microsec/expected_T < 6: # SONYは4T
        return 'SONY'
    else:
        return None


def decode_signal(raw_code,format_tyoe):
    """

    信号はON,OFFの連続値。それぞれの時間がcodeには記録されてる
    実際に必要なのはOFFの時間で、これがONの時間(tのこと)の何倍かで0,1を判断する
    NEC,AEHA 0...ON:OFF=1:1  1...ON:OFF=1:3
    sony     0...ON:OFF=1:1  1...ON:OFF=2:1
    """

    if not format_tyoe:
        format_tyoe = specify_format_type(raw_code)
        print('特定したフォーマット: ',format_tyoe)
    
    # 各メーカーごとのリーダー部の長さ。
    # たとえばNECならリーダー部は24Tということ
    if format_tyoe == 'NEC':
        t_range = 24.0
    elif format_tyoe == "AEHA":
        t_range = 12.0
    elif format_tyoe == "SONY":
        t_range = 4.0
        sys.exit('SONY製はまだ対応できてないです...(._.)')
    else:
        sys.exit('メーカーが特定できませんでした')

    code = {}

    binary_data = ""
    base_time = round((raw_code[0]+raw_code[1])/t_range) # このtの値は信号がONの時間のこと
    print('base_time:',base_time)

    code['base_time'] = base_time
    code['signal'] = []

    for i in range(0,len(raw_code)-1, 2):
       
        # 外れ値対策(リーダー部やリピート指示部など)
        if raw_code[i] > base_time*3 or raw_code[i+1] > base_time*6:
            if binary_data:
                code['signal'].append(zero_padding_b2x(binary_data)) # 2進数を16進数に
                binary_data = ""

            print('外れ値: ',raw_code[i],raw_code[i+1])
            code['signal'].append([round(raw_code[i]/base_time), round(raw_code[i+1]/base_time)])
            continue
        
        if raw_code[i + 1] < base_time * 2.0:
            binary_data += "0"
        elif raw_code[i + 1] < base_time * 6.0:
            binary_data += "1"

    code['signal'].append(zero_padding_b2x(binary_data)) # 2進数を16進数に

    # 奇数対策(あるとしたら最後)
    if len(raw_code)%2 == 1:
        code['signal'].append([round(raw_code[i]/base_time), 1])

    print('code: ',json.dumps(code))


if __name__ == '__main__':


    with open(FILE, "r") as f:
        raw_codes = json.load(f)

    if ID and ID in raw_codes:
        decode_signal(raw_codes[ID],MAKER)
    else:
        for k,v in raw_codes.items():
            print('key:',k)
            decode_signal(raw_codes[k],MAKER)
            print('\n')



