"""
 -*- coding: utf-8 -*-
 author： Hao Hu
 @date   2022/10/5 9:09 PM
"""

from time import sleep
import time
import os, json
import datetime
import os
import os.path as osp
from tqdm import tqdm
import asyncio
from pyppeteer import launch
import random
import pytesseract
from PIL import Image
from pytesseract import Output


def get_ids_list(ori_folder):
    files = os.listdir(ori_folder)
    ids_url_list = []
    for sample in files:
        prefix_url = 'https://www.amazon.com/dp/'
        ids_url_list.append(prefix_url + sample[:-5])
    return ids_url_list


def get_pos(img_path):
    first_box = (370, 3800, 1127, 8000)
    fist_area = Image.open(img_path).crop(first_box)
    recognize_content = pytesseract.image_to_data(fist_area, output_type=Output.DICT)
    text_content = recognize_content['text']
    pos_list = []
    for index in range(len(text_content)):
        if text_content[index] == 'Read' and text_content[index + 1] == 'more':
            pos_list.append([recognize_content['left'][index] + recognize_content['width'][index] / 2 + 370,
                             recognize_content['top'][index] + recognize_content['height'][index] / 2 + 3800])
    return pos_list


async def get_first_reviews_screenshots(page, prefix):
    stop_time = random.uniform(8, 18)
    img_path = prefix + '1.png'
    link_elements = await page.Jx('//a[@data-hook="see-all-reviews-link-foot"]')
    see_all_reviews_link = await (await link_elements[0].getProperty('href')).jsonValue()
    await page.goto(see_all_reviews_link)
    await page.setViewport({'width': 1200, 'height': 8000})
    await page.screenshot({"path": img_path})
    return page


def remove_problemed_page(img_path, folder_path):
    """如果出现验证码，直接删除对应文件夹"""
    if len(pytesseract.image_to_string(Image.open(img_path))) < 360:
        os.system("rm {}".format(folder_path))
        print(folder_path)
    return True


async def get_screenshots(ids_url_list):
    """得到每一个产品的截图"""
    folder_name = str(datetime.date.today())
    folder_name = '2022-10-01'
    log_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/cattree_screenshot_pic/'
    folder_path = osp.join(log_path, folder_name)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    ids_list = []
    files = os.listdir(folder_path)
    for sample in files:
        ids_list.append(sample)
    print(ids_list)
    for link_tmp in tqdm(ids_url_list):
        # link_tmp = 'https://www.amazon.com/dp/B00BFFHPZM'
        ids = link_tmp.split("/")[-1]
        if ids in ids_list:
            pass
        else:
            print(ids)
            ids_path = osp.join(log_path, folder_name, ids)
            img_path = osp.join(log_path, folder_name, ids, ids + '.png')
            if not os.path.isdir(ids_path):
                os.makedirs(ids_path)
            browser = await launch()
            page = await browser.newPage()
            await page.goto(link_tmp)
            await page.setViewport({'width': 1200, 'height': 8000})
            await page.screenshot({"path": img_path})
            first_img_path = osp.join(ids_path, '1.png')
            link_elements = await page.Jx('//a[@data-hook="see-all-reviews-link-foot"]')
            see_all_reviews_link = await (await link_elements[0].getProperty('href')).jsonValue()
            await page.goto(see_all_reviews_link)
            await page.setViewport({'width': 1200, 'height': 8000})
            await page.screenshot({"path": first_img_path})
            next_page_element = await page.Jx('//li[@class="a-last"]')
            index = 1
            while (len(next_page_element) > 0):

                next_page_element = await page.Jx('//li[@class="a-last"]//a')
                if len(next_page_element) > 0:
                    next_page_link = await (await next_page_element[0].getProperty('href')).jsonValue()
                    index += 1
                    tmp_img_path = osp.join(ids_path, str(index) + '.png')
                    await page.goto(next_page_link)
                    sleep(random.uniform(8, 18))
                    await page.setViewport({'width': 1200, 'height': 8000})
                    await page.screenshot({"path": tmp_img_path})
                else:
                    pass
                if len(pytesseract.image_to_string(Image.open(img_path))) < 360:
                    os.system("rm {}".format(folder_path))
                    break

            await browser.close()


if __name__ == '__main__':
    ori_folder = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile_get_review/data'
    ids_url_list = get_ids_list(ori_folder)
    asyncio.get_event_loop().run_until_complete(get_screenshots(ids_url_list))

