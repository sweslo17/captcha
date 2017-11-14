import utils
img_num = 1

for img_num in range (1,101):
    utils.gen_processed_box_img("test_data/{}.jpg".format(img_num), str(img_num))