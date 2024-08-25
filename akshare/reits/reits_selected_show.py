#!/usr/bin/env python
# -*- coding:utf-8 -*-

from reits_utils import code_id_map_em
from reits_info_em import REIT

import pandas as pd
from copy import deepcopy
from datetime import datetime

def basic_static_info(tgt: list = None) -> None:
    if not tgt:
        return
    tgt = set(tgt)
    reits = {code: REIT(code) for code in tgt}

    # columns: 
    # '基金简称', '基金代码', '发行日期', '资产规模',  
    # '成立来分红','今年分红'('今年分红次数','今年分红率'),'去年分红'('去年分红次数', '去年分红率')
    data = []
    for code,reit in reits.items():
        tmp = []
        tmp.append(reit.name)
        tmp.append(code)
        tmp.append(reit.info['发行日期'])
        tmp.append(reit.info['资产规模'][0])
        tmp.append(reit.info['成立来分红'][0])
        tmp.append(f"{reit.info['今年分红']}元 ( 今年分红{reit.info['今年分红次数']}次, 分红率为{reit.info['今年分红率']} ) ")
        tmp.append(f"{reit.info['去年分红']}元 ( 去年分红{reit.info['去年分红次数']}次，当前价格预计分红率为{reit.info['去年分红率']} ) ")
        data.append(deepcopy(tmp))

    columns = ['基金简称', '基金代码', '发行日期', '资产规模',
               '成立来分红','今年分红', '去年分红']
    reits_info = pd.DataFrame(data=data, columns=columns)

    curr = datetime.now().strftime("%Y-%m-%d")
    reits_info.to_csv(f"reits基本信息-{curr}.csv", encoding='utf_8_sig', index=False)
    # print(reits_info)
    return reits_info


if __name__ == "__main__":
    code_id_dict = code_id_map_em()
    tgt_code = [
        "508077", # 华夏基金华润有巢REIT
        "508068", # 华夏北京保障房REIT
        "508058", # 中金厦门安居REIT
        "180501", # 红土创新深圳安居REIT
        "508031", # 国泰君安城投宽庭保租房REIT
    ]

    basic_static_info(tgt=tgt_code)
