#-*- coding: UTF-8 -*-  
import pandas as pd
import xlrd
import csv

#读取excel文件
rowList=[]
workbook = xlrd.open_workbook('通讯录.xls')
for booksheet in workbook.sheets():
    for row in range(booksheet.nrows):
        colList=[]
        for col in range(booksheet.ncols):
            colList.append(booksheet.cell(row, col).value)
        rowList.append(colList)

#print(rowList)

#写 csv文件
with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(rowList)

#读 csv文件
with open('alldata.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        print(', '.join(row))

print('*******************************************************************************\n')
df = pd.read_csv('alldata.csv')

def city():
    '''微信朋友圈的城市'''
    address = df['city'].value_counts()
    print(address)
    
def gender():
    '''微信朋友的性别比例
        1:男  2：女   3：未知
    '''
    gender = df['male'].value_counts()
    print(gender)
    
def star():
    '''星标好友
        1:星标   0：非星标
    '''
    star = df['star'].value_counts()
    print(star)
    
def remark():
    remark = df['RemarkName']
    name = df['name']
    
    remarkCount = 0
    maleCount = 0
    femaleCount = 0
    for i in range(1,len(remark)):
        if str(remark[i]).strip() == str(name[i]).strip() or remark[i] == '  noremark  ':
            remarkCount = remarkCount + 1
        else:
            if judgeGender(i) == 'male':
                maleCount = maleCount + 1
            elif judgeGender(i) == 'female':
                femaleCount = femaleCount + 1
    print('微信总朋友人数：',str(len(remark)),'\n')
    print('预计认识的总人数：',str(len(remark)-remarkCount),'\n')
    print('认识的人中汉子人数：',maleCount,'妹子人数：',femaleCount)

def judgeGender(index):
    '''判断传入的某个位置的用户的性别
        参数：int行
        返回结果：字符串
    '''
    gender = df['gender']
    if gender[index] == '1':
        return('male')
    elif gender[index] == '2':
        return('female')
    else:
        return('unknown')

if __name__=='__main__':
    remark()