# file: model.py
# author: BINWong
# time: 2019/1/9 14:13
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

import math


class Node(object):
    """
    建立字典树的节点
    """

    def __init__(self, char):
        self.char = char
        # 记录是否完成
        self.word_finish = False
        # 用来计数
        self.count = 0
        # 用来存放节点
        self.child = []
        # 方便计算 左右熵
        # 判断是否是后缀（标识后缀用的，也就是记录 b->c->a 变换后的标记）
        self.isback = False


class TrieNode(object):
    """
    建立前缀树，并且包含统计词频，计算左右熵，计算互信息的方法
    """

    def __init__(self, node, data=None, PMI_limit=20):
        """
        初始函数，data为外部词频数据集
        :param node:
        :param data:
        """
        # 建立字典树
        self.root = Node(node)
        self.PMI_limit = PMI_limit
        if not data:
            return
        node = self.root
        for key, values in data.items():
            # 创建词节点
            new_node = Node(key)
            # 设置词出现的次数
            new_node.count = int(values)
            # 设置为记录完成
            new_node.word_finish = True
            # 把创建的字典节点保存到
            node.child.append(new_node)

    def add(self, word):
        """
        添加节点，对于左熵计算时，这里采用了一个trick，用a->b<-c 来表示 cba
        具体实现是利用 self.isback 来进行判断
        :param word: 是一个列表,列表里边词语组合
        :return:  相当于对 [a, b, c] a->b->c, [b, c, a] b->c->a
        """
        node = self.root
        # 正常加载
        # 将列表枚举 得到下标和词
        for count, char in enumerate(word):
            # 设置查找状态false
            found_in_child = False
            # 在节点中找这个词
            for child in node.child:
                # 如果找到了这个词
                if char == child.char:
                    # 设置当前节点为此节点
                    node = child
                    # 设置查找状态为true
                    found_in_child = True
                    # 查找完成，退出查找
                    break

            # 顺序在节点后面添加节点。 a->b->c
            # 如果没有找到这个词（说明咱们原来没有这个词）
            if not found_in_child:
                # 那就给这个词创建一个新的节点
                new_node = Node(char)
                # 把新的的节点添加到node里边去
                node.child.append(new_node)
                # 设置当前节点为新创建的这个节点
                node = new_node

            # 判断是否是最后一个节点
            if count == len(word) - 1:
                # 如果是最后一个节点，就说明这个词组结束了
                # 给这个词组出现的次数+1
                node.count += 1
                # 设置本词组结束
                node.word_finish = True

        # 建立后缀表示
        # 记录总长度
        length = len(word)
        # 设置节点为根节点
        node = self.root
        # 如果此词组总长度为3
        if length == 3:
            # 因为word可能为列表也可能为集合，所以咱们要把它转为list列表方便计算
            word = list(word)
            # 当词组长度为3时，进行交换位置操作 a,b,c -> b,c,a
            word[0], word[1], word[2] = word[1], word[2], word[0]

            # 枚举这个词组，得到下标和词
            for count, char in enumerate(word):
                # 设置
                found_in_child = False
                # 在节点中找字符（不是最后的后缀词）
                if count != length - 1:
                    for child in node.child:
                        if char == child.char:
                            node = child
                            found_in_child = True
                            break
                else:
                    # 由于初始化的 isback 都是 False， 所以在追加 word[2] 后缀肯定找不到
                    for child in node.child:
                        if char == child.char and child.isback:
                            node = child
                            found_in_child = True
                            break

                # 顺序在节点后面添加节点。 b->c->a
                # 如果没有这个节点 就创建一个节点并追加到这个词组后边
                if not found_in_child:
                    new_node = Node(char)
                    node.child.append(new_node)
                    node = new_node

                # 判断是否是最后一个节点，这个词组每出现一次就+1
                if count == len(word) - 1:
                    node.count += 1
                    # 因为这里是接续前边的词，就设置isback为True
                    node.isback = True
                    node.word_finish = True

    def search_one(self):
        """
        计算互信息: 寻找一阶共现，并返回词概率
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        # 计算 1 gram 总的出现总次数
        total = 0
        # 循环遍历根节点的所有子节点
        for child in node.child:
            # 判断 这个词(词组)是否完成
            if child.word_finish is True:
                # 如果完成 总次数加上此词(词组)出现次数
                total += child.count

        # 计算 当前词(词组) 占整体的比例
        for child in node.child:
            if child.word_finish is True:
                result[child.char] = child.count / total
        return result, total

    def search_bi(self):
        """
        计算互信息: 寻找二阶共现，并返回 log2( P(X,Y) / (P(X) * P(Y)) 和词概率
        :return:
        """
        # 结果保存的字典
        result = {}
        # 设置根节点
        node = self.root
        # 如果节点数为空，就直接返回
        if not node.child:
            return False, 0

        # 设置total初始值为0
        total = 0
        # 1 grem 各词的占比，和 1 grem 的总次数
        one_dict, total_one = self.search_one()
        # 循环遍历 一级节点
        for child in node.child:
            # 循环遍历 二级节点
            for ch in child.child:
                # 如果这个词(词组)完成
                if ch.word_finish is True:
                    # 词(词组) 总数 加上此词组数
                    total += ch.count

        # 循环遍历一级节点
        for child in node.child:
            # 循环遍历二级节点
            for ch in child.child:
                # 如果这个词(词组) 结束
                if ch.word_finish is True:
                    # 互信息值越大，说明 a,b 两个词相关性越大
                    PMI = math.log(max(ch.count, 1), 2) - math.log(total, 2) - math.log(one_dict[child.char],
                                                                                        2) - math.log(one_dict[ch.char],
                                                                                                      2)
                    # 这里做了PMI阈值约束
                    if PMI > self.PMI_limit:
                        # 例如: dict{ "a_b": (PMI, 出现概率), .. }
                        result[child.char + '_' + ch.char] = (PMI, ch.count / total)
        return result

    def search_left(self):
        """
        寻找左频次
        统计左熵， 并返回左熵 (bc - a 这个算的是 abc|bc 所以是左熵)
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        # 循环一级节点，这里的child是一级节点
        for child in node.child:
            # 循环二级节点这里的cha是二级节点
            for cha in child.child:
                # 记录此 cha 节点下 三级交换过的词组出现总次数
                total = 0
                # p应该是概率的意思
                p = 0.0
                # 循环 cha 节点下的三级节点，这里的ch是三级节点
                for ch in cha.child:
                    # 如果这个词(词组)结束了，并且这个词(词组)是交换过的
                    # 这个if的作用是统计词组长度为3的，交换过的词出现总次数
                    # 作者写的：if ch.word_finish is True and ch.isback:
                    if ch.word_finish and ch.isback:  # 优化后的
                        # 总数加上此词(词组)次数
                        total += ch.count
                # 还是 cha 节点下的循环三级节点，这里的ch是三级节点
                for ch in cha.child:
                    # 这个if的作用是计算此词组的信息
                    if ch.word_finish and ch.isback:
                        p += (ch.count / total) * math.log(ch.count / total, 2)
                # 计算的是此cha的信息熵
                result[child.char + cha.char] = -p
        return result

    def search_right(self):
        """
        寻找右频次
        统计右熵，并返回右熵 (ab - c 这个算的是 abc|ab 所以是右熵)
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return False, 0

        # 循环遍历一级节点，child是一级节点对象
        for child in node.child:
            # 循环遍历二级节点，这里的cha是二级节点对象
            for cha in child.child:
                # 此二级词组出现的总次数
                total = 0
                p = 0.0
                for ch in cha.child:
                    if ch.word_finish is True and not ch.isback:
                        total += ch.count
                for ch in cha.child:
                    if ch.word_finish is True and not ch.isback:
                        p += (ch.count / total) * math.log(ch.count / total, 2)
                # 计算的是信息熵
                result[child.char + cha.char] = -p
        return result

    def find_word(self, N):
        # 通过搜索得到互信息
        # 例如: dict{ "a_b": (PMI, 出现概率), .. }
        bi = self.search_bi()
        # 通过搜索得到左右熵
        left = self.search_left()
        right = self.search_right()
        result = {}
        for key, values in bi.items():
            d = "".join(key.split('_'))
            # 计算公式 score = PMI + min(左熵， 右熵) => 熵越小，说明越有序，这词再一次可能性更大！
            result[key] = (values[0] + min(left[d], right[d])) * values[1]

        # 按照 大到小倒序排列，value 值越大，说明是组合词的概率越大
        # result变成 => [('世界卫生_大会', 0.4380419441616299), ('蔡_英文', 0.28882968751888893) ..]
        result = sorted(result.items(), key=lambda x: x[1], reverse=True)
        print("result: ", result)
        # 用于保存新词
        dict_list = []
        # add_word用于保存新词及其概率
        add_word = {}

        for d in result:
            # d: (新词, 概率)
            flag = True
            # 循环遍历新词
            print('dict_list = ', dict_list)
            print('d = ', d)
            for tmp in dict_list:
                # 去掉新词中间的下划线得到第一个词
                pre = tmp.split('_')
                now = d[0].split('_')

                # 新出现单词后缀，再老词的前缀中 or 如果发现新词，出现在列表中; 则跳出循环 
                # 前面的逻辑是： 如果A和B组合，那么B和C就不能组合(这个逻辑有点问题)，例如：`蔡_英文` 出现，那么 `英文_也` 这个不是新词
                # 疑惑: **后面的逻辑，这个是完全可能出现，毕竟没有重复**
                # print(d[0].split('_')[-1], '==', pre)
                # print("".join(tmp.split('_')), 'in', "".join(d[0].split('_')))
                if now[-1] == pre[0] or now[0] == pre[-1] or "".join(tmp.split('_')) in "".join(d[0].split('_')):
                    # 如果不满足上述条件，就设置flag为False
                    # pre = '世界卫生'，
                    flag = False
                    break
            # 如果此新词符合条件，就添加这个新词
            if flag:
                new_word = "".join(d[0].split('_'))
                add_word[new_word] = d[1]
                dict_list.append(d[0])
                N -= 1
                if N <= 0:
                    break

        return result, add_word
