#!/usr/bin/env python
# -*- coding:utf-8 -*-
import xlwt

wb = xlwt.Workbook()
sheet = wb.add_sheet('sheet1')

for row in range(10):
    for col in range(5):
        sheet.write(row, col, '第{0}行第{1}列'.format(row, col))

wb.save('xxx.xls')


# 更多示例：https://github.com/python-excel/xlwt/tree/master/examples