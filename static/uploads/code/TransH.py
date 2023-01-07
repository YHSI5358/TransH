from py2neo import Graph,Node,Relationship, NodeMatcher 
from tqdm import tqdm 
import torch 
import torch.optim as optim
import torch.nn.functional as F
import random
import copy
import time
import codecs
import numpy as np
from tqdm import tqdm 
import json
# from sklearn.model_selection import train_test_split

entity2id = {}
relation2id = {}


def get_entity_rel():
    g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,    # neo4j 服务器监听的端口号
            user="neo4j",      # 数据库user name，如果没有更改过，应该是neo4j
            password="123456")
    rels = []
    a = g.run("CALL db.relationshipTypes")
    for i in a:
        rels.append(i['relationshipType'])

    triples=[]
    entity_set,relation_set=set(),set()
    print("提取关系")
    for rel in tqdm(rels,ncols=80):
        b=g.run("MATCH p=(m)-[r:%s]->(n) RETURN ID(m),ID(r),ID(n)"%(rel))
        for i in list(b):
            if len(i) != 3:
                continue
            triples.append(list(i))
            entity_set.add(list(i)[0])
            entity_set.add(list(i)[2])
            relation_set.add(list(i)[1])
    entities=list(entity_set)
    relationships=list(relation_set) #<id>

    for i in range(len(entities)):
        entity2id[entities[i]] = i
    for i in range(len(relationships)):
        relation2id[relationships[i]] = i
    
    entity_no = list(range(0,len(entities)))
    relation_no = list(range(0,len(relationships)))

    
    # 划分测试集训练集
    # train, test = train_test_split(triples, test_size=0.20, random_state=2020)
    # with codecs.open("train", "w") as f2:
    #     print("写train")
    #     for triple  in tqdm(train,ncols=80):
    #         f2.write(str(triple[0]) + "\t" + str(triple[1]) + "\t" + str(triple[2]))
    #         f2.write("\n")
    # with codecs.open("test", "w") as f2:
    #     print("写test")
    #     for triple  in tqdm(test,ncols=80):
    #         f2.write(str(triple[0]) + "\t" + str(triple[1]) + "\t" + str(triple[2]))
    #         f2.write("\n")
    # 写出所有关系和实体(真实<id>)
    # with codecs.open("pairs", "w") as f2:
    #     print("写pairs")
    #     for triple  in tqdm(triples,ncols=80):
    #         f2.write(str(triple[0]) + "\t" + str(triple[1]) + "\t" + str(triple[2]))
    #         f2.write("\n")


    triple_list = []
    for triple in triples:
        h_ = entity2id[triple[0]]
        r_ = relation2id[triple[1]]
        t_ = entity2id[triple[2]]
        triple_list.append([h_,r_,t_])


    print("Complete load. entity : %d , relation : %d , triple : %d" % (
        len(entity_no), len(relation_no), len(triple_list)))
    return entity_no, relation_no, triple_list

