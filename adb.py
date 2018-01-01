import os

def adb_command(command):
    os.system("adb "+command)

def adb_press_play(time_ms):
    os.system("adb shell input swipe 100 100 100 100 %d" % time_ms)