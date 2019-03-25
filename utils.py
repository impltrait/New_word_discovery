# file: utils.py
# author: BINWong
# time: 2019/1/9 14:23
# Copyright 2019 BINWong. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

import pickle


def get_stopwords():
    with open('data/stopword.txt', 'r', encoding='utf-8') as f:
        stopword = [line.strip() for line in f]
    return set(stopword)


def generate_ngram(input_list, n):
    """

    :param input_list: ['台湾', '中', ····· '时', '电子报'] 这个列表可能是空的
    :param n: 3
    :return:
    """
    result = []

    # 这里不同请看 README.md
    for i in range(1, n + 1):
        result.extend(zip(*[input_list[j:] for j in range(i)]))
    return result


def load_dictionary(filename):
    """
    加载外部词频记录
    :param filename:
    :return:
    """
    word_freq = {}
    print('------> 加载外部词集')
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                line_list = line.strip().split(' ')
                # 规定最少词频
                if int(line_list[1]) > 2:
                    word_freq[line_list[0]] = line_list[1]
            except IndexError as e:
                print(line)
                continue
    """
    {
     '成功'： '3',
     ·····
     '赋予'： '6'
    }
    """
    return word_freq


def save_model(model, filename):
    with open(filename, 'wb') as fw:
        # 数据序列
        pickle.dump(model, fw)


def load_model(filename):
    with open(filename, 'rb') as fr:
        # 反序列化
        model = pickle.load(fr)
    return model
