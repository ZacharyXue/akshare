# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
Date: 2024/8/22 11:44
Desc: 东方财富网-REITs-REITs信息
https://quote.eastmoney.com/sz180301.html
"""

import pandas as pd
import requests
import re
from datetime import datetime

from reits_utils import code_id_map_em, get_html_info, get_html_dividend


class REIT:
    def __init__(self, symbol: str = "180301"):
        self.code = symbol
        self.url = f"https://fundf10.eastmoney.com/jbgk_{symbol}.html"

        self.info = {}
        self.html_info(
            table_name= 'info w790',
            keys= ['基金全称', '基金简称', '基金代码', '发行日期', '资产规模', '成立来分红']
        )
        self.request_info()
        self.cal_turnoverrate()
        self.cal_dividendrate()

        self.name = self.info['基金简称']

    def __str__(self) -> str:
        ret = f'{self.name}\n'
        for k in self.info:
            v = self.info[k][0] if isinstance(self.info[k], list) \
                else self.info[k]
            ret += f' - {k}: {v}\n'
        
        return ret

    def html_info(self,
            table_name: str = 'info w790',
            keys: list = None,
            timeout: float = None
    ) -> dict:
        """
        东方财富-个股-REITs信息
        https://quote.eastmoney.com/sz180301.html

        :param timeout: choice of None or a positive float number
        :type timeout: float
        :return: 股票信息
        :rtype: dict
        """
        
        keys = keys if keys else \
            ['基金全称', '基金简称', '基金代码', '发行日期', '资产规模', '成立来分红']

        info = get_html_info(
            url=self.url,
            table_name=table_name,
            keys=keys,
            timeout=timeout
        )    
        # print(info)
        self.info.update(info)
        return info

    def request_info(self,
            timeout: float = None
    ) -> dict:
        """
        东方财富-个股-REITs信息
        https://quote.eastmoney.com/sz180301.html

        :param timeout: choice of None or a positive float number
        :type timeout: float
        :return: 股票信息
        :rtype: dict
        """
        code_id_dict = code_id_map_em()
        if self.code not in code_id_dict:
            print(f"{self.code} is not found")
            return None
        
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fltt": "1",
            "invt": "2",
            "fields": "f58,f734,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f47,f48,f19,f17,f531,f15,f13,f11,f20,f18,f16,f14,f12,f39,f37,f35,f33,f31,f40,f38,f36,f34,f32,f211,f212,f213,f214,f215,f210,f209,f208,f207,f206,f161,f49,f171,f50,f86,f168,f108,f167,f71,f292,f51,f52,f191,f192,f452,f177",
            "secid": f"{code_id_dict[self.code]}.{self.code}",
            "_": "1640157544804",
        }
        r = requests.get(url=url, params=params, timeout=timeout)
        data = r.json()['data']
        # print(data)

        res = dict()
        output_num = lambda n: n if isinstance(n, (float, int)) else 0
        res['当前价格'] = output_num(data['f43']) / 1e3
        res['成交量'] = f"{output_num(data['f47']) / 1e4}万"
        self.info.update(res)
        return res

    def cal_turnoverrate(self):
        if '资产规模' not in self.info or \
            '成交量' not in self.info:
            return
        
        total_share = re.findall("份额规模(\d+.\d+)", \
                                 self.info['资产规模'][0])
        if total_share:
            total_share = float(total_share[0])
        else:
            return
        traded_share = re.findall("\d+.\d+", self.info['成交量'])
        if not traded_share:
            return 
        else:
            traded_share = float(traded_share[0])

        res = dict()
        res['换手率'] = f"{traded_share / total_share:.2f}%"
        self.info.update(res)
        return res

    def cal_dividendrate(self):
        if '成立来分红' not in self.info:
            return
        if '当前价格' not in self.info or self.info['当前价格'] < 0.1:
            return
        
        url = self.info['成立来分红'][1]
        curr_price = self.info['当前价格']
        dividend_dict = get_html_dividend(url=url)

        curr_date = datetime.now()
    
        dates = [datetime.strptime(date_str, "%Y-%m-%d") 
                 for date_str in dividend_dict.keys()]
        dates_curr = [date.strftime("%Y-%m-%d") for date in dates if date.year == curr_date.year]
        dates_last = [date.strftime("%Y-%m-%d") for date in dates if date.year == curr_date.year - 1]
        # print(f"all dates:{dividend_dict.keys()}")
        # print(f"curr_date:{curr_date}\n dates_curr:{dates_curr}\n dates_last:{dates_last}")

        curr_dividend = sum([dividend_dict[date]['每份分红']  for date in dates_curr])
        last_dividend = sum([dividend_dict[date]['每份分红']  for date in dates_last])
        # print(f"curr_diviend:{curr_dividend}, last_dividend:{last_dividend}, curr_price:{curr_price}")

        res = dict()
        res['今年分红率'] = f'{curr_dividend * 100. / curr_price:.2f}%'
        res['去年分红率'] = f'{last_dividend * 100. / curr_price:.2f}%'  # 以当前价格去年股息估计去年股息
        res['今年分红'] = curr_dividend
        res['今年分红次数'] = len(dates_curr)
        res['去年分红'] = last_dividend
        res['去年分红次数'] = len(dates_last)

        # print(res)
        self.info.update(res)
        return res


if __name__ == "__main__":
    # tmp = REIT()
    # print(tmp)
    # tmp.cal_dividendrate()
    code_id_dict = code_id_map_em()
    for code in code_id_dict.keys():
        print(REIT(symbol=code))
