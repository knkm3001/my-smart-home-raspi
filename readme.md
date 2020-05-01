# my-smart-home-raspi
my-smart-home のラズパイを使用していたときのもの。保存用として残している。
現在はESP32を使っているため、こちらは使用していない。

## 概要
参考サイトをもとにraspiを使って家の赤外線リモコンを操作できるスマートリモコンを作成してみた。  
[irrp.py](http://abyz.me.uk/rpi/pigpio/examples.html#Python_irrp_py) を使って赤外線リモコンの送信データを取得、それをjsonデータに変換する。  
ラズパイに立てたapiサーバに、先程のjsonデータをポストすると、  
そのフォーマットに従って赤外線LEDをLチカさせ、リモコンとしての操作ができる。

以下URLを参考にした。  
[格安スマートリモコンの作り方](https://qiita.com/takjg/items/e6b8af53421be54b62c9)  
[うたかたサバイバー Raspberry Piでエアコンの赤外線リモコンを解析する](https://paltee.net/archives/247)  
[電脳伝説 赤外線LEDドライブ回路の決定版](https://vintagechips.wordpress.com/2013/10/05%E8%B5%A4%E5%A4%96%E7%B7%9Aled%E3%83%89%E3%83%A9%E3%82%A4%E3%83%96%E5%9B%9E%E8%B7%AF%E3%81%AE%E6%B1%BA%E5%AE%9A%E7%89%88/)  
[赤外線リモコンの通信フォーマット](http://elm-chan.org/docs/ir_format.html)  
[irrp.py](http://abyz.me.uk/rpi/pigpio/examples.html#Python_irrp_py) 

## TODO
- readmeをもう少し丁寧に書く
- 16進数表記の信号のバイナリをもうちょっとしっかり読み解いてみる
- SONY製品はまだ未対応なのでやってみる
- APIサーバが雑なのでいい感じにする

## 使用した道具や部品

|  部品名 |  個数  |
| ---- | ---- |
|  raspi3 modelB  |1台|
|  赤外線リモコン受信モジュール<br>OSRB38C9AA|1つ|
|MOSFET 2N7000|1つ|
|MOSFET IRFU9024NPBF|1つ|
|赤外線LED OSI5LA5113A|2つ|
|抵抗 4.7kΩ 1/2W|1つ|
|抵抗 27Ω 1W|4つ|
|プレッドボード|1つ|
|ジャンパワイヤ|複数本|

## 手順
1. 回路を作成  
(ちゃんとしたのをあとで書き加えておきます。)

1. 赤外線信号データを取得  
  [irrp.py](http://abyz.me.uk/rpi/pigpio/examples.html#Python_irrp_py) というスクリプトをダウンロードする。  
  これを使って送信された赤外線信号データを取得。  
  下のコマンドをつかって家にある三菱製エアコンのリモコン(型番:NH151 709AL)の  
  電源ONボタンを記録することにした。  
  ```python irrp.py -r -g18 -f codes aircon:on --no-confirm```  
  コマンドを実行すると codes というファイルにリモコンが送信した信号データの  
  パルスのONとOFFの時間が交互に記載されている。  
  このONとOFFの時間をもとに0,1を表現し、信号の波形を送っている。  
  参考: [赤外線リモコンの通信フォーマット](http://elm-chan.org/docs/ir_format.html)

1. 本レポジトリからソースをダウンロード  
    git clone でもなんでも。  

1. POSTするjsonデータを取得   
  つぎに codes に記載された先程の信号データをもとに、POST用のjsonを作成。  
  ``` python decode.py -f codes -i aircon:on ```  
  出力された code: hogehoge の部分がpostするべきjsonのデータ。   
  base_timeはパルス信号の単位周期のこと。これがONの時間にあたる。  
  OFFの時間がこのONの何倍かで0,1が表現される。  
  この0,1からなる2進数文字列を解析し、それを16進数に変換したものがjsonに記載されている。また外れ値  
  (信号には最初のリーダー部やリピート指示など、ONとOFFの時間が単位周期の数倍以上になる部分がある)  
  は単純に16進数表記などでは表せないので単位周期の何倍かを表すために配列(ON,OFFそれぞれ)として別の形で表記した。  
  以下のjsonは先程取得したエアコンのリモコンの信号データを変換し取得したjsonデータ。  
  これを見るとこのリモコンは同じ信号を2回送信しているのがわかる。  
  ``` {"base_time": 435, "signal": [[8, 4], "c4d3648000041a506c920000000020000058", [1, 30], [8, 4], "c4d3648000041a506c920000000020000058", [1, 1]]} ```
1. APIサーバを建てる  
  ```python api_server.py```
1. APIサーバに先程のjsonをpostする  
  http://<raspi ip address>:5000/infrared_code/  
  ここにPOSTする  






