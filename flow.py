import matplotlib.pyplot as plt
import numpy as np
import math
import requests
from bs4 import BeautifulSoup 

def get_vector(ov_x, ov_y):
    vx = np.zeros(X.shape) #0.4刻みにすると16×16のマップが出来上がったため。
    vy = np.zeros(Y.shape) #np.zaros((x,y)) :x*yの空の二次元配列   
    for i in range(0,16):
        for j in range(0,16):
            for k in range(number_of_sensors): #観測点の個数分繰り返す
                dis = math.sqrt((ovp_x[k] - X[i,j])**2 + (ovp_y[k] - Y[i,j])**2) #観測点からの距離
                if dis == 0:
                    dis = 1;
                vx[i,j] += ov_x[k] / dis #xのベクトル成分
                vy[i,j] += ov_y[k] / dis
    return vx, vy


def draw_map(vx, vy, ov_x, ov_y):
    """
    quiver matplotlibチュートリアル参照
    quiver : ベクトル場の可視化
    """
    ax.cla()
    #観測点だけ色を変える
    ax.quiver(ovp_x,ovp_y,ov_x,ov_y, color='red', angles='xy', scale_units='xy', scale=2)#units='height') #観測点の矢印
    Q = ax.quiver(X,Y,vx,vy, color='blue',angles='xy', scale_units='xy', scale=2) #観測点以外の矢印
    #quiverkey : quiverの矢印の長さ、向きに対応するラベルを指定する関数
    #qk = ax.quiverkey(Q, 0.9, 0.9, 2, r'$2 \frac{m}{s}$', labelpos='N', coordinates='figure')

def get_flow_sensor(angle_offset):
    global stock_data
    for i in range(4):
        try:
            # ページを取得
            r = requests.get(url)
            r.raise_for_status()  # HTTPエラーチェック
            # BeautifulSoupを使用して解析
            soup = BeautifulSoup(r.content, 'html.parser')
            # 抽出したい情報が含まれている<p>要素を取得
            all_p_elements = soup.find_all('p')
            # 直近の<p>要素を取得
            if all_p_elements:
                latest_p_element = all_p_elements[-1]
                getting_text = latest_p_element.get_text(',').encode('utf-8').decode('utf-8')
                now_data = np.array(getting_text.split(',')).reshape(-1,6)
                now_data = now_data[-1].astype(float)
                stock_data = np.append(stock_data, now_data).reshape(-1,6)
                break
            else:
                print("ページには<p>要素が存在しません。")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    x = np.zeros(number_of_sensors)
    y = np.zeros(number_of_sensors) 
    for l in range(number_of_sensors):
        data = stock_data[stock_data[:,1] == l]
        if data.size == 0:
            data = stock_data[stock_data[:,1] == 1.0]
        if data.size == 0:
            data = stock_data[-1]
        else:
            data = data[-1]

        angle = np.arctan2(float(data[3]), float(data[2])) + np.deg2rad(angle_offset*-1.0)
        print('(id:%d,%d) magx= %f  magy=%f angle=%f rad %f degree'%(l, int(data[1]), float(data[2]), float(data[3]), angle, np.rad2deg(angle)))
        x[l] = np.cos(angle) * (float(data[4])+0.1) 
        y[l] = np.sin(angle) * (float(data[4])+0.1) 

    return x, y

def ov_rip_current(vx, vy):
    thred_rip1 = 0.3
    thred_rip2 = 0.1
    angle = np.arctan2(vy, vx)
    detected_rip = np.sum(angle > 0.5*np.pi*thred_rip1)/angle.size
    return detected_rip > thred_rip2

url = "http://192.168.1.124/env"
stock_data = np.array([]) 
fig, ax = plt.subplots()
#Y,Xの二つの二次元格子配列を宣言する
#Y, X = np.meshgrid(np.arange(0,2*np.pi,0.4),np.arange(0,2*np.pi,0.4))
Y, X = np.meshgrid(np.arange(16),np.arange(16))
#観測点
ovp_x = [X[0,0],X[14,14],X[7,7],X[4,11],X[12,1]]
ovp_y = [Y[0,0],Y[14,14],Y[7,7],Y[4,11],Y[12,1]]
#配列の要素数
number_of_sensors = len(ovp_x) #len(配列)で配列の要素数を取得できる

angle_offset = -40 #デモ環境が真の北方向と何度ずれているか

for i in range(100):
    print(str(i)+'回目描画中')
    ovp_x_data, ovp_y_data = get_flow_sensor(angle_offset)
    vx, vy = get_vector(ovp_x_data, ovp_y_data)
    draw_map(vx, vy, ovp_x_data, ovp_y_data)
    ax.set_title('Arrows scale with plot width, not view ('+str(i)+')')
    for i, (x, y) in enumerate(zip(ovp_x, ovp_y)):
        ax.text(x, y, i+1, fontsize='xx-large', backgroundcolor='lightblue')
 
    if ov_rip_current(vx, vy):
        for _ in range(2):
            ax.text(0.3, -0.08, 'Alert rip cuurrnt!', transform=ax.transAxes, backgroundcolor = 'red', fontsize='xx-large', fontweight='bold')
            plt.pause(.1)
            ax.text(0.3, -0.08, 'Alert rip cuurrnt!', transform=ax.transAxes, backgroundcolor = 'blue', fontsize='xx-large', fontweight='bold')
            plt.pause(0.1)

    plt.pause(0.5)
