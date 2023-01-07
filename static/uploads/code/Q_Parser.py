class QuestionParser:

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'disease_symptom':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'symptom_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('symptom'))

            elif question_type == 'disease_cause':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_acompany':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_not_food':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_do_food':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'food_not_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('food'))

            elif question_type == 'food_do_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('food'))

            elif question_type == 'disease_drug':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'drug_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('drug'))

            elif question_type == 'disease_check':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'check_disease':
                sql = self.sql_transfer(question_type, entity_dict.get('check'))

            elif question_type == 'disease_prevent':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_lasttime':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_cureway':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_cureprob':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_easyget':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            # 新增四个属性
            elif question_type == 'disease_costmoney':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_getprob':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_getway':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_yibaostatus':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_desc':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            elif question_type == 'disease_curedepartment':
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询疾病的原因
        if question_type == 'disease_cause':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cause".format(i) for i in entities]

        # 查询疾病的科室
        elif question_type == 'disease_curedepartment':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cure_department".format(i) for i in entities]

        # 查询疾病的防御措施
        elif question_type == 'disease_prevent':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.prevent".format(i) for i in entities]

        # 查询疾病的持续时间
        elif question_type == 'disease_lasttime':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cure_lasttime".format(i) for i in entities]

        # 查询疾病的治愈概率
        elif question_type == 'disease_cureprob':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cured_prob".format(i) for i in entities]

        # 查询疾病的治疗方式
        elif question_type == 'disease_cureway':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cure_way".format(i) for i in entities]

        # 查询疾病的易发人群
        elif question_type == 'disease_easyget':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.easy_get".format(i) for i in entities]

        # 新增四个属性的查找
        # 查询疾病的收费标准
        elif question_type == 'disease_costmoney':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.cost_money".format(i) for i in entities]

        # 查询疾病的患病概率
        elif question_type == 'disease_getprob':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.get_prob".format(i) for i in entities]

        # 查询疾病的传播途径
        elif question_type == 'disease_getway':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.get_way".format(i) for i in entities]

        # 查询疾病的医保状态
        elif question_type == 'disease_yibaostatus':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.yibao_status".format(i) for i in entities]

        # 查询疾病的相关介绍
        elif question_type == 'disease_desc':
            sql = ["MATCH (m:`疾病`) where m.name = '{0}' return m.name, m.desc".format(i) for i in entities]

        # 查询疾病有哪些症状
        elif question_type == 'disease_symptom':
            sql = ["MATCH (m:`疾病`)-[r:has_symptom]->(n:`症状`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询症状会导致哪些疾病
        elif question_type == 'symptom_disease':
            sql = ["MATCH (m:`疾病`)-[r:has_symptom]->(n:`症状`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询疾病的并发症
        elif question_type == 'disease_acompany':
            sql1 = ["MATCH (m:`疾病`)-[r:acompany_with]->(n:`疾病`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (m:`疾病`)-[r:acompany_with]->(n:`疾病`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2
        # 查询疾病的忌口
        elif question_type == 'disease_not_food':
            sql = ["MATCH (m:`疾病`)-[r:no_eat]->(n:`食物`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询疾病建议吃的东西
        elif question_type == 'disease_do_food':
            sql1 = ["MATCH (m:`疾病`)-[r:do_eat]->(n:`食物`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (m:`疾病`)-[r:recommand_eat]->(n:`食物`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2

        # 已知忌口查疾病
        elif question_type == 'food_not_disease':
            sql = ["MATCH (m:`疾病`)-[r:no_eat]->(n:`食物`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 已知推荐查疾病
        elif question_type == 'food_do_disease':
            sql1 = ["MATCH (m:`疾病`)-[r:do_eat]->(n:`食物`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (m:`疾病`)-[r:recommand_eat]->(n:`食物`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2

        # 查询疾病常用药品－药品别名记得扩充
        elif question_type == 'disease_drug':
            sql1 = ["MATCH (m:`疾病`)-[r:common_drug]->(n:`药品`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (m:`疾病`)-[r:recommand_drug]->(n:`药品`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2

        # 已知药品查询能够治疗的疾病
        elif question_type == 'drug_disease':
            sql1 = ["MATCH (m:`疾病`)-[r:common_drug]->(n:`药品`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql2 = ["MATCH (m:`疾病`)-[r:recommand_drug]->(n:`药品`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
            sql = sql1 + sql2
        # 查询疾病应该进行的检查
        elif question_type == 'disease_check':
            sql = ["MATCH (m:`疾病`)-[r:need_check]->(n:`检查`) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 已知检查查询疾病
        elif question_type == 'check_disease':
            sql = ["MATCH (m:`疾病`)-[r:need_check]->(n:`检查`) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        return sql



if __name__ == '__main__':
    handler = QuestionParser()
