from static.uploads.code.Q_Class import *
from static.uploads.code.TransH import *
from py2neo import Graph
import codecs

entity_vector, relation_vector, relation_hyper = {}, {}, {}
entity2id, relation2id = {}, {}
id2entity = {}


class reason:
    def __init__(self):
        self.g = Graph(
            "http://localhost:7474",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            auth=("neo4j", "123456")  # 数据库user name，如果没有更改过，应该是neo4j
        )
        self.question_classifier = QuestionClassifier()
        self.readfile()

    def readfile(self):
        file1 = "./static/uploads/code/weights_and_files/entity2id"
        file2 = "./static/uploads/code/weights_and_files/relation2id"
        file3 = "./static/uploads/code/weights_and_files/entity_dim200_nbatchs20_epoch400_loss0.003410"
        file4 = "./static/uploads/code/weights_and_files/rel_norm_dim200_nbatchs20_epoch400_loss0.003410"
        file5 = "./static/uploads/code/weights_and_files/rel_hyper_dim200_nbatchs20_epoch400_loss0.003410"
        with codecs.open(file1, 'r') as f1, codecs.open(file2, 'r') as f2 :
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            for line in lines1:
                line = line.strip().split('\t')
                if len(line) != 2:
                    continue
                entity2id[line[0]] = json.loads(line[1])
                id2entity[line[1]] = json.loads(line[0])
            for line in lines2:
                line = line.strip().split('\t')
                if len(line) != 2:
                    continue
                relation2id[line[0]] = json.loads(line[1])

        with codecs.open(file3, 'r') as f1, codecs.open(file4, 'r') as f2, codecs.open(file5, 'r') as f3:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            lines3 = f3.readlines()
            for line in lines1:
                line = line.strip().split('\t')
                if len(line) != 2:
                    continue
                entity_vector[line[0]] = json.loads(line[1])

            for line in lines2:
                line = line.strip().split('\t')
                if len(line) != 2:
                    continue
                relation_vector[line[0]] = json.loads(line[1])

            for line in lines3:
                line = line.strip().split('\t')
                if len(line) != 2:
                    continue
                relation_hyper[line[0]] = json.loads(line[1])


    def get_id(self, question):
        data = self.question_classifier.classify(question)

        if 'args' in data:
            args = data['args']
        else:
            return -1,-1
        
        entity_dict = {}
        for arg, types in args.items():
            for _type in types:
                if _type not in entity_dict:
                    entity_dict[_type] = [arg]
                else:
                    entity_dict[_type].append(arg)
        question_types = data['question_types']
        for question_type in question_types:
            if (question_type == 'disease_cause' or 
                question_type == 'disease_prevent' or
                question_type == 'disease_lasttime' or
                question_type == 'disease_cureprob' or
                question_type == 'disease_cureway' or
                question_type == 'disease_easyget' or 
                question_type == 'disease_costmoney' or
                question_type == 'disease_getprob' or
                question_type == 'disease_getway' or
                question_type == 'disease_yibaostatus' or
                question_type == 'disease_desc' ):
                return -1,-1

            # 查询疾病有哪些症状
            elif question_type == 'disease_symptom':
                relation_sql = [
                    "MATCH (m:疾病)-[r:has_symptom]->(n:症状) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

            # 查询症状会导致哪些疾病
            elif question_type == 'symptom_disease':
                relation_sql = [
                    "MATCH (m:疾病)-[r:has_symptom]->(n:症状) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

            # 查询疾病的并发症
            elif question_type == 'disease_acompany':
                sql1 = [
                    "MATCH (m:疾病)-[r:acompany_with]->(n:疾病) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                sql2 = [
                    "MATCH (m:疾病)-[r:acompany_with]->(n:疾病) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                relation_sql = sql1 + sql2
            # 查询疾病的忌口
            elif question_type == 'disease_not_food':
                relation_sql = [
                    "MATCH (m:疾病)-[r:no_eat]->(n:食物) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

            # 查询疾病建议吃的东西
            elif question_type == 'disease_do_food':
                sql1 = [
                    "MATCH (m:疾病)-[r:do_eat]->(n:食物) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                sql2 = [
                    "MATCH (m:疾病)-[r:recommand_eat]->(n:食物) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                relation_sql = sql1 + sql2

            # 已知忌口查疾病
            elif question_type == 'food_not_disease':
                relation_sql = [
                    "MATCH (m:疾病)-[r:no_eat]->(n:食物) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

            # 已知推荐查疾病
            elif question_type == 'food_do_disease':
                sql1 = [
                    "MATCH (m:疾病)-[r:do_eat]->(n:食物) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                sql2 = [
                    "MATCH (m:疾病)-[r:recommand_eat]->(n:食物) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                relation_sql = sql1 + sql2

            # 查询疾病常用药品－药品别名记得扩充
            elif question_type == 'disease_drug':
                sql1 = [
                    "MATCH (m:疾病)-[r:common_drug]->(n:药品) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                sql2 = [
                    "MATCH (m:疾病)-[r:recommand_drug]->(n:药品) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                relation_sql = sql1 + sql2

            # 已知药品查询能够治疗的疾病
            elif question_type == 'drug_disease':
                sql1 = [
                    "MATCH (m:疾病)-[r:common_drug]->(n:药品) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                sql2 = [
                    "MATCH (m:疾病)-[r:recommand_drug]->(n:药品) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]
                relation_sql = sql1 + sql2

            # 查询疾病应该进行的检查
            elif question_type == 'disease_check':
                relation_sql = [
                    "MATCH (m:疾病)-[r:need_check]->(n:检查) where m.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

            # 已知检查查询疾病
            elif question_type == 'check_disease':
                relation_sql = [
                    "MATCH (m:疾病)-[r:need_check]->(n:检查) where n.name = '{0}' return id(r)".format(i[0]) for i in entity_dict.values()]

        entity_sql = ["MATCH (m) where m.name = '{0}' return id(m) LIMIT 1".format(i[0]) for i in entity_dict.values()]

        entity_id = self.g.run(entity_sql[0]).data()
        relation_id = self.g.run(relation_sql[0]).data()

        return entity_id, relation_id

    def process_get_answer(self, entityID, relationID):
        results = []
        tail_ids = []
        for i in entityID:
            for j in relationID:
                result,tail_id = self.get_answer(i,j)
                if(result != -1):
                    results.append(result)
                    tail_ids.append(tail_id)
        return results,tail_ids

    def get_answer(self, entityId, relationId):
        r = relation_vector[relationId]
        norm = np.array(r)
        r_hyper = relation_hyper[relationId]
        hyper = np.array(r_hyper)
        head = np.array(entity_vector[entityId])

        Two_tuple = {}
        for i in range(len(entity_vector)):
            if i == int(entityId):
                continue
            t = entity_vector[str(i)]
            Two_tuple[str(i)] = self.distance(head, norm, hyper, t)
        tail = 0
        two_tuple = sorted(Two_tuple.items(), key=lambda x: x[1])

        tail = id2entity[str(two_tuple[0][0])]

        print(tail)
        sql = ["MATCH (n) where id(n) = {0} return n.name".format(tail)]
        result = self.g.run(sql[0]).data()
        if(len(list(result))==0):
            result = -1
        else:
            result = list(result[0].values())[0]
        return result ,tail



    def distance(self, h, r_norm, r_hyper, t):
        head = np.array(h)
        norm = np.array(r_norm)
        hyper = np.array(r_hyper)
        tail = np.array(t)
        h_hyper = head - np.dot(norm, head) * norm
        t_hyper = tail - np.dot(norm, tail) * norm
        d = h_hyper + hyper - t_hyper
        return np.sum(np.square(d))


def run(question):
    Reason = reason()
    questions = question.split()
    results = []
    triple_ids_list = []
    for question in questions:
        temp_entity, temp_relation = Reason.get_id(question)
        if temp_entity == -1:
            result = ["未找到相关信息。"]
            return result,-1
        entity = []
        relation = []
        for i in temp_entity:
            entity.append(list(i.values())[0])
        for i in temp_relation:
            relation.append(list(i.values())[0])

        entityid = []
        relationid = []
        for i in entity:
            entityid.append(str(entity2id[str(i)]))
        for i in relation:
            relationid.append(str(relation2id[str(i)]))
        result,tail = Reason.process_get_answer(entityid, relationid)
        triple_ids = []
        for i in entity:
            for j in relation:
                for k in tail:
                    triple_ids.append([i,j,k])
        name_triples = []
        for i in triple_ids:
            head_name = Reason.g.run("MATCH (h) WHERE ID(h)=%s  RETURN h.name"%(str(i[0]))).data()[0]['h.name']
            rel_name = Reason.g.run("match (x)-[r]-(y) where id(r)=%s return r.name"%(str(i[1]))).data()[0]['r.name']
            tail_name = Reason.g.run("MATCH (t) WHERE ID(t)=%s  RETURN t.name"%(str(i[2]))).data()[0]['t.name']
            if len(tail_name)>20:
                tail_name = tail_name[0:10]
            name_triples.append([head_name,rel_name,tail_name])
        for i in result:
            results.append(i)
        for i in name_triples:
            triple_ids_list.append(i)

    return results,triple_ids_list
