"""
 -*- coding: utf-8 -*-
 author： Hao Hu
 @date   2022/10/5 9:10 PM
"""
import os
from email_reminder import send_email_to_remind
from tqdm import tqdm
import json
import traceback
from PIL import Image
import pytesseract
from pytesseract import Output

CUDA_VISIBLE_DEVICES = 3


def get_img_path_list(folder_path):
    ids_list = os.listdir(folder_path)
    ids_to_img_path = {}
    for ids in ids_list:
        ids_to_img_path[ids] = {}
        ids_folder_path = os.path.join(folder_path, ids)
        img_list = os.listdir(ids_folder_path)
        ids_to_img_path[ids]['review_screenshots'] = []
        ids_to_img_path[ids]['homepage'] = os.path.join(ids_folder_path, ids + '.png')
        for sample in img_list:
            if ids in sample:
                pass
            else:
                img_path = os.path.join(ids_folder_path, sample)
                ids_to_img_path[ids]['review_screenshots'].append(img_path)

    return ids_to_img_path


def get_product_information(img_path):
    first_box = (370, 3800, 1127, 8000)
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


def get_homepage_sample(ids, product_title, rating_num, brand, color, style, material, price, score):
    """通过首页的截图，得到商品的信息"""
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


def string_to_ordinate(img_path):
    """返回每一行句子，主要是为了得到顾客姓名和title"""
    review_box = (10, 800, 900, 7000)
    fist_area = Image.open(img_path).crop(review_box)
    recognize_content = pytesseract.image_to_data(fist_area, output_type=Output.DICT)
    complete_sentence = []
    tmp_sentence = ''
    balance_tl_y = 0
    for index in range(0, len(recognize_content["text"])):
        text = recognize_content["text"][index]
        tmp_tl_y = recognize_content["top"][index]
        if abs(balance_tl_y - tmp_tl_y) > 5:
            complete_sentence.append(tmp_sentence)
            balance_tl_y = tmp_tl_y
            tmp_sentence = text
        else:
            tmp_sentence = tmp_sentence + ' ' + text

    return complete_sentence


def get_title_and_name(complete_sentence, name_and_title):
    """得到顾客姓名和title"""
    stars_misidentification = ['Fode', 'Fefe', 'Fede', 'Sede']
    title_str = ''
    for tmp_index in range(len(name_and_title)):
        title_flag = 0
        for sample in stars_misidentification:
            if sample in name_and_title[tmp_index]:
                title_flag = 1
                for title_index in range(tmp_index + 1, len(name_and_title)):
                    title_str = title_str + ' ' + name_and_title[title_index]

    if title_flag == 1 or len(title_str) == 0:
        title_list = []
        # for tmp_index in  range(len(name_and_title),-1,-1):
        for sample in complete_sentence:
            if name_and_title[-1] in sample:
                title_list.append(sample)
        for tmp_index in range(len(name_and_title) - 1, -1, -1):
            for sample in title_list:
                if name_and_title[tmp_index] in sample:
                    pass
                else:
                    title_list.remove(sample)
                    break

            if len(title_list) == 1:
                title = title_list[0]
        if len(title_list) >= 1:
            for sample in title_list[-1].split():
                flag = 0
                for tmp_sample in stars_misidentification:
                    if tmp_sample in sample:
                        flag = 1
                if flag == 0:
                    title_str = title_str + ' ' + sample
    title_index = 0
    flag = 0
    # 定位title的位置，然后得到complete_sentence上一个的元素
    # title_str_list = title_str.split()
    # for sample,index in enumerate(complete_sentence):
    #     for title_content in title_str_list:
    #         if str(title_content) not in str(sample):
    #             flag = 0
    #             break
    #         else:
    #             flag = 1
    #     if flag == 1:
    #         title_index = index-1
    # if title_index==0:
    #     customer_name = ''
    # if title_index>0:
    #     customer_name = complete_sentence[title_index]

    return title_str