class TransH():
    def __init__(self, entity_set, relation_set, triple_list, embedding_dim = 50, lr = 0.01, margin = 1.0, C = 1.0):
        self.entities = entity_set#{id:emb}
        self.relations = relation_set#{id:emb}
        self.triples = triple_list#[id,id,id]
        self.dimension = embedding_dim
        self.learning_rate = lr
        self.margin = margin
        self.loss = 0.0
        self.norm_relations = {}
        self.hyper_relations = {}#{id:emb}
        self.C = C
    def data_initialise(self, continue_trian = 0, entity_name = "None", rel_hyper_name = "None", rel_norm_name = "None"):
        if continue_trian == 0:
            entityVectorList = {}
            relationNormVectorList = {}
            relationHyperVectorList = {}

            for entity in self.entities:
                entity_vector = torch.Tensor(self.dimension).uniform_(-6.0 / np.sqrt(self.dimension), 6.0 / np.sqrt(self.dimension))
                entityVectorList[entity] = entity_vector.requires_grad_(True)

            for relation in self.relations:
                relation_norm_vector = torch.Tensor(self.dimension).uniform_(-6.0 / np.sqrt(self.dimension), 6.0 / np.sqrt(self.dimension))
                relation_hyper_vector = torch.Tensor(self.dimension).uniform_(-6.0 / np.sqrt(self.dimension), 6.0 / np.sqrt(self.dimension))

                relationNormVectorList[relation] = relation_norm_vector.requires_grad_(True)
                relationHyperVectorList[relation] = relation_hyper_vector.requires_grad_(True)

            self.entities = entityVectorList#{id:emb}
            self.norm_relations = relationNormVectorList
            self.hyper_relations = relationHyperVectorList
        else:
            entity_dic = {}
            rel_hyper_dic = {}
            rel_norm_dic = {}
            with codecs.open(entity_name, 'r') as f1, codecs.open(rel_hyper_name, 'r') as f2, codecs.open(rel_norm_name, 'r') as f3:
                content1 = f1.readlines()
                content2 = f2.readlines()
                content3 = f3.readlines()
                for line in content1:
                    line = line.strip().split("\t")
                    if len(line) != 2:
                        continue
                    entity_dic[int(line[0])] = torch.Tensor(json.loads(line[1])).requires_grad_(True)
                for line in content2:
                    line = line.strip().split("\t")
                    if len(line) != 2:
                        continue
                    rel_hyper_dic[int(line[0])] = torch.Tensor(json.loads(line[1])).requires_grad_(True)
                for line in content3:
                    line = line.strip().split("\t")
                    if len(line) != 2:
                        continue
                    rel_norm_dic[int(line[0])] = torch.Tensor(json.loads(line[1])).requires_grad_(True)
            self.entities = entity_dic
            self.norm_relations = rel_norm_dic
            self.hyper_relations = rel_hyper_dic
                    
            

    def training_run(self, epochs=100, times = 2 ,nbatches = 50):
        batch_size = int(len(self.triples) / nbatches)
        print("batch size: ", batch_size)
        for epoch in range(epochs):
            start = time.time()
            self.loss = 0.0

            for batch in tqdm(range(nbatches),ncols=80):
                batch_samples = random.sample(self.triples, batch_size)#[id,id,id]
                Tbatch = []
                for sample in batch_samples:
                    corrupted_sample = copy.deepcopy(sample)
                    seed = random.random()
                    if seed < 0.5:
                        # 更改头节点
                        corrupted_sample[0] = random.sample(self.entities.keys(), 1)[0]
                        while corrupted_sample[0] == sample[0]:
                            corrupted_sample[0] = random.sample(self.entities.keys(), 1)[0]
                    else:
                        # 更改尾节点
                        corrupted_sample[2] = random.sample(self.entities.keys(), 1)[0]
                        while corrupted_sample[2] == sample[2]:
                            corrupted_sample[2] = random.sample(self.entities.keys(), 1)[0]

                    if (sample, corrupted_sample) not in Tbatch:
                        Tbatch.append((sample, corrupted_sample))

                self.update_triple_embedding(Tbatch)
            end = time.time()
            print("epoch: ", epoch, "cost time: %s" % (round((end - start), 3)))
            print("running loss: ", self.loss/len(self.triples))

        with codecs.open("weights_and_files/entity_dim" + str(self.dimension) + "_nbatchs" + str(nbatches) + "_epoch" + str(epochs*times) + "_loss"+ str(self.loss/len(self.triples))[0:8], "w") as f1:
            print("写f1")
            for e in tqdm(self.entities,ncols=80):
                f1.write(str(e) + "\t")
                f1.write(str(list(self.entities[e].detach().numpy())))
                f1.write("\n")

        with codecs.open("weights_and_files/rel_norm_dim" + str(self.dimension) + "_nbatchs" + str(nbatches) + "_epoch" + str(epochs*times) + "_loss"+ str(self.loss/len(self.triples))[0:8], "w") as f2:
            print("写f2")
            for r in tqdm(self.norm_relations,ncols=80):
                f2.write(str(r) + "\t")
                f2.write(str(list(self.norm_relations[r].detach().numpy())))
                f2.write("\n")

        with codecs.open("weights_and_files/rel_hyper_dim" + str(self.dimension) + "_nbatchs" + str(nbatches) + "_epoch" + str(epochs*times) + "_loss"+ str(self.loss/len(self.triples))[0:8], "w") as f3:
            print("写f3")
            for r in tqdm(self.hyper_relations,ncols=80):
                f3.write(str(r) + "\t")
                f3.write(str(list(self.hyper_relations[r].detach().numpy())))
                f3.write("\n")


    def norm_l2(self, h, r_norm, r_hyper, t):
        return torch.norm(h - r_norm.dot(h)*r_norm + r_hyper -(t - r_norm.dot(t)*r_norm))

    # loss = F.relu(self.margin + correct_distance - corrupted_distance) + self.C * scale
    # 模长约束
    # def scale_entity(self, vector):
    #     return torch.relu(torch.sum(vector**2) - 1)

    def update_triple_embedding(self, Tbatch):

        for correct_sample, corrupted_sample in Tbatch:
            correct_head = self.entities[correct_sample[0]]#entities:{id:emb}
            correct_tail  = self.entities[correct_sample[2]]
            relation_norm = self.norm_relations[correct_sample[1]]
            relation_hyper = self.hyper_relations[correct_sample[1]]

            corrupted_head = self.entities[corrupted_sample[0]]
            corrupted_tail = self.entities[corrupted_sample[2]]

            opt1 = optim.SGD([correct_head], lr=self.learning_rate)
            opt2 = optim.SGD([correct_tail], lr=self.learning_rate)
            opt3 = optim.SGD([relation_norm], lr=self.learning_rate)
            opt4 = optim.SGD([relation_hyper], lr=self.learning_rate)

            if correct_sample[0] == corrupted_sample[0]:
                opt5 = optim.SGD([corrupted_tail], lr=self.learning_rate)
                correct_distance = self.norm_l2(correct_head, relation_norm, relation_hyper, correct_tail)
                corrupted_distance = self.norm_l2(correct_head, relation_norm, relation_hyper, corrupted_tail)
                scale = self.scale_entity(correct_head) + self.scale_entity(correct_tail) + self.scale_entity(corrupted_tail)

            else:
                opt5 = optim.SGD([corrupted_head], lr=self.learning_rate)
                correct_distance = self.norm_l2(correct_head, relation_norm, relation_hyper, correct_tail)
                corrupted_distance = self.norm_l2(corrupted_head, relation_norm, relation_hyper, correct_tail)
                scale = self.scale_entity(correct_head) + self.scale_entity(correct_tail) + self.scale_entity(
                    corrupted_head)

            opt1.zero_grad()
            opt2.zero_grad()
            opt3.zero_grad()
            opt4.zero_grad()
            opt5.zero_grad()

            loss = F.relu(self.margin + correct_distance - corrupted_distance)
            loss.backward()
            self.loss += loss.item()
            opt1.step()
            opt2.step()
            opt3.step()
            opt4.step()
            opt5.step()


            self.entities[correct_sample[0]] = correct_head #
            self.entities[correct_sample[2]] = correct_tail
            if correct_sample[0] == corrupted_sample[0]:
                self.entities[corrupted_sample[2]] = corrupted_tail
            elif correct_sample[2] == corrupted_sample[2]:
                self.entities[corrupted_sample[0]] = corrupted_head
            self.norm_relations[correct_sample[1]] = relation_norm
            self.hyper_relations[correct_sample[1]] = relation_hyper


