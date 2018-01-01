### A Small program for Wechat Jump game

1. Running with android rooted device
2. Grab the screenshot
3. Find the source point with cv2.matchTemplate
4. Find the target point with color diff:
    - discard the pixels in the range of source_x +/- 25. (not quite reliable)
    - the top pixel of target: the first one neither the bg color
    - the left corner pixel of target: the minimun X value of target pixel. 
        - This would cause it's not the actual center of an ellipse, but it's still inside of the object.
        - the shadow is affecting this also, not resolved it yet.
5. Calculate the distance and revert it into pressing timing.
6. Sending pressing event via adb
