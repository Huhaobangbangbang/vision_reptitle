"""
 -*- coding: utf-8 -*-
 author： Hao Hu
 @date   2022/10/13 10:13 PM
"""
from importlib.resources import contents
from selenium import webdriver
from time import sleep
import time
from lxml import etree
from selenium.webdriver.common.by import By
import requests
import os, json
import os.path as osp
import random
from lxml import etree
import asyncio
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from email_reminder import send_email_to_remind
import datetime
hea = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'En-Us',
    'cache-control': 'max-age=0',
    'downlink': '8',
    'ect': '4g',
    'rtt': '250',
    'Cookie': "session-id=257-3500989-3695223; i18n-prefs=GBP; ubid-acbuk=257-5950834-2508848; x-wl-uid=1bEcLG2b03/1tAwPJNyfuRH+U7J9ZaPYejSBR4HXKuYQPJtLhQbDYyO/GOMypGKXqZrG7qBkS0ng=; session-token=x04EF8doE84tE+6CXYubsjmyob/3M6fdmsQuqzD0jwl/qGdO5aRc2eyhGiwoD0TFzK1rR/yziHsDS4v6cdqT2DySFXFZ9I5OHEtgufqBMEyrA0/Scr87KKA+GWOjfVmKRuPCqOGaixZQ6AIjU3e2iFOdM+3v90NeXFI3cazZcd6x9TYCy9b5u9V8zR7ePbdP; session-id-time=2082758401l; csm-hit=tb:MAA188S1G57TNTH6HQCZ+s-T9EGT4C8FC8J74X5T7CY|1594212767446&t:1594212767446&adb:adblk_no",
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}


def initializate_options():
    """初始化"""
    # 启动并初始化Chrome
    options = webdriver.ChromeOptions()  # 初始化Chrome
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("disable-web-security")
    options.add_argument('disable-infobars')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])

    return options



def gethtml(url0, head):
    """为了得到静态页面HTML，有对页面反应超时的情况做了些延时处理"""
    i = 0
    stop_time= random.uniform(10,20)
    sleep(stop_time)
    while i < 5:
        try:
            html = requests.get(url=url0, headers=head, timeout=(10, 20))
            repeat = 0
            while (html.status_code != 200):  # 错误响应码重试
                print('error: ', html.status_code)
                time.sleep(5)
                repeat += 1
                html = requests.get(url=url0, headers=head, timeout=(10, 20))
                if (html.status_code != 200 and repeat == 2):
                    return html, repeat
            return html, repeat
        except requests.exceptions.RequestException:
            print('超时重试次数: ', i + 1)
            i += 1
    raise Exception()

def get_ids_list(link_list):
    result_list = []
    for link_tmp in link_list:
        ids = link_tmp.split("/")[-2]
        if 'picasso' in ids or 'sspa' in ids:
            pass
        else: 
            result_list.append("{}\n".format(ids))
    return result_list

def get_sample(rating_num,intruction,stars,price,tmp_ids):
    tmp_sample = {}
    tmp_sample[tmp_ids[:-1]] = {}
    try:
        tmp_sample[tmp_ids[:-1]]['rating_num'] = rating_num[0]
    except:
        tmp_sample[tmp_ids[:-1]]['rating_num'] = ''
    try:
        tmp_sample[tmp_ids[:-1]]['instruction'] = intruction[0]
    except:
        tmp_sample[tmp_ids[:-1]]['instruction'] = ''
    try:
        tmp_sample[tmp_ids[:-1]]['stars'] = stars[0]
    except:
        tmp_sample[tmp_ids[:-1]]['stars'] = ''
    try:
        tmp_sample[tmp_ids[:-1]]['price'] = price[0]
    except:
        tmp_sample[tmp_ids[:-1]]['price'] = ''
    return tmp_sample



def cope_string(html_str):
    """处理网页中的字符串"""
    ids = html_str.split('div data-asin="')[1].split('"')[0]
    ids_to_information ={}
    if len(ids)==0:
        pass
    else:
   
        ids_to_information[ids] = {}
        ids_type = 'normal'
        if 'Amazon brand' in html_str:
            ids_type = 'Amazon brand' 
        elif 'Sponsored' in html_str:
            ids_type = 'Sponsored'
        if 'Best Seller' in html_str:
            ids_to_information[ids]['Best_Seller'] = 'yes'
        else:
            ids_to_information[ids]['Best_Seller'] = 'no'
        ids_to_information[ids]['ids_type'] = ids_type
        
    return ids_to_information
                


def get_items(req):
    """使用Xpath解析页面，提取商品信息"""
    if (type(req) == str):
        html = etree.HTML(req)
    else:
        html = etree.HTML(req.text)
    sample_list = []
    for index in range(100):
        try:
            xpath_str = '//div[@data-index="{}"]'.format(index)
            products_information_list = html.xpath(xpath_str)
            html_str = str(etree.tostring(products_information_list[0]))
            ids_to_information = cope_string(html_str)
            if len(ids_to_information) == 0:
                pass
            else:
                sample_list.append(ids_to_information)
        except IndexError:
            break
    return sample_list
    # return sample_list,ids_list


def put_dict_lis(results_list):
    """得到列表中的字典的键"""
    ids_list = []
    for sample in results_list:
        print(sample)
        key = list(sample)[0]
        ids_list.append("{}\n".format(key))
    return ids_list


def get_sort_data(results_list):
    folder = '/home/vision/projects/huhao_reptile_DON_NOT_DELETE/huhao/data/ccattree_rank_ads_no_ads'
    today_date = str(datetime.datetime.now()).split()[0]+'-'+str(datetime.datetime.now()).split()[1][:2]+'-'+str(datetime.datetime.now()).split()[1][3:5]
    result_path = osp.join(folder,today_date+'.json')
    results = {}
    results['rank_samples'] = results_list
    ids_list = put_dict_lis(results_list)
    out_file = open(result_path, "w")
    json.dump(results, out_file, indent=6)
    txt_path = osp.join(folder,today_date+'.txt')
    with open(txt_path,'w') as fp:
        fp.writelines(ids_list)


if __name__ == '__main__':
    #启动并初始化Chrome
    first_page = 'https://www.amazon.com/s?k=cattree&crid=2BDJM8GZOOEQ3&sprefix=cattree%2Caps%2C682&ref=nb_sb_noss_2'
    second_page = 'https://www.amazon.com/s?k=cattree&page=2&crid=2BDJM8GZOOEQ3&qid=1664254901&sprefix=cattree%2Caps%2C682&ref=sr_pg_2'
    
    url_list = [first_page,second_page]
    sample_list = []
    ids_result_list = []
    for url in url_list:
        try:
            options = initializate_options()
            driver = webdriver.Chrome(chrome_options=options)
            driver.get(url)
            req, error = gethtml(url, hea)  # 默认header
            tmp_list = get_items(req)
            sample_list = sample_list+tmp_list 
            wait = WebDriverWait(driver, 20)
            driver.quit()  # 关闭浏览器
        except:
            send_email_to_remind()
    get_sort_data(sample_list)
        
        
    
        
