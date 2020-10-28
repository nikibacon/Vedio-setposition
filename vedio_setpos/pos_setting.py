import cv2
import numpy as np
import os
import os.path as osp
import sys
import requests, os


def write_file(filename, points_write):
    # 寫入檔案
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('(x1, y1),(x2, y2)\n')

        # for p in points_write:
        # f.write('(' + str(p[0]) + ',' + str(p[1]) + ')\n')

        for count, p in enumerate(points_write, start=1):
            # print(count, p)

            if count % 2 == 1:
                f.write(str(p[0]) + ',' + str(p[1]) + ',')

            if count % 2 == 0:
                f.write(str(p[0]) + ',' + str(p[1]) + '\n')


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, ',', y)

        font = cv2.FONT_HERSHEY_SIMPLEX
        strXY = '(' + str(x) + ',' + str(y) + ')'
        y1 = y - 10  # move text up
        cv2.putText(img, strXY, (x, y1), font, 1, (0, 165, 255), 2)

        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)

        points.append((x, y))
        points_write.append((x, y))

        if len(points) >= 2:
            cv2.rectangle(img, points[-2], points[-1], (0, 255, 0), 2)
            print(points)
            print(points_write)
            print(type(points_write))

            points.clear()
        cv2.imshow('image', img)
        write_file(filename, points_write)
    return


filename = 'points.txt'

ip_cam_url = 'rtsp://admin:admin@192.168.0.221/'
cam = cv2.VideoCapture(ip_cam_url)
# cam = cv2.VideoCapture(0)


stat, img = cam.read()
# img = np.zeros((512, 512, 3), np.uint8)
cv2.imshow('image', img)

points = []
points_write = []

cv2.setMouseCallback('image', click_event)

cv2.waitKey(0)
cam.release()
cv2.destroyAllWindows()


