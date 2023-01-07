from static.uploads.code.Q_Class import *
from static.uploads.code.Q_Parser import *
from static.uploads.code.Match import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = ['未找到相关信息。']
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer,-1
        res_sql = self.parser.parser_main(res_classify)

        final_answers,web_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer,-1
        else:
            return final_answers,web_answers

def run(question):
    handler = ChatBotGraph()
    questions = question.split()
    answers = []
    web_answers = []
    for question in questions:
        answer,web_answer = handler.chat_main(question)

        for ans in answer:
            answers.append(ans)
        
        for web in web_answer:
            web_answers.append(web)
    return answers,web_answers

