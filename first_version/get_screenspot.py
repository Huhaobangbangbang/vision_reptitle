"""
 -*- coding: utf-8 -*-
 author： Hao Hu
 @date   2022/9/24 12:09 PM
"""
import asyncio
from turtle import width
from pyppeteer import launch
import random
from time import sleep#,zh-CN,zh;q=0.9
import datetime
import os.path as osp
import os
from tqdm import tqdm
async def get_new_links():
    browser = await launch()
    # open a new tab in the browser
    page = await browser.newPage()
    # add URL to a new page and then open it
    await page.goto(
        "https://www.amazon.com/s?k=projector&crid=20CY5D5M2QELJ&sprefix=projector%2Caps%2C593&ref=nb_sb_noss_1")
    link_elements = await page.Jx('//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')
    link_list = []
    for item in link_elements:
        # 获取链接：通过getProperty方法获取
        title_link = await (await item.getProperty('href')).jsonValue()
        link_list.append(title_link)
    return link_list


def check_already_get(folder_path):
    img_list = os.listdir(folder_path)
    ids_list = []
    for sample in img_list:
        ids_list.append(sample.split(".")[0])
    return ids_list



async def screenshot_scroll(link_list):
    # launch chromium browser in the background
    folder_name = str(datetime.date.today())
    log_path = '/cloud/cloud_disk/users/huh/nlp/vision-reptile/vision_reptile/data/projector_screenshot_pic'
    folder_path = osp.join(log_path,folder_name)
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    ids_list = check_already_get(folder_path)
    for link_tmp in tqdm(link_list):
        ids = link_tmp.split("/")[-2]
        if ids in ids_list:
            pass
        else:
            try:
                img_path = osp.join(log_path,folder_name,ids+'.png')
                browser = await launch()
                # open a new tab in the browser
                page = await browser.newPage()
                # add URL to a new page and then open it
                await page.goto(link_tmp)
                stop_time= random.uniform(10,20)
                sleep(stop_time)
                # create a screenshot of the page and save it
                await page.setViewport({'width':1200,'height':8000})
                await page.screenshot({"path":img_path})
                # close the browser
                await browser.close()
            except:
                pass



if __name__ == '__main__':
    link_list = asyncio.get_event_loop().run_until_complete(get_new_links())
    # link_list = ['https://www.amazon.com/BOSOZOKU-Cactus-Scratching-Indoor-Kittens/dp/B094QT7325/ref=sr_1_1?crid=2BDJM8GZOOEQ3&keywords=cattree&qid=1664000116&qu=eyJxc2MiOiI2LjMxIiwicXNhIjoiNi4wNCIsInFzcCI6IjQuOTcifQ%3D%3D&sprefix=cattree%2Caps%2C682&sr=8-1'
    # ,'https://www.amazon.com/Go-Pet-Club-62-Inch-Black/dp/B0091OMWUW/ref=sr_1_2?crid=2BDJM8GZOOEQ3&keywords=cattree&qid=1664000116&qu=eyJxc2MiOiI2LjMxIiwicXNhIjoiNi4wNCIsInFzcCI6IjQuOTcifQ%3D%3D&sprefix=cattree%2Caps%2C682&sr=8-2']
    asyncio.get_event_loop().run_until_complete(screenshot_scroll(link_list))


