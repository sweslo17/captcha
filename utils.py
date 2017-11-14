# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import PIL
from PIL import ImageEnhance
import numpy as np


def pil_img_to_opencv(pil_image):
    open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return open_cv_image

def preprocess_bw(image):
    blurred = cv2.GaussianBlur(image, (5, 5), 1.3)
    edged = cv2.Canny(blurred, 10, 200)
    return edged

def clean_bg(pil_image):
    im = pil_image.convert('RGB')
    data = np.array(im)
    # just use the rgb values for comparison
    rgb = data[:,:,:]
    #color = data[5][5]   # Original value
    color = np.median(data[5,:],axis=0)
    black = [0,0,0]
    white = [255,255,255]
    mask = np.all((rgb > color-114), axis = -1)
    # change all pixels that match color to white
    data[mask] = white

    # change all pixels that don't match color to black
    ##data[np.logical_not(mask)] = black
    clear_bg = PIL.Image.fromarray(data)
    return clear_bg

def tune_brightness(pil_image):
    enhancer = ImageEnhance.Brightness(pil_image)
    factor = 115/100
    result = enhancer.enhance(factor)
    return result

def get_contours(image):
    digitCnts = []
    (img, cnts, heiarachy) = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    (cnts, boundingBoxes) = contours.sort_contours(cnts, method="left-to-right")
    height, width = image.shape
    min_x, min_y = width, height
    max_x = max_y = 0
    # loop over the digit area candidates
    for (cnt), (x, y, w, h) in zip(cnts,boundingBoxes):
        min_x, max_x = min(x, min_x), max(x+w, max_x)
        min_y, max_y = min(y, min_y), max(y+h, max_y)
        if w >= 10 and h >= 10:
            digitCnts.append((x,y,x+w,y+h))
    return digitCnts

def preprocess_color(pil_image):
    pil_image = clean_bg(pil_image)
    pil_image = tune_brightness(pil_image)
    cv_image = pil_img_to_opencv(pil_image)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.3)
    edged = cv2.Canny(blurred, 10, 200)
    return edged

def draw_contours(image, counter_boxes):
    output_image = image.copy()
    for box in counter_boxes:
        cv2.rectangle(output_image, (box[0],box[1]), (box[2],box[3]), (255, 0, 0), 1)
    return output_image

def gen_processed_box_img(path, img_name):
    '''
    label前中繼資料(processing)：
    box filename: 原始圖片name_box.jpg
    box preprocess: 原始圖片name_preprocess_box.jpg
    crop filename: 原始圖片name_N_X1_X2_Y1_Y2.jpg
    '''
    pil_image = PIL.Image.open(path)
    cv_image = pil_img_to_opencv(pil_image)
    preprocessed_image = preprocess_color(pil_image)
    contours = get_contours(preprocessed_image)
    # 1. boxed origin
    cv2.imwrite('preprocessed_data/{}_box.png'.format(img_name), draw_contours(cv_image, contours))
    # 2. boxed preprecessed
    cv2.imwrite('preprocessed_data/{}_preprocess_box.png'.format(img_name), draw_contours(preprocessed_image, contours))
    # 3. corped
    for idx, cnt in enumerate(contours):
        cv2.imwrite('preprocessed_data/{}_corped_{}_{}_{}_{}_{}.png'.format(img_name, idx, cnt[0], cnt[1], cnt[2], cnt[3]), 
                cv_image[cnt[1]:cnt[3], cnt[0]:cnt[2]])