if __name__ == '__main__':
    entity_set, relation_set, triple_list = get_entity_rel()
 
    transH = TransH(entity_set, relation_set, triple_list, embedding_dim=200, lr=0.01, margin=1.0)
    #continue_train表示是否从之前的训练模型继续训练，后面是文件名称
    transH.data_initialise(continue_trian = 1, 
                            entity_name = "weights_and_files/entity_dim200_nbatchs20_epoch400_loss0.003410", 
                            rel_hyper_name = "weights_and_files/rel_hyper_dim200_nbatchs20_epoch400_loss0.003410", 
                            rel_norm_name = "weights_and_files/rel_norm_dim200_nbatchs20_epoch400_loss0.003410")
    transH.training_run(epochs=100,times=5,nbatches=100)#times表示第几次训练，跟最后生成的参数文件名有关
    
    

    # 下面这部分代码是生成relation2id和entity2id的，如果neo4j重新导入过，这个要执行一边
    # with codecs.open("relation2id", "w") as f2:
    #     print("写relation2id")
    #     for item  in tqdm(relation2id.items(),ncols=80):
    #         f2.write(str(item[0]) + "\t" + str(item[1]))
    #         f2.write("\n")
    # with codecs.open("entity2id", "w") as f2:
    #     print("写entity2id")
    #     for item  in tqdm(entity2id.items(),ncols=80):
    #         f2.write(str(item[0]) + "\t" + str(item[1]))
    #         f2.write("\n")
