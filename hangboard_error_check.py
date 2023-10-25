import datetime as dt
import pandas as pd
import numpy as np
import sys

doc = sys.argv[1]

df = pd.read_excel(doc)
df.date = pd.to_datetime(df.date)
df.date = pd.to_datetime(df.date, format='%d %b %Y')
df = df.set_index('date')

def error_check(entry, expected=6): # expected is number of total rounds
    def check_element(elem):
      entry_list = list(map(float,elem.split(',')))
      success = entry_list[1]
      fail = len(entry_list) - 2
      total = success + fail
      if total != expected:
          return True
      return False
    if ':' in entry:
        left,right = entry.split(':')
        left_res = check_element(left[2:])
        right_res = check_element(right[2:])
        return left_res or right_res
    else:
      check_element(entry)

problems = df.applymap(lambda x: error_check(x,6))
indices = problems.index.to_list()
locations = [(indices[x], problems.columns[y]) for x,y in zip(*np.where(problems.values == True))] # get "coordinates" i.e. row, column where "True" exists

if locations:
    print('Mistakes-- check these:')
    for date, hold in locations:
        print(f'{date.to_pydatetime().strftime("%d%b%Y")} : {hold}')

else:
    print('No errors found')
