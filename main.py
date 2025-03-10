# This is a sample Python script.
import cv2
import numpy as np

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


cam = cv2.VideoCapture('lane Detection Test Video-01.mp4')
left_top_x = 0
right_top_x = 0
left_bottom_x = 0
right_bottom_x = 0
while True:
    ret, frame = cam.read()
    if ret is False:
        break
    width = 400
    height = 200
    frame = cv2.resize(frame, (width, height))
    cv2.imshow('Original', frame)

    gri50nuante = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Grayscale', gri50nuante)
    sus_st = (int(width * 0.55), int(height * 0.75))
    sus_dr = (int(width * 0.45), int(height * 0.75))
    jos_st = (0, height)
    jos_dr = (width, height)
    trapez = np.array([sus_st, sus_dr, jos_st, jos_dr], dtype=np.int32)
    blankframe = np.zeros((height, width), dtype=np.uint8)
    cv2.fillConvexPoly(blankframe, trapez, 1)
    cv2.imshow('Trapez', blankframe * 255)
    stradaGriTrapez = blankframe * gri50nuante
    cv2.imshow('Cut Road', stradaGriTrapez)

    trapezoid_bounds = np.float32([sus_st, sus_dr, jos_st, jos_dr])
    screen_bounds = np.float32([(width, 0), (0, 0), (0, height), (width, height)])
    magic_matrix = cv2.getPerspectiveTransform(trapezoid_bounds, screen_bounds)
    wrapStrada = cv2.warpPerspective(stradaGriTrapez, magic_matrix, (width, height))
    cv2.imshow('Wrapped Road', wrapStrada)

    blurStrada = cv2.blur(wrapStrada, ksize=(5, 5))
    cv2.imshow('Blurred Road', blurStrada)

    sobel_vert = np.float32([[-1, -2, -1],
                             [0, 0, 0],
                             [+1, +2, +1]])
    sobel_horiz = np.transpose(sobel_vert)
    filter_horiz = cv2.filter2D(np.float32(blurStrada), -1, sobel_horiz)
    filter_vert = cv2.filter2D(np.float32(blurStrada), -1, sobel_vert)
    # cv2.imshow('Sobel horiz', cv2.convertScaleAbs(filter_horiz))
    # cv2.imshow('Sobel vert', cv2.convertScaleAbs(filter_vert))

    filter_final = np.sqrt((filter_vert ** 2 + filter_horiz ** 2))
    cv2.imshow('Sobel filter', cv2.convertScaleAbs(filter_final))

    thresh = int(255 / 2 - 50)
    (T, binariz) = cv2.threshold(cv2.convertScaleAbs(filter_final), thresh, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binarizare', binariz)

    noiseRed = binariz.copy()
    noiseRed[0:int(height * 0.05), :] = 0
    noiseRed[int(height * 0.95):height, :] = 0

    noiseRed[:, 0:int(width * 0.05)] = 0
    noiseRed[:, int(width * 0.95): width] = 0
    cv2.imshow('Noise reduction', noiseRed)

    left_pct = []
    right_pct = []
    left_xs = []
    left_ys = []
    right_xs = []
    right_ys = []
    pctAlbe = np.argwhere(noiseRed > 0)
    for i in pctAlbe:
        if i[1] < width / 2:
            left_pct.append(i)
        if i[1] > width / 2:
            right_pct.append(i)
    for i in left_pct:
        left_ys.append(i[0])
        left_xs.append(i[1])
    for i in right_pct:
        right_ys.append(i[0])
        right_xs.append(i[1])

    (b_r, a_r) = np.polynomial.polynomial.polyfit(right_xs, right_ys, deg=1)
    (b_l, a_l) = np.polynomial.polynomial.polyfit(left_xs, left_ys, deg=1)
    left_top_y = 0
    tmp = (left_top_y - b_l) // a_l
    if (tmp >= -10 ** 8) & (tmp <= 10 ** 8):
        left_top_x = tmp
    left_bottom_y = height
    tmp = (left_bottom_y - b_l) // a_l
    if (tmp >= -10 ** 8) & (tmp <= 10 ** 8):
        left_bottom_x = tmp
    right_top_y = 0
    tmp = (right_top_y - b_r) // a_r
    if (tmp >= -10 ** 8) & (tmp <= 10 ** 8):
        right_top_x = tmp
    right_bottom_y = height
    tmp = (right_bottom_y - b_r) // a_r
    if (tmp >= -10 ** 8) & (tmp <= 10 ** 8):
        right_bottom_x = tmp

    left_top = int(left_top_x), int(left_top_y)
    right_top = int(right_top_x), int(right_top_y)
    left_bottom = int(left_bottom_x), int(left_bottom_y)
    right_bottom = int(right_top_x), int(right_bottom_y)
    cv2.line(noiseRed, left_top, left_bottom, (200, 0, 0), 5)
    cv2.imshow('linii', noiseRed)
    cv2.line(noiseRed, right_top, right_bottom, (220, 0, 0), 5)
    cv2.imshow('linii', noiseRed)

    blankframelinieleft = np.zeros((height, width), dtype=np.uint8)
    magic_matrix2 = cv2.getPerspectiveTransform(screen_bounds, trapezoid_bounds)
    cv2.line(blankframelinieleft, left_top, left_bottom, (255, 0, 0), 3)
    wrapStrada2left = cv2.warpPerspective(blankframelinieleft, magic_matrix2, (width, height))
    cv2.imshow('linie jos stanga', wrapStrada2left)

    blankframelinieright = np.zeros((height, width), dtype=np.uint8)
    magic_matrix2 = cv2.getPerspectiveTransform(screen_bounds, trapezoid_bounds)
    cv2.line(blankframelinieright, right_top, right_bottom, (50, 0, 0), 3)
    wrapStrada2right = cv2.warpPerspective(blankframelinieright, magic_matrix2, (width, height))
    cv2.imshow('linie jos dreapta', wrapStrada2right)

    pctAlbeFinalR = np.argwhere(wrapStrada2right > 0)
    pctAlbeFinalL = np.argwhere(wrapStrada2left > 0)

    liniicolor = frame.copy()
    for cord in pctAlbeFinalL:
        liniicolor[cord[0], cord[1]] = (250, 50, 250)
    for cord in pctAlbeFinalR:
        liniicolor[cord[0], cord[1]] = (50, 50, 250)
    cv2.imshow('linie color', liniicolor)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
