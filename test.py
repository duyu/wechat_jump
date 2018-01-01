#!/usr/bin/env python
#coding: utf-8

import os
import cv2
import numpy
from adb import adb_command, adb_press_play

SCREENSHOT_IMAGE = "screenshot.png"
jump_factor = 2.1
IMAGE_DIFF = 15
DEBUG = False

def dist((x1,y1),(x2,y2)):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def is_pixel_similar(pixel1, pixel2):
    global IMAGE_DIFF
    pixel_dif = pixel1.astype(int) - pixel2.astype(int)
    return abs(pixel_dif[0]) < IMAGE_DIFF and abs(pixel_dif[1]) < IMAGE_DIFF and abs(pixel_dif[2]) < IMAGE_DIFF
    
def move(source_pt, target_pt):
    distance = dist(source_pt, target_pt)
    time_ms = int(distance * jump_factor)
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
    
    for i in xrange(5000):
        if not DEBUG:
            adb_command('shell screencap /sdcard/screen.png')
            adb_command("pull /sdcard/screen.png " + SCREENSHOT_IMAGE)
        else:
            SCREENSHOT_IMAGE = "last_screen.png"
        print "start loop %d" % i
        
        # Find the object in image and calculate the object bottom center
        img_rgb = cv2.imread(SCREENSHOT_IMAGE)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_w, img_h = img_gray.shape[::-1]
        print img_w, img_h
        template = cv2.imread('template.png',0)
        template_w, template_h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = numpy.where( res >= threshold)
        source_pt = (loc[1][0]+template_w/2, loc[0][0]+template_h - 10)
        print source_pt

        # Find the target point
        # scan start from the score area and ended with the source area, step 50px
        target_top_start = None
        target_top_end = None
        target_top_center = None
        target_right = None
        found_right = False
        target_pixel = None
        
        # find the top line pixels firstly
        for scan_y in range(250, source_pt[1]):
            bg_pixel = img_rgb[scan_y, 100]
            for scan_x in range(100, img_w):
                pixel = img_rgb[scan_y,scan_x]
                # check if it's the source object
                if abs(scan_x - source_pt[0]) < 25:
                    # print "found source pixel: ", source_pixel, pixel, (scan_x, scan_y)
                    continue
                # get the pixel of target object and set the top
                if target_top_start is None:
                    # if it's not similar to background, we found the top start pixel of target
                    if not is_pixel_similar(pixel, bg_pixel):
                        target_top_start = (scan_x , scan_y)
                        target_top_end = (scan_x , scan_y)
                        target_pixel = img_rgb[scan_y,scan_x]
                        print "Fount target top pixel: ", pixel, target_top_start
                        continue
                # if it's the same line as the top line
                elif scan_y == target_top_start[1]:
                    # try finding the target top last pixel
                    if not is_pixel_similar(pixel, bg_pixel):
                        target_top_end = (scan_x, scan_y)
                    else:
                        target_top_center = (int((target_top_start[0] + target_top_end[0])/2), scan_y)
                        break
                else:
                    # should never come here
                    print "What's wrong?"
            if target_top_center:
                break
        print "Found Target Top Center: ", target_top_center
        # find the rightest pixel of target object
        target_right = target_top_end
        current_x = target_top_end[0]
        current_y = target_top_end[1]
        while True:
            # under right of last target_right
            bg_pixel = img_rgb[current_y + 1, 100]
            under_right_pixel = img_rgb[current_y + 1, current_x + 1]
            # print "Check under: ", (current_x+1, current_y+1), (under_right_pixel, bg_pixel)
            if not is_pixel_similar(under_right_pixel, bg_pixel):
                # if the under right pixel is not similar as bg pixel, find the last one of under line
                current_x += 1
                current_y += 1
                # print "Check line %d - %d" %(current_y, current_x), under_right_pixel, bg_pixel

                for scan_x in range(current_x + 1, img_w):
                    pixel = img_rgb[current_y, scan_x]
                    if is_pixel_similar(pixel, bg_pixel):
                        # found the last one in the under line, go check next line
                        current_x = scan_x - 1
                        # print "found the rightest of this line", current_x, current_y
                        break
                    else:
                        continue
            else:
                # if the under pixel is similar as bg pixel, it means the current one is the rightest
                print "Found the Rightest: ", under_right_pixel, target_right
                target_right = (current_x, current_y)    
                break

        if target_right:
            print("found target top and target right", target_top_center, target_right)
            target_pt = (target_top_center[0], target_right[1])
        else:
            print("Target not found...")
            break

        cv2.line(img_rgb,source_pt, target_pt,(0,0,255), thickness=5)
        
        # cv2.imshow("image", img_rgb)

        if not DEBUG:
            cv2.imwrite("last_operate.png", img_rgb)
            os.system("cp screenshot.png last_screen.png")
            move(source_pt, target_pt)
        
            if cv2.waitKey(3000) & 0xFF == 27:
                break
        else:
            if cv2.waitKey(0) & 0xFF == 27:
                break
    
    cv2.destroyAllWindows()
