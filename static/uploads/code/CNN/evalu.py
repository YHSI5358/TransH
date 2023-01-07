import time
import torch
import numpy as np
from train_eval import train, init_network
from importlib import import_module
import argparse
from tensorboardX import SummaryWriter
import os
def evaluate2(config,model,data_iter,test=False):
    model.eval()
    
    with torch.no_grad():
        outputs=model(text)
        labels=labels.data.cpu().numpy()
        predic=torch.max(outputs.data,1)[1].cpu.numpy()
    print(predic)
parser = argparse.ArgumentParser(description='Chinese Text Classification')
parser.add_argument('--model', type=str, required=True, help='choose a model: TextCNN, TextRNN, FastText, TextRCNN, TextRNN_Att, DPCNN, Transformer')
args = parser.parse_args()
model_name = args.model
x = import_module('models.' + model_name)
dataset = 'THUCNews'  # 数据集

    # 搜狗新闻:embedding_SougouNews.npz, 腾讯:embedding_Tencent.npz, 随机初始化:random
embedding = 'embedding_SougouNews.npz'
config = x.Config(dataset, embedding)
model = x.Model(config).to(config.device)
text=input()
evaluate2(config,model,text)