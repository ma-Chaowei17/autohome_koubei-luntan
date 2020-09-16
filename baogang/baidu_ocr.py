import random

from aip import AipOcr

# 18066371
# mlDT7FOgc0a5gtn4dGtpMdVO
# y8f1EwBttvnPQu3MvEGTKzVh1OS03SK6

# 18066468
# I4yS9obZm1SBAQMbOnaDklxF
# 4OIYoR5ZQFN9pC5vL1fOAWG73FFtZbN0

import requests
import base64


def get_word(image):
    # encoding:utf-8

    '''
    通用文字识别
    '''

    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(image, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    access_token = '24.4d8798866f99ab8e0e3dccd490e1927c.2592000.1590473619.282335-19612178'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers, timeout=5)

    # print(result)
    words_result = response.json()['words_result']
    word_list = ""
    for i in range(len(words_result)):
        word_list = word_list + words_result[i]['words']
    # print(word_list)
    return list(word_list)


if __name__ == "__main__":
    a = get_word("./sss.jpg")
    print(a)
    # print(a)
