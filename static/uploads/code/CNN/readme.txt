1.文件结构：
models:存有各种模型（TextCNN,TextRNN等）
THUCNews:存放数据
run.py:运行文件
train_eval.py:训练文件
utils:读取数据
2.环境：
pytroch1.0以上版本，tensorboardX。文件路径如有问题可根据报错找到位置修改为绝对路径。
2.运行方式：
运行run.py,注意后面要加上模式，如：python run.py --model TextCNN