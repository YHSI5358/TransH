from unittest import result
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
import json
import time
from more_itertools import tail
from py2neo import Graph,Node,Relationship, NodeMatcher 
def index(request):
    return render(request,'web/index/temp.html')


def runcode(request):
    '''运行代码'''
    g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,    # neo4j 服务器监听的端口号
            user="neo4j",      # 数据库user name，如果没有更改过，应该是neo4j
            password="123456")
    Question = request.POST.get('Question')
    method = request.POST['method']

    if method == '1':
        from importlib import import_module
        filename = 'A_byMatch'
        find1 = import_module('static.uploads.code.'+filename)
        results,triples = find1.run(Question)
        if triples==-1:
            context = {"Question":Question,"results":results}
            return render(request,"web/index/temp.html",context)
        temp_dic = {}
        links = []
        for i in triples:
            temp_dic['source'] = i[0]
            temp_dic['target'] = i[2]
            temp_dic['rela'] = i[1]
            links.append(temp_dic)
            temp_dic = {}  

        json_data = json.dumps(links, separators=(',', ':'))
        context = {"Question":Question,"results":results,"data":json_data,"method":method}
        return render(request,"web/index/temp.html",context)
    else:
        from importlib import import_module
        filename = 'A_byTransH'
        find1 = import_module('static.uploads.code.'+filename)
        results,name_triples = find1.run(Question)
        if name_triples==-1:
            context = {"Question":Question,"results":results}
            return render(request,"web/index/temp.html",context)
        
        temp_dic = {}
        links = []
        for i in name_triples:
            temp_dic['source'] = i[0]
            temp_dic['target'] = i[2]
            temp_dic['rela'] = i[1]
            links.append(temp_dic)
            temp_dic = {}  

        json_data = json.dumps(links, separators=(',', ':'))
        context = {"Question":Question,"results":results,"data":json_data,"method":method}
        return render(request,"web/index/temp.html",context)

