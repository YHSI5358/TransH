class CutWords:
    def __init__(self):
        dict_path = 'disease.txt'
        self.word_dict, self.max_wordlen = self.load_words(dict_path)

    # 加载词典
    def load_words(self, dict_path):
        words = list()
        max_len = 0
        for line in open(dict_path,encoding="UTF-8"):
            wd = line.strip()
            if not wd:
                continue
            if len(wd) > max_len:
                max_len = len(wd)
            words.append(wd)
        return words, max_len
        
    # 双向最大向前匹配
    def max_biward_cut(self, sent):
        # 双向最大匹配法是将正向最大匹配法得到的分词结果和逆向最大匹配法的到的结果进行比较，从而决定正确的分词方法。
        # 启发式规则：
        # 1.如果正反向分词结果词数不同，则取分词数量较少的那个。
        # 2.如果分词结果词数相同 a.分词结果相同，就说明没有歧义，可返回任意一个。 b.分词结果不同，返回其中单字较少的那个。
        forward_cutlist = self.max_forward_cut(sent)
        backward_cutlist = self.max_backward_cut(sent)
        count_forward = len(forward_cutlist)
        count_backward = len(backward_cutlist)

        def compute_single(word_list):
            num = 0
            for word in word_list:
                if len(word) == 1:
                    num += 1
            return num

        if count_forward == count_backward:
            if compute_single(forward_cutlist) > compute_single(backward_cutlist):
                return backward_cutlist
            else:
                return forward_cutlist

        elif count_backward > count_forward:
            return forward_cutlist

        else:
            return backward_cutlist

