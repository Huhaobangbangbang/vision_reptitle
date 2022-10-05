"""
 -*- coding: utf-8 -*-
 author： Hao Hu
 @date   2022/9/26 5:37 PM
"""
import os
import easyocr
from tqdm import tqdm
# 创建reader对象
import json
from itertools import product
from turtle import color
from PIL import Image
import pytesseract

CUDA_VISIBLE_DEVICES = 3


def get_img_path_list(folder_path):
    img_list = os.listdir(folder_path)
    img_path_list = []
    for img in img_list:
        img_path = os.path.join(folder_path, img)
        img_path_list.append(img_path)
    return img_path_list


def get_product_information(img_path):
    first_box = (605, 150, 940, 1861)
    fist_area = Image.open(img_path).crop(first_box)
    recognize_content = pytesseract.image_to_string(fist_area)
    product_title = recognize_content.split("Visit")[0]
    rating_num = recognize_content.split("ratings")[0].split()[-1]
    brand, product_color, style, material, price = '', '', '', '', ''
    try:
        brand = recognize_content.split("Brand")[1].split()[0]

    except:
        pass
    try:
        if recognize_content.split("Material")[1].split("Color")[1].split()[1] == 'Brand':
            product_color = recognize_content.split("Material")[1].split("Color")[1].split()[0]
        else:
            product_color = recognize_content.split("Material")[1].split("Color")[1].split()[0] + ' ' + \
                            recognize_content.split("Material")[1].split("Color")[1].split()[1]

    except:
        pass
    try:
        style = recognize_content.split("style")[1].split()[0]
    except:
        pass

    try:
        material = recognize_content.split("Material")[1].split()[0]
        if material == '~':
            material = recognize_content.split("Material")[1].split()[1]
    except:
        pass
    try:
        price = recognize_content.split("Shipping")[0].split()[-1]
    except:
        pass
    score = ''
    try:
        second_area = Image.open(img_path)
        recognize_content = pytesseract.image_to_string(second_area)
        score = recognize_content.split("outof 5")[0].split()[-1]
    except:
        pass
    return product_title, rating_num, brand, product_color, style, material, price, score


def get_tmp_sample(ids, product_title, rating_num, brand, color, style, material, price, score):
    tmp_sample = {}
    tmp_sample['ids'] = ids
    tmp_sample['product_title'] = product_title
    tmp_sample['rating_num'] = rating_num
    tmp_sample['brand'] = brand
    tmp_sample['color'] = color
    tmp_sample['style'] = style
    tmp_sample['material'] = material
    tmp_sample['price'] = price
    try:
        if int(score) > 5:
            tmp_sample['score'] = score[0] + '.' + score[1]
    except:
        tmp_sample['score'] = score
    return tmp_sample


def get_important_information(img_path_list):
    all_samples = []
    for img_path in tqdm(img_path_list):
        ids = img_path.split('/')[-1].split('.')[0]
        product_title, rating_num, brand, color, style, material, price, score = get_product_information(img_path)
        tmp_sample = get_tmp_sample(ids, product_title, rating_num, brand, color, style, material, price, score)
        all_samples.append(tmp_sample)
        json_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/cattree_json/2022-09-24.json'
        out_file = open(json_path, "w")
        json.dump(all_samples, out_file, indent=6)


if __name__ == '__main__':
    folder_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/cattree_screenshot_pic/2022-09-24'
    img_path_list = get_img_path_list(folder_path)

    get_important_information(img_path_list)
