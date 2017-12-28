#!/usr/bin/env python
# -*- coding:utf-8 -*-
import xlrd
from xlrd.book import Book
from xlrd.sheet import Sheet
from xlrd.sheet import Cell

workbook = xlrd.open_workbook('基础课程大纲.xlsx')

sheet_names = workbook.sheet_names()

# sheet = workbook.sheet_by_name('工作表1')
sheet = workbook.sheet_by_index(1)

# 循环Excel文件的所有行
for row in sheet.get_rows():
    # 循环一行的所有列
    for col in row:
        # 获取一个单元格中的值
        print(col.value)
