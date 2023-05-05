import pandas as pd
import os
import numpy as np
from tqdm import tqdm
import csv

#————————————在这里输入路径信息并划分比例————————————————
# image_file = input('输入图片所在文件夹的绝对路径：')
image_file = 'D:\DS\JPEGImages\image'
# frac = input('输入ava格式下验证集所占比例：')
frac = 0.1
# ac = input('输入ava格式下的精确率：')
ac = 0.9
# .csv-->.xml
# 在这里输入模块一数据集构建好的input.csv原文件
file_path = r'D:\DS\csv\input.csv'
# xml保存的位置
save_xml_dir = r'D:\DS\annotation\xml/'

#——————————————————————————————————————————————————————————————————————————
#记录图片大小
width = 1280
height = 720
#去掉表头汉字：采取'gb18030'编码
with open(file_path,encoding='utf-8-sig') as csvfile:
    # 读取csv数据
    csv_reader = csv.reader(csvfile)
    # 去掉第一行(第一行是列名)
    csv_header = next(csv_reader)
    # 因为csv数据中有许多行其实是同一个照片，因此需要pre_img
    pre_img = ''  # 存储前一张图像的名称
    for row in csv_reader:
        # 只要文件名
        img = row[0]+'_'+row[1]
        # 遇到的是一张新图片
        if img != pre_img:
            # 非第一张图片,在上一个xml中写下</annotation>
            if pre_img != '':
                xml_file1 = open((save_xml_dir + pre_img + '.xml'), 'a',encoding='utf-8')
                xml_file1.write('</annotation>')
                xml_file1.close()

            # 新建xml文件
            xml_file = open((save_xml_dir + img + '.xml'), 'w',encoding='utf-8')
            xml_file.write('<annotation>\n')
            xml_file.write('        <folder>VOC2007</folder>\n')
            xml_file.write('        <filename>' + str(img) + '.jpg' + '</filename>\n')
            xml_file.write('<source>\n')
            xml_file.write('        <database> Unknown </database>\n')
            xml_file.write('</source>\n')
            xml_file.write('<size>\n')
            xml_file.write('        <width>' + str(width) + '</width>\n')
            xml_file.write('        <height>' + str(height) + '</height>\n')
            xml_file.write('        <depth>3</depth>\n')
            xml_file.write('</size>\n')
            xml_file.write('<segmented>0</segmented>\n')
            xml_file.write('<object>\n')
            xml_file.write('        <name>' + str(row[-1]) + '</name>\n')
            xml_file.write('        <pose>Unspecified</pose>\n')
            xml_file.write('        <truncated>0</truncated>\n')
            xml_file.write('        <difficult>0</difficult>\n')
            xml_file.write('        <bndbox>\n')
            xml_file.write('            <xmin>' + str(row[2]) + '</xmin>\n')
            xml_file.write('            <ymin>' + str(row[3]) + '</ymin>\n')
            xml_file.write('            <xmax>' + str(row[4]) + '</xmax>\n')
            xml_file.write('            <ymax>' + str(row[5]) + '</ymax>\n')
            xml_file.write('        </bndbox>\n')
            xml_file.write('</object>\n')
            xml_file.close()
            pre_img = img
        else:
            # 同一张图片，只需要追加写入object
            xml_file = open((save_xml_dir + pre_img + '.xml'), 'a',encoding='utf-8')
            xml_file.write('<object>\n')
            xml_file.write('        <name>' + str(row[-1]) + '</name>\n')
            xml_file.write('        <pose>Unspecified</pose>\n')
            xml_file.write('        <truncated>0</truncated>\n')
            xml_file.write('        <difficult>0</difficult>\n')
            xml_file.write('        <bndbox>\n')
            xml_file.write('            <xmin>' + str(row[2]) + '</xmin>\n')
            xml_file.write('            <ymin>' + str(row[3]) + '</ymin>\n')
            xml_file.write('            <xmax>' + str(row[4]) + '</xmax>\n')
            xml_file.write('            <ymax>' + str(row[5]) + '</ymax>\n')
            xml_file.write('        </bndbox>\n')
            xml_file.write('</object>\n')
            xml_file.close()
            pre_img = img
# csv表格最后一个xml需要写入</annotation>
xml_file1 = open((save_xml_dir + pre_img + '.xml'), 'a',encoding='utf-8')
xml_file1.write('</annotation>')
xml_file1.close()


df = pd.read_csv(file_path)
df['x1'] /= width
df['y1'] /= height
df['x2'] /= width
df['y2'] /= height
df = df.sort_values('frame_id')
# print('annotations/train.csv:\n', df.head())
df = df.fillna(0)
df['frame_id'] = df['frame_id'].astype(np.int32)
df['action_id'] = df['action_id'].astype(np.int32)
df = df.sort_values('frame_id')
#——————在这里输入您的annotations/train.csv路径————————
df.to_csv('annotations/train.csv', index=False, header=False)
sdf = df.sample(frac=frac).sort_values('frame_id')
# print('annotations/val.csv: \n', sdf.head())
#——————在这里输入您的annotations/val.csv路径————————
sdf.to_csv('annotations/val.csv', index=False, header=False)


df = df.drop(['person_id'], axis=1)
df['ac'] = [ac] * df.shape[0]
# print('annotations/dtrain.csv: \n', df.head())
# df.to_csv('annotations/dtrain.csv', index=False, header=False)


sdf = sdf.drop(['person_id', 'action_id'], axis=1)
sdf['blank'] = [''] * sdf.shape[0]
sdf['ac'] = [ac] * sdf.shape[0]
# print('annotations/tval.csv: \n', sdf.head())
#——————在这里输入您的annotations/tval.csv路径————————
sdf.to_csv('annotations/tval.csv', index=False, header=False)

df = pd.DataFrame()
# pathDir = os.listdir('frame')
pathDir = os.listdir('D:\DS\JPEGImages\image1')
path, original_video_id, video_id, frame_id = [], [], [], []
for x in pathDir:
    original_video_id.append(x.split('_')[0])
    video_id.append(x.split('_')[0])
    frame_id.append(x.split('_')[1].split('.')[0])
    path.append(os.path.join('%s' % x))
df['original_video_id'] = original_video_id
df['video_id'] = video_id
df['frame_id'] = frame_id
df['frame_id'] = df['frame_id'].astype(np.int32)
df['path'] = path
df['labels'] = ['']*len(path)
df = df.sort_values('frame_id')
# print('frame_list/train.csv: \n', df.head())
#——————在这里输入您的frame_list/train.csv路径————————
df.to_csv('frame_list/train.csv', index=False, header=False)

df = df.loc[df.frame_id.isin(sdf.frame_id)]
# print('frame_list/val.csv: \n', df.head())
#——————在这里输入您的frame_list/val.csv路径————————
df.to_csv('frame_list/val.csv', index=False, header=False)

print('xml has been generated')
print('ava has been generated')