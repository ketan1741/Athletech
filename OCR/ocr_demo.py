import cv2 
import time 
import easyocr
import numpy as np
import pytesseract
import matplotlib.pyplot as plt

# ------------ 2560 x 1440 ------------ # 
# height of kill info: 43 pixels
# height of weapon info: 106-113 pixels
# ------------ 2560 x 1440 ------------ # 

sta = time.time()
# Open an image file
height, width = 1440, 2560
image = cv2.imread('image4.png')
image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

imagec = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
# Note the y coordinate comes first in numpy array

# ------------------------------------------------------- 0.06sec -------------------------------------------------------
# weapon
part1_weap1 = image[int(906*height/1440):int(925*height/1440),   int(2100*width/2560):int(2530*width/2560)]   # top
part1_weap2 = image[int(1012*height/1440):int(1042*height/1440), int(2100*width/2560):int(2530*width/2560)]
part1_weap3 = image[int(1118*height/1440):int(1148*height/1440), int(2100*width/2560):int(2530*width/2560)]
part1_weap4 = image[int(1224*height/1440):int(1254*height/1440), int(2100*width/2560):int(2530*width/2560)]
part1_weap5 = image[int(1341*height/1440):int(1360*height/1440), int(2100*width/2560):int(2530*width/2560)]   # bottom
part1_concate = np.concatenate((part1_weap1, part1_weap2, part1_weap3, part1_weap4, part1_weap5), axis = 0)   # vertical
# HP and AC
part2_hp = image[int(1380*height/1440):int(1428*height/1440),  int(78*width/2560):int(153*width/2560)] 
part2_ac = image[int(1380*height/1440):int(1428*height/1440), int(354*width/2560):int(429*width/2560)]  
part2_concate = np.concatenate((part2_hp, part2_ac), axis = 0)
# money, magazine and kill
part3_money = image[int(470*height/1440):int(530*height/1440), int(60*width/2560):int(190*width/2560)]  
part4_magaz = image[int(1382*height/1440):int(1420*height/1440), int(2280*width/2560):int(2445*width/2560)]   

part5_kill1 = imagec[int(100*height/1440):int(143*height/1440),  int(2000*width/2560):int(2550*width/2560)]   
part5_kill2 = imagec[int(147*height/1440):int(190*height/1440),  int(2000*width/2560):int(2550*width/2560)]  
part5_kill3 = imagec[int(194*height/1440):int(237*height/1440),  int(2000*width/2560):int(2550*width/2560)]  
part5_kill4 = imagec[int(241*height/1440):int(284*height/1440),  int(2000*width/2560):int(2550*width/2560)]
part5_kill5 = imagec[int(288*height/1440):int(331*height/1440),  int(2000*width/2560):int(2550*width/2560)]    
part5_concate = np.concatenate((part5_kill1, part5_kill2, part5_kill3, part5_kill4, part5_kill5), axis = 0)   # vertical

# ------------------------------------------------------- 0.06sec -------------------------------------------------------
text1 = pytesseract.image_to_string(part1_concate, config='--oem 1 --dpi 300 --psm 1')
text2 = pytesseract.image_to_string(part2_concate, config='--oem 1 --dpi 300 --psm 6')
text31 = pytesseract.image_to_string(part3_money, config='--oem 1 --dpi 300 --psm 13')
text41 = pytesseract.image_to_string(part4_magaz, config='--oem 1 --dpi 300 --psm 13')
text5 = pytesseract.image_to_string(part5_concate, config='--oem 1 --dpi 300 --psm 6')
print(text1)
print(text2)
print(text31)
print(text41)
print(text5)
end = time.time()
print(end-sta)


sta = time.time()
reader = easyocr.Reader(['en'])
result1 = reader.readtext(part1_concate)
result2 = reader.readtext(part2_concate)
result3 = reader.readtext(part3_money)
result4 = reader.readtext(part4_magaz)
result5 = reader.readtext(part5_concate)
end = time.time()

for res in result1:
    print(res[1])
for res in result2:
    print(res[1])
for res in result3:
    print(res[1])
for res in result4:
    print(res[1])
for res in result5:
    print(res[1])

print(end-sta)
cv2.imwrite('result/demo11.png', part1_concate)
cv2.imwrite('result/demo21.png', part2_concate)
cv2.imwrite('result/demo31.png', part3_money)
cv2.imwrite('result/demo41.png', part4_magaz)
cv2.imwrite('result/demo51.png', part5_concate)


# Define the target colors and threshold
# blue_rgb = np.array([156, 178, 238])
# yellow_rgb = np.array([247, 200, 97])
# threshold = 35

# # Calculate the distance from each pixel to the target colors
# dist_blue = np.linalg.norm(part5 - blue_rgb, axis=-1)
# dist_yellow = np.linalg.norm(part5 - yellow_rgb, axis=-1)

# # Generate the masks
# mask_blue = dist_blue < threshold
# mask_yellow = dist_yellow < threshold
# mask_combined = np.logical_or(mask_blue, mask_yellow)

# # Apply the masks
# part5 = (mask_combined * 255).astype(np.uint8)

# cv2.imwrite('output1.png', part1)
# cv2.imwrite('output2.png', part2)
# cv2.imwrite('output3.png', part3)
# cv2.imwrite('output4.png', part4)
# cv2.imwrite('output5.png', part5)

# # Use pytesseract to convert the image into text
# text1 = pytesseract.image_to_string(part1, config='--oem 1 --dpi 300 --psm 13')
# text2 = pytesseract.image_to_string(part2, config='--oem 1 --dpi 300 --psm 13')
# text3 = pytesseract.image_to_string(part3, config='--oem 1 --dpi 300 --psm 6')
# text4 = pytesseract.image_to_string(part4, config='--oem 1 --dpi 900 --psm 6')
# text5 = pytesseract.image_to_string(part5, config='--oem 1 --dpi 900 --psm 6')
# end = time.time()

# # Print the text
# print("----------------life-----------------")
# print(text1)
# print("---------------armor-----------------")
# print(text2)
# print("-------------magazine----------------")
# print(text3)
# print("--------------weapon-----------------")
# print(text4)
# print("---------------kill------------------")
# print(text5)
# print("-------------------------------------")
# print(end-sta)

# import os
# import time
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="csgoocr-c89400e0c174.json"

# from google.cloud import vision

# def detect_text(path):
#     """Detects text in the file."""
#     client = vision.ImageAnnotatorClient()

#     with open(path, 'rb') as image_file:
#         content = image_file.read()

#     image = vision.Image(content=content)

#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     print('Texts:')
#     for text in texts:
#         print('\n"{}"'.format(text.description))

#     if response.error.message:
#         raise Exception(
#             '{}\nFor more info on error messages, check: '
#             'https://cloud.google.com/apis/design/errors'.format(
#                 response.error.message))

# sta = time.time()
# detect_text("image.png")
# end = time.time()
# print(end-sta)