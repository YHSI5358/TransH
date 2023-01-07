import json
import operator # operator模块输出一系列对应Python内部操作符的函数
import time
from tqdm import tqdm 
import numpy as np
import codecs
import datetime

entity2id = {}
relation2id = {}
def test_data_loader(entity_embedding_file, norm_relation_embedding_file, hyper_relation_embedding_file, test_data_file):
    print("load data...")
    file1 = entity_embedding_file
    file2 = norm_relation_embedding_file
    file3 = hyper_relation_embedding_file
    file4 = test_data_file

    entity_dic = {}
    norm_relation = {}
    hyper_relation = {}
    triple_list = []

    with codecs.open(file1, 'r') as f1, codecs.open(file2, 'r') as f2, codecs.open(file3, 'r') as f3:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        lines3 = f3.readlines()
        for line in lines1:
            line = line.strip().split('\t')
            if len(line) != 2:
                continue
            entity_dic[line[0]] = json.loads(line[1])

        for line in lines2:
            line = line.strip().split('\t')
            if len(line) != 2:
                continue
            norm_relation[line[0]] = json.loads(line[1])

        for line in lines3:
            line = line.strip().split('\t')
            if len(line) != 2:
                continue
            hyper_relation[line[0]] = json.loads(line[1])

    with codecs.open(file4, 'r') as f4:
        content = f4.readlines()
        for line in content:
            triple = line.strip().split("\t")
            if len(triple) != 3:
                continue
            
            head = entity2id[triple[0]]
            tail = entity2id[triple[2]]
            relation = relation2id[triple[1]]

            triple_list.append([head, relation, tail])

    print("Complete load. entity : %d , relation : %d , triple : %d" % (
        len(entity_dic), len(norm_relation), len(triple_list)))

    return entity_dic, norm_relation, hyper_relation, triple_list

class testTransH:
    def __init__(self, entities_dict, norm_relation, hyper_relation, test_triple_list):
        self.entities = entities_dict
        self.norm_relation = norm_relation
        self.hyper_relation = hyper_relation
        self.test_triples = test_triple_list
        self.mean_rank = 0
        self.hit_10 = 0
        self.hit_1 = 0
        self.hit_2 = 0

    def test_run(self,recordname):
        hits10 = 0
        hits1 = 0
        hits2 = 0
        rank_sum = 0
        num = 0
        start = time.time()
        for triple in tqdm(self.test_triples,ncols=80):
            num += 1
            rank_head_dict = {}
            rank_tail_dict = {}
            # test_triple: [id,id,id]  entity: { id: emb }
            # entity2id : { <id>: id } relation2id : { <id>: id }
            for entity in self.entities.keys():
                head_triple = [entity, triple[1], triple[2]]

                head_embedding = self.entities[head_triple[0]]
                tail_embedding = self.entities[head_triple[2]]
                norm_relation = self.norm_relation[head_triple[1]]
                hyper_relation = self.hyper_relation[head_triple[1]]
                distance = self.distance(head_embedding, norm_relation,hyper_relation, tail_embedding)
                rank_head_dict[tuple(head_triple)] = distance

            for tail in self.entities.keys():
                tail_triple = [triple[0], triple[1], tail]

                head_embedding = self.entities[tail_triple[0]]
                tail_embedding = self.entities[tail_triple[2]]
                norm_relation = self.norm_relation[tail_triple[1]]
                hyper_relation = self.hyper_relation[tail_triple[1]]
                distance = self.distance(head_embedding, norm_relation, hyper_relation, tail_embedding)
                rank_tail_dict[tuple(tail_triple)] = distance

            # itemgetter 返回一个可调用对象，该对象可以使用操作__getitem__()方法从自身的操作中捕获item
            # 使用itemgetter()从元组记录中取回特定的字段 搭配sorted可以将dictionary根据value进行排序
            # sort 是应用在 list 上的方法，sorted 可以对所有可迭代的对象进行排序操作。

            rank_head_sorted = sorted(rank_head_dict.items(), key=operator.itemgetter(1), reverse=False)
            rank_tail_sorted = sorted(rank_tail_dict.items(), key=operator.itemgetter(1), reverse=False)


            for i in range(len(rank_head_sorted)):
                if triple[0] == rank_head_sorted[i][0][0]:
                    if i < 10:
                        hits10 += 1
                    if i < 1:
                        hits1 += 1
                    if i < 2:
                        hits2 += 1
                    rank_sum = rank_sum + i + 1
                    break

            for i in range(len(rank_tail_sorted)):
                if triple[2] == rank_tail_sorted[i][0][2]:
                    if i < 10:
                        hits10 += 1
                    if i < 1:
                        hits1 += 1
                    if i < 2:
                        hits2 += 1
                    rank_sum = rank_sum + i + 1
                    break
        end = time.time()
        print("epoch: ", num, "cost time: %s" % (round((end - start), 3)))
        self.hit_10 = hits10 / (2 * len(self.test_triples))
        self.hit_1 = hits1 / (2 * len(self.test_triples))
        self.hit_2 = hits2 / (2 * len(self.test_triples))

        self.mean_rank = rank_sum / (2 * len(self.test_triples))
        with codecs.open("weights_and_files/record", "a") as f2:
            print("写record")
            rtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f2.write(recordname + "\thit_10:" + str(self.hit_10)+ "\thit_1:" + str(self.hit_1)+ "\thit_2:" + str(self.hit_2) + "\tmean_rank:" + str(self.mean_rank) +"\t" +rtime)
            f2.write("\n")

        return self.hit_10, self.mean_rank


    def distance(self, h, r_norm, r_hyper, t):
        head = np.array(h)
        norm = np.array(r_norm)
        hyper = np.array(r_hyper)
        tail = np.array(t)
        h_hyper = head - np.dot(norm, head) * norm
        t_hyper = tail - np.dot(norm, tail) * norm
        d = h_hyper + hyper - t_hyper
        return np.sum(np.square(d))



if __name__ == "__main__":

    with codecs.open('weights_and_files/entity2id', 'r') as f1:
        content = f1.readlines()
        for line in content:
            triple = line.strip().split("\t")
            if len(triple) != 2:
                continue
            entity = triple[0]
            id = triple[1]
            entity2id[entity] = id
    with codecs.open('weights_and_files/relation2id', 'r') as f2:
        content = f2.readlines()
        for line in content:
            triple = line.strip().split("\t")
            if len(triple) != 2:
                continue
            relation = triple[0]
            id = triple[1]
            relation2id[relation] = id


    entity, norm_relation, hyper_relation, test_triple = test_data_loader("weights_and_files/entity_dim200_nbatchs20_epoch400_loss0.003410",
                                                               "weights_and_files/rel_norm_dim200_nbatchs20_epoch400_loss0.003410",
                                                               "weights_and_files/rel_hyper_dim200_nbatchs20_epoch400_loss0.003410",
                                                               "weights_and_files/test")

    recordname = "dim: 200, nbatchs: 20, batchsize: 836, epoch: 400"
    # test_triple: [id,id,id]  entity: { id: emb }
    # entity2id : { <id>: id } relation2id : { <id>: id }
    test = testTransH(entity, norm_relation, hyper_relation, test_triple)
    hit10, mean_rank = test.test_run(recordname)
    print("raw entity hits@10: ", hit10)
    print("raw entity meanrank: ",mean_rank)
