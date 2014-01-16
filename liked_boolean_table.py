# -*- coding: utf-8 -*-
from pandas import *
import pandas as pd
import os
import csv

"""
Created on Wed Jan 08 16:31:27 2014

@author: James Barney
"""

col_input = open('contacts_long.csv', 'r')
cols = []  #the liked pages

for row in csv.reader(col_input):
    cols.extend(row)

for string in xrange(len(cols)):
    try:
        cols[string] = int(cols[string])
    except:
        print "skipping a bad line--cannot convert to long"
        
df = pd.DataFrame.from_csv('sample500.csv', header=None)

bool_table = df.isin(cols)
bool_table.to_csv('bool_table.csv')



