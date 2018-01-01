### A Small program for Wechat Jump game

1. Running with android rooted device
2. Grab the screenshot
3. Find the source point with cv2.matchTemplate
4. Find the target point with color diff:
    - discard the pixels in the range of source_x +/- 25. (not quite reliable)
    - the top pixel of target: the first one neither the bg color
    - the right corner pixel of target: the max X value of target pixel
5. Calculate the distance and revert it into pressing timing.
6. Sending pressing event via adb