def put_list_to_sentence(normal_list):
    normal_str = ''
    for sample in normal_list:
        normal_str = normal_str + ' ' + str(sample)
    return normal_str


def get_review_sample(helpful_count, review_content, review_place, product_information, title_str):
    sample = {}

    sample['helpful_count'] = put_list_to_sentence(helpful_count)
    sample['review_place'] = put_list_to_sentence(review_place)
    sample['product_information'] = put_list_to_sentence(product_information)
    sample['title'] = title_str
    sample['review_content'] = put_list_to_sentence(review_content)
    return sample


def get_reviews(img_path):
    """得到截图中所对应的评论"""
    first_box = (10, 800, 880, 7000)
    helpful_count = ['0']
    fist_area = Image.open(img_path).crop(first_box)
    recognize_content = pytesseract.image_to_string(fist_area)
    complete_sentence = string_to_ordinate(img_path)
    recognize_content_list = recognize_content.split()
    reviews_list = []
    # STARS识别出来的单词经常包含Fode,Fefe,Fede

    for index in range(len(recognize_content_list)):
        if recognize_content_list[index] == 'Report' and recognize_content_list[index + 1] == 'abuse':
            try:
                content_end_index = index - 1
                if recognize_content_list[index - 1] == 'Helpful':
                    content_end_index = index - 2
                    if recognize_content_list[index - 2] == 'helpful':
                        helpful_count = recognize_content_list[index - 6:index - 2]
                        content_end_index = index - 7
                for tmp_index in range(content_end_index, -1, -1):
                    if recognize_content_list[tmp_index] == 'Purchase' and recognize_content_list[
                        tmp_index - 1] == 'Verified':
                        review_content = recognize_content_list[tmp_index + 1:content_end_index]
                        break

                # get review_in_index
                for tmp_index in range(tmp_index - 1, -1, -1):
                    if recognize_content_list[tmp_index] == 'Reviewed' and recognize_content_list[
                        tmp_index + 1] == 'in':
                        review_place = recognize_content_list[tmp_index:tmp_index + 9]
                        product_information = recognize_content_list[tmp_index + 9:tmp_index - 2]
                        name_and_title = recognize_content_list[tmp_index - 15:tmp_index]
                        title_str = get_title_and_name(complete_sentence, name_and_title)
                        break
                # print(helpful_count)
                tmp_sample = get_review_sample(helpful_count, review_content, review_place, product_information,
                                               title_str)
                reviews_list.append(tmp_sample)
            except:
                traceback.print_exc()
                print('traceback.format_exc():\n%s' % traceback.format_exc())
    return reviews_list


def get_json(ids_to_img_path):
    """通过ids_to_img_path字典将信息保存到json上面"""
    folder_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/cattree_screenshot_pic/json_2022_10_1'
    for ids, value in tqdm(ids_to_img_path.items()):
        tmp_sample = {}
        json_path = os.path.join(folder_path, ids + '.json')
        review_page_and_homepage = ids_to_img_path[ids]
        review_page_list = review_page_and_homepage['review_screenshots']
        home_page = review_page_and_homepage['homepage']
        all_reviews_list = []
        for img_path in tqdm(review_page_list):
            reviews_list = get_reviews(img_path)
            all_reviews_list += reviews_list
        product_title, rating_num, brand, product_color, style, material, price, score = get_product_information(
            home_page)
        homepage_sample = get_homepage_sample(ids, product_title, rating_num, brand, product_color, style, material,
                                              price, score)
        tmp_sample['product_information'] = homepage_sample
        tmp_sample['reviews'] = all_reviews_list
        out_file = open(json_path, "w")
        json.dump(tmp_sample, out_file, indent=6)


if __name__ == '__main__':
    folder_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/cattree_screenshot_pic/2022-10-01'
    ids_to_img_path = get_img_path_list(folder_path)
    get_json(ids_to_img_path)




