import pandas as pd
import numpy as np
from math import floor, ceil
from datetime import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

class Pyramid:
  def __init__(self,document,sub_location=None):
    """ 
    document: url (from mountain project of csv)
    sub_location: default to "all". Otherwise pass list starting from state. eg.: ['California', 'Joshua Tree National Park'] 
    """
    self.document = document
    self.sub_location = sub_location
    self.climber = document.split('/')[-2].replace('-',' ').title()
    self.grade_chart = pd.read_html("https://www.mountainproject.com/international-climbing-grades")
    old_ropes = self.grade_chart[0].YDSUSA[:-1].to_list()
    new_ropes = [0,0,0,0,1,2,3,4,5,6,7,7.4,8,8.4,8.8,9,9.4,9.8]+list(np.round(np.arange(10,16,.1),1))
    self.ropes_convert = dict(zip(old_ropes, new_ropes))
    old_boulder = self.grade_chart[1].HuecoUSA[:-1]
    new_boulder = np.insert(np.arange(0,17.5,.25),0,[-1])
    self.boulder_convert = dict(zip(old_boulder,new_boulder))
   
    self.data = self._clean_data(self.document)
    if sub_location:
      self.data = self.data[self.data.location.apply(lambda x: all(item in x for item in sub_location))]
    else:  # for use in the title
      self.sub_location = ['All locations']

    all_types = self.data['type'].unique()
    trad_types = [t for t in all_types if 'Trad' in t]
    sport_types = [t for t in all_types if 'Sport' in t and 'Trad' not in t]
    boulder_types = [t for t in all_types if 'Boulder' in t and 'Trad' not in t and 'Sport' not in t]

    self.style_options = {}
    if trad_types:
      self.style_options['trad'] = trad_types
    if sport_types:
      self.style_options['sport'] = sport_types
    if boulder_types:
      self.style_options['boulder'] = boulder_types


  def make_pyramid(self, type_and_style=(None, None)):
    # Split Trad and Sport data
    self.pyramid_styles = type_and_style[0]
    self.lead_styles = type_and_style[1]

    if not self.pyramid_styles:
      self.pyramid_styles = [list(self.style_options.keys())[0]]
    if not self.lead_styles:
      self.lead_styles = self.data[self.data['type'].isin(np.array([self.style_options[p] for p in self.pyramid_styles]).flatten())].lead_style.unique() # maybe return this for allowed 
    self.styles = {}
    for p in self.pyramid_styles:
      try:
        self.styles[p] = self.data[(self.data['type'].isin(self.style_options[p])) & (self.data['lead_style'].isin(self.lead_styles))]
      except KeyError:
        pass

    self.boulder = 0
    if self.pyramid_styles[0] == 'boulder':  # pass into _grade_to_letter
      self.boulder = 1

    self.pyramids = {}
    self.titles = {}
    for key,style in self.styles.items():   # likely unnecessary going forward, perhaps split boulders from routes
      if not style.empty:
        top_pyramid = style
        top_pyramid.grade = style.grade.apply(self._x_round)
        top_grades = top_pyramid.grade.unique()
        top_grades.sort()
        top_pyramid.grade = top_pyramid.grade.apply(self._grade_to_letter,boulder=self.boulder)
        self.pyramids[key] = top_pyramid

    perms = ('1 2 3 4 5 6 7 8 9'.split(), ['-','','+'])
    self.grades_list = [a+b for a in perms[0] for b in perms[1]]
    self.numbs = '10 11 12 13 14 15'.split()
    self.letters =  list('abcd')
    for i in self.numbs:
      for j in self.letters:
        self.grades_list.append(i+j)
    self.boulder_grades = ['V'+str(n) for n in ['-easy']+list(range(17))]


  def _sum_miles(self, length_data):
    min_date = length_data.Date.min().year
    max_date = length_data.Date.max().year + 1
    front_dates = list(range(min_date,max_date))
    back_dates = [d + 1 for d in front_dates]
    front_dates = [f'01/01/{y}' for y in front_dates]
    back_dates = [f'01/01/{y}' for y in back_dates]
    date_list = list(zip(front_dates,back_dates))
    self.date_list = date_list # save for use in "yearly_progress"
    yearly_mileage = {}
    for start, end in date_list:
      year = start[-4:]
      length = round(length_data[(length_data.Date >= start) & (length_data.Date <= end)].Length.sum()/5280,3)
      yearly_mileage[year] = length
    return yearly_mileage

  def _clean_data(self,document):
    data = pd.read_csv(document)
    data.Date = pd.to_datetime(data.Date)
    length_data = data[['Date', 'Length']]
    self.yearly_mileage = self._sum_miles(length_data)
    data = data[['Date','Route', 'Rating', 'Style', 'Lead Style', 'Route Type', 'Location']]
    
    data = data.rename(columns = (dict(zip(data.columns,['date', 'route', 'grade', 'style', 'lead_style', 'type', 'location']))))
    data.location = data.location.apply(lambda x: x.split(' > ')) # turn in to list (for graph object parsing and subdivision)
    data.grade = data.grade.apply(self._clean_grade)
    data = data[data['style'].isin(['Flash', 'Send', 'Solo', 'Lead'])] # currently removes bouldering "attempt", consider adding back
    data.lead_style = data.lead_style.fillna(data['style'])  # bring bouldering's send, flash, etc to lead style for later so it's all together
    data = data[data.lead_style != 'Fell/Hung']
    data = data[data.grade.apply(lambda x: type(x) in [int,np.int64, float, np.float64])] # get rid of strings (ex WI)
    return data

  def _clean_grade(self, grade):
    grade = str(grade).split()  # can be ['5.8','R'] or in the worst ['5.8','V-easy']
    try: # if mixed results as above, this checks for a "V" somewhere and assumes it's a bouldering grade
      vgrade = [g for g in grade if g.startswith('V')][0]
      grade = self.boulder_convert[vgrade]
    except IndexError:
      if grade[0][0] == '5':
        grade = self.ropes_convert[grade[0]]
    return grade

  def _x_round(self, x):
    """ rounds back to decimanls that can be reversed to letter grades
    for 10 and greater, rounds down to nearest .25
    eg. x_round(11.49) = 11.25, x_round(11.51) = 11.5
    and sub 10 numbers n to n.0, n.4 or n.8 whichever is closest - rounds down in ties
    """
    if x >= 10:
      return floor(x*4)/4
    else:
      base = floor(x)
      return_map = {x - base : 0, abs(x - base -.4): .4, abs(x - base - .8): .8}
      end = return_map[min(x-base, abs(x-base-.4), abs(x-base-.8))]
      return float(base + end)

  def _grade_to_letter(self, grade, boulder): # boulder is a boolean
    if boulder:
      try:
        grade = str(floor(grade))
        if grade == '-1':
          return 'V-easy'
        else:
          return 'V'+grade
      except: # sometimes grades like "5.8 V0" are given, assume it's 
        return 'V-easy'

    letter_map = {'.0':'a', '.25':'b', '.5':'c', '.75':'d'}
    letter_map_low = {'.0':'-', '.4':'', '.8':'+'}
    grade = float(grade) # ensure eg. 7 is 7.0 for proper mapping
    if grade >= 10:
      grade = str(grade)
      grade = grade[:2] + letter_map[grade[2:]]
      return grade
    else:
      grade = str(grade)
      grade = grade[:1] + letter_map_low[grade[1:]]
      return grade
    
  # Rounding Key example:

  # 10a, 10-, 10a/b  -> 10a
  # 10b, 10          -> 10b
  # 10b/c, 10c, 10+  -> 10c
  # 10c/d, 10d       -> 10d

  # def _grade_to_number(self, grade):   ################### Not used, maybe delete later
  #   letter_map = {'a':'.0', 'b':'.25', 'c':'.5', 'd':'.75', '-':'.0', '+':'.8'}
  #   if grade[-1].isnumeric() == False:
  #     grade = grade[:-1] + letter_map[grade[-1]]
  #     # print(grade)
  #   else:
  #     grade += '.4'
  #     # print(grade)


  def show_pyramids(self, requested_type_and_style=(None,None)):#['Redpoint','Pinkpoint','Onsight'])): #,[requested_pyramid_styles=None, lead_styles=['Redpoint','Pinkpoint','Onsight']):  # self.style_options[0] grabs the first key of dictionary, could be sport, trad, etc. point is it won't be empty  #NEW

    self.make_pyramid(requested_type_and_style) # among other things, creates self.pyramid_styles and self.lead_styles
    requested_pyramid_styles=requested_type_and_style[0]
    lead_styles=requested_type_and_style[1]

    all_pyramid_styles = [self.pyramids[p] for p in self.pyramid_styles]
    top_pyramid = pd.concat([self.pyramids[p] for p in self.pyramid_styles], axis=0)
    top_pyramid['count'] = pd.Series([1 for x in range(len(top_pyramid.index))], index=top_pyramid.index)

    grade_schema = self.grades_list
    if self.boulder:
      grade_schema = self.boulder_grades

    top_pyramid.grade = pd.Categorical(top_pyramid.grade, categories=grade_schema, ordered=True)
    top_pyramid.sort_values('grade', ascending=False, inplace=True)
    top_grades = top_pyramid.grade.unique()[:7] # get top 6 grades (arbitrary choice, can be an option later)
    top_grades = top_grades.tolist()[::-1]
    top_pyramid = top_pyramid[top_pyramid.grade.isin(top_grades)]

    date = dt.now().strftime('%-d%b%Y')
    self.title = f"{self.climber}<br>{'+'.join(self.pyramid_styles)} pyramid -- {self.sub_location[-1]} -- {date}<br>{'+'.join(self.lead_styles)}" 
    fig = px.bar(top_pyramid, x="count", y="grade", orientation='h', hover_name='route', title=self.title )
    
    fig.layout.yaxis=dict(autorange="reversed")
    fig.layout.yaxis.type = 'category' # ESSENTIAL! otherwise just the numeric (9,8,7, etc.) data get shown. Order matters too. This must happen AFTER reversing the range
    return fig 
