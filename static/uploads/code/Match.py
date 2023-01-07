from py2neo import Graph

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            "http://localhost:7474",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            auth=("neo4j", "123456")  # 数据库user name，如果没有更改过，应该是neo4j
            )
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        web_answers = []
        attri = [
            "m.cost_money", "m.cure_department", "m.cure_lasttime", "m.cure_way", "m.cured_prob", "m.desc", 
            "m.easy_get", "m.get_prob", "m.get_way", "m.cause", "m.prevent", "m.yibao_status"
            ]
        attr_dic = {}
        attr_dic["m.cost_money"]="治疗费用"
        attr_dic["m.cure_department"]="诊断科室"
        attr_dic["m.cure_lasttime"]="治疗时长"
        attr_dic["m.cure_way"]="治疗方式"
        attr_dic["m.cured_prob"]="治愈概率"
        attr_dic["m.desc"]="描述"
        attr_dic["m.easy_get"]="易感人群"
        attr_dic["m.get_prob"]="得病概率"
        attr_dic["m.get_way"]="致病方式"
        attr_dic["m.cause"]="诱因"
        attr_dic["m.prevent"]="预防手段"
        attr_dic["m.yibao_status"]="医保政策"
        attri = set(attri)
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                ress = self.g.run(query).data()
                for i in ress:
                    if len(i.items())==3:
                        head = i['m.name']
                        relation = i['r.name']
                        tail = i['n.name']
                    else:
                        head = head = i['m.name']
                        relation = attr_dic[list(i.items())[1][0]]
                        tail = str(list(i.items())[1][1])
                        if(len(tail)>20):
                            tail = tail[0:20]
                    web_answers.append([head,relation,tail])

                answers += ress

            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers,web_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'symptom_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '症状{0}可能染上的疾病有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cause':
            desc = [i['m.cause'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可能的成因有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_prevent':
            desc = [i['m.prevent'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的预防措施包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_lasttime':
            desc = [i['m.cure_lasttime'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}治疗可能持续的周期为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cureway':
            desc = [';'.join(i['m.cure_way']) for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可以尝试如下治疗：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cureprob':
            desc = [i['m.cured_prob'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}治愈的概率为（仅供参考）：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_easyget':
            desc = [i['m.easy_get'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的易感人群包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        #新增五个属性
        elif question_type == 'disease_costmoney':
            desc = [i['m.cost_money'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的收费标准为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_getprob':
            desc = [i['m.get_prob'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}感染的概率为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_getway':
            desc = [i['m.get_way'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的感染途径为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        
        elif question_type == 'disease_curedepartment':
            desc = [i['m.cure_department'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的诊断科室为：{1}'.format(subject, '；'.join(list(set(desc[0]))[:self.num_limit]))

        elif question_type == 'disease_yibaostatus':
            desc = [i['m.yibao_status'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}能否使用医保：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_desc':
            desc = [i['m.desc'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的基本情况为：{1}'.format(subject,  '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_acompany':
            desc1 = [i['n.name'] for i in answers]
            desc2 = [i['m.name'] for i in answers]
            subject = answers[0]['m.name']
            desc = [i for i in desc1 + desc2 if i != subject]
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_not_food':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}忌食的食物包括有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_do_food':
            do_desc = [i['n.name'] for i in answers if i['r.name'] == '宜吃']
            recommand_desc = [i['n.name'] for i in answers if i['r.name'] == '推荐食谱']
            subject = answers[0]['m.name']
            final_answer = '{0}宜食的食物包括有：{1}\n推荐食谱包括有：{2}'.format(subject, ';'.join(list(set(do_desc))[:self.num_limit]), ';'.join(list(set(recommand_desc))[:self.num_limit]))

        elif question_type == 'food_not_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人最好不要吃{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'food_do_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人建议多试试{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常的使用的药品包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'drug_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}主治的疾病有{1},可以试试'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_check':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常可以通过以下方式检查出来：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'check_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '通常可以通过{0}检查出来的疾病有{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()