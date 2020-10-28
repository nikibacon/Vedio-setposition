import cv2
import numpy as np
import os
from twilio.rest import Client
import os.path as osp
import sys
import requests, os
import time
import multiprocessing as mp
from vedio_setpos.settings import ACCOUNT_SID, AUTH_TOKEN, TOKEN

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# cap = cv2.VideoCapture(0)

# print(cap.isOpened())
# cap.open(0)

# while True:
#     ret, frame = cap.read()

#     cv2.imshow('frame', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break


# cap.release()

# cv2.destroyAllWindows()
def read_file(filename):
    points = []  # 不管檔案存不存在都需要清單
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if '(x1, y1),(x2, y2)' in line:
                continue
            point = line.strip().split(',')
            points.append(point)

    return points


def lineNotify(token, msg, picURI):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + TOKEN
    }

    payload = {'message': msg}
    files = {'imageFile': open(picURI, 'rb')}
    r = requests.post(url, headers=headers, params=payload, files=files)
    return r.status_code


outputFolder = "my_output"

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

ip_cam_url = 'rtsp://admin:admin@192.168.0.221/'
# http://192.168.0.221:80?user=admin&pwd=admin&action=stream
# http://admin:admin@192.168.0.221/

# rtsp://admin:admin@192.168.0.221/
cam = cv2.VideoCapture(ip_cam_url)

frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 16.0, (frame_width, frame_height))

width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("Image Size: %d x %d" % (width, height))

print(cam.isOpened())

# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

cam.set(3, 640)
cam.set(4, 480)


# while True:
#     stat, frame = cam.read()


#     cv2.imshow('getCam', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cam.release()
#         cv2.destroyAllWindows()
#         break


# width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
# height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
# print("Image Size: %d x %d" % (width, height))

def move(x1, y1, x2, y2):
    area = width * height

    stat, frame = cam.read()
    frame = frame[y1: y2, x1: x2]
    avg = cv2.blur(frame, (4, 4))
    avg_float = np.float32(avg)

    # 輸出圖檔用的計數器
    outputCounter = 0
    count = 0

    while (cam.isOpened()):
        stat, frame = cam.read()
        frame = frame[y1: y2, x1: x2]

        if stat == False:
            break

        blur = cv2.blur(frame, (4, 4))

        # 計算目前影格與平均影像的差異值
        diff = cv2.absdiff(avg, blur)

        # 將圖片轉為灰階
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 篩選出變動程度大於門檻值的區域
        stat, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)

        # 使用型態轉換函數去除雜訊
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 產生等高線
        cnts, cntImg = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hasMotion = False
        for c in cnts:
            # 忽略太小的區域
            if cv2.contourArea(c) < 2500:
                continue

            # 偵測到物體，可以自己加上處理的程式碼在這裡...
            hasMotion = True
            # 計算等高線的外框範圍
            (x, y, w, h) = cv2.boundingRect(c)

            # 畫出外框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if not hasMotion:
            count = 0
            # print(count)

        if hasMotion:
            # 儲存有變動的影像

            count += 1
            # print(count)
            if count == 20:
                cv2.imwrite("%s/output_%04d.jpg" % (outputFolder, outputCounter), frame)

                msg = "Moving!"
                picURI = "%s/output_%04d.jpg" % (outputFolder, outputCounter)
                outputCounter += 1

                lineNotify(TOKEN, msg, picURI)

                # message = client.messages.create(
                # body='你在動!!',
                # from_='+12014743791',
                # to=PHONE_NUM
                # )
                # print(message.sid)

                count += 1

                if count > 20:
                    continue

            # fourcc = cv2.VideoWriter_fourcc(*'XVID')

        # 畫出等高線（除錯用）
        cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)

        out.write(frame)

        # 顯示偵測結果影像
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 更新平均影像
        cv2.accumulateWeighted(blur, avg_float, 0.01)
        avg = cv2.convertScaleAbs(avg_float)

    cam.release()
    out.release()
    cv2.destroyAllWindows()


def main(x1, y1, x2, y2):
    print('開始執行', x1, y1, x2, y2)
    move(x1, y1, x2, y2)
    time.sleep(5)
    print('結束')


if __name__ == '__main__':

    filename = 'points.txt'
    points = read_file(filename)

    # move(1525,73,1837,367)
    # move(76,236,667,558)

    # for count, point in enumerate(points):
    #     x1 = int(points[count][0])
    #     y1 = int(points[count][1])
    #     x2 = int(points[count][2])
    #     y2 = int(points[count][3])
    #     print(x1,y1,x2,y2)
    #     move(x1,y1,x2,y2)

    threads = []
    for count, point in enumerate(points):
        x1 = int(points[count][0])
        y1 = int(points[count][1])
        x2 = int(points[count][2])
        y2 = int(points[count][3])
        print(count)
        print(x1, y1, x2, y2)

        threads.append(mp.Process(target=main, args=(x1, y1, x2, y2)))

        threads[count].start()
        time.sleep(3)

    for count, point in enumerate(points):
        threads[count].join()
        print('\nthread' + str(count) + 'finish')

    print('complete')
