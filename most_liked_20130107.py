from pandas import *
import pandas as pd
import os
import csv

"""
Generating the list of most popular pages, with lower bound at 10% of likes
of most popular page

Last modified: 1/8/13, James Barney

"""

#os.chdir('L:\\Analytics_Share\\Team_Internal\\Analysis\\Thailand\\2014')

likes = pd.read_csv('contacts_long.csv',names=['page'])
likes = likes.ix[:,0]
pop = likes.value_counts()

print pop.index[0:5]

pop =  pop[pop>(pop.max()/10)]
pages = pd.DataFrame(pop.index,columns=['pageid'])
pages['likes'] = pop.values
print pages.to_string()

inPut = open('sample500.csv', 'rb')
reader = csv.reader(inPut, delimiter=',')

