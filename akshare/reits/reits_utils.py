# -*- coding:utf-8 -*-
# !/usr/bin/env python

from functools import lru_cache

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re


@lru_cache()
def code_id_map_em() -> dict:
    """
    东方财富- REITs和市场代码
    https://quote.eastmoney.com/center/gridlist.html#fund_reits_all
    :return: REITs和市场代码
    :rtype: dict
    """
    url = "https://53.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:1 t:9 e:97",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, timeout=15, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df["market_id"] = 1
    temp_df.columns = ["sh_code", "sh_id"]
    code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
    params = {
        "pn": "1",
        "pz": "50000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0 t:10 e:97",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, timeout=15, params=params)
    data_json = r.json()
    if not data_json["data"]["diff"]:
        return dict()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["sz_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
    return code_id_dict


def get_absolute_path(
        url: str,
        tgt: str
)-> str:
    if not tgt or not url:
        return ""
    
    if tgt[0] == '/':
        return "https:" + tgt
    else:
        url_list = url.split('/')
        url_list[-1] = tgt
        return '/'.join(url_list)


def get_html_info(
        url: str =  "https://fundf10.eastmoney.com/jbgk_180301.html",
        table_name: str = 'info w790',
        keys: list = [],
        timeout: float = None
) -> dict:
    """
    reits 基金页面基本概况的解析
    url: https://fundf10.eastmoney.com/jbgk_180301.html 
    """
    r = requests.get(url, timeout=timeout)
    if r.status_code != 200:
        print(f"request failed, url={url},\
              status={r.status_code}")
        return None
    
    html_content = r.text
    # 解析 html
    soup = BeautifulSoup(html_content, 'html.parser')
    # 获取 https://fundf10.eastmoney.com/jbgk_180301.html 基本概括表格
    table = soup.find('table', class_=table_name)
    res = {}
    keys = set(keys)

    for row in table.find_all('tr'):
        # 找到当前行中的所有<th>和<td>元素
        headers = row.find_all('th')
        cells = row.find_all('td')

        # 假设每个<tr>行中都有两个<th>和两个<td>，且标题和数据是成对出现的
        for header, cell in zip(headers, cells):
            # 提取文本内容
            header_text = header.get_text(strip=True)
            cell_text = cell.get_text(strip=True)

            if keys and header_text not in keys:
                continue
            
            # print(f"{header_text}: {cell_text}")
            res[header_text] = cell_text

            # 如果<td>中包含<a>标签，也提取链接
            a_tag = cell.find('a')
            if a_tag:
                res[header_text]= [
                    cell_text,
                    get_absolute_path(url, a_tag['href'])
                ]
                # print(f"Link: {a_tag['href']}")

    return res


def get_html_dividend(
        url: str =  "https://fundf10.eastmoney.com/fhsp_180301.html",
        table_name: str = 'w782 comm cfxq',
        timeout: float = None
) -> dict:
    """
    reits 基金页面基本概况的解析
    url: https://fundf10.eastmoney.com/fhsp_180301.html
    """
    r = requests.get(url, timeout=timeout)
    if r.status_code != 200:
        print(f"request failed, url={url},\
              status={r.status_code}")
        return None
    
    html_content = r.text
    # 解析 html
    soup = BeautifulSoup(html_content, 'html.parser')
    # 获取 https://fundf10.eastmoney.com/fhsp_180301.html 分红信息
    # 只获取 登记日与分红现金
    table = soup.find('table', class_=table_name)
    # 提取表头数据
    headers = [th.get_text() for th in table.find('thead').find_all('th')]
    # 提取表体数据
    rows = table.find('tbody').find_all('tr')

    res = {}
    pattern = "(\d+\.\d+)元"
    # 遍历每一行，提取单元格数据
    for row in rows:
        cells = row.find_all('td')
        # 获取每行的数据并去除多余的空格
        data = [cell.get_text(strip=True) for cell in cells]
        curr = dict(zip(headers, data))

        if '每份分红' in curr:
            dividend = re.findall(pattern, curr['每份分红'])
            if dividend:
                curr['每份分红'] = float(dividend[0])
            else:
                curr['每份分红'] = 0.

            res[curr['权益登记日']] = curr

    # print(res)
    return res

if __name__ == "__main__":
    get_html_dividend()
    