#!/usr/bin/env python
#coding: utf-8

import os.path as op
import cv2
import numpy
from adb import adb_command, adb_press_play

SCREENSHOT_IMAGE = op.join(op.dirname(__file__), 'screenshot.png') 

def dist((x1,y1),(x2,y2)):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def color_dif(pixel1, pixel2):
    pixel_dif = pixel1.astype(int) - pixel2.astype(int)
    return abs(pixel_dif[0]) + abs(pixel_dif[1]) + abs(pixel_dif[2])
    
def move(source_pt, target_pt):
    distance = dist(source_pt, target_pt)
    time_ms = int(distance * 2.1)
    print source_pt, "->", target_pt
    print "Distance: %d, Time: %d" % (distance, time_ms)
    adb_press_play(time_ms)

if __name__ == '__main__':
    adb_command("wait-for-device")
    adb_command("root")
    adb_command("wait-for-device")
    adb_command("remount")
    adb_command("wait-for-device")

    cv2.namedWindow('image')
    
    for i in xrange(150):
        adb_command('shell screencap /sdcard/screen.png')
        adb_command("pull /sdcard/screen.png " + SCREENSHOT_IMAGE)
        print "start loop %d" % i
        
        # Find the object in image and calculate the object bottom center
        img_rgb = cv2.imread(SCREENSHOT_IMAGE)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_w, img_h = img_gray.shape[::-1]
        template = cv2.imread('template.png',0)
        template_w, template_h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = numpy.where( res >= threshold)
        source_pt = (loc[1][0]+template_w/2, loc[0][0]+template_h - 10)
        print source_pt

        # Find the target point
        # scan start from the score area and ended with the source area, step 50px
        target_top = None
        target_left = None
        found_left = False
        target_pixel = None
        source_pixel = img_rgb[source_pt[1], source_pt[0]]
        for scan_y in range(250, source_pt[1]):
            bg_pixel = img_rgb[scan_y, 100]
            for scan_x in range(100, img_w - 100):
                pixel = img_rgb[scan_y,scan_x]
                # check if it's the source object
                if color_dif(pixel, source_pixel) < 10:
                    continue
                # get the pixel of target object and set the top
                if target_pixel is None:
                    if color_dif(pixel, bg_pixel) > 10:
                        print bg_pixel, pixel
                        target_top = (scan_x, scan_y)
                        target_left = (scan_x, scan_y)
                        target_pixel = pixel
                        break
                else:
                    # found the first pixel of target object
                    if color_dif(pixel, target_pixel) < 10:
                        if scan_x < target_left[0]:
                            target_left = (scan_x, scan_y)
                        else:
                            found_left = True
                        break
                if found_left:
                    break
            
        print("found target left and target top", target_left, target_top)
        target_pt = (target_top[0], target_left[1])

        cv2.line(img_rgb,source_pt, target_pt,(0,0,255), thickness=5)
        
        cv2.imshow("image", img_rgb)
        move(source_pt, target_pt)
        
        if cv2.waitKey(6000) & 0xFF == 27:
            break
    cv2.destroyAllWindows()
