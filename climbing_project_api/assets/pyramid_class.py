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
    self.old_ropes = self.grade_chart[0].YDSUSA[:-1].to_list()
    self.new_ropes = [0,0,0,0,1,2,3,4,5,6,7,7.4,8,8.4,8.8,9,9.4,9.8]+list(np.round(np.arange(10,16,.1),1))
    self.ropes_convert = dict(zip(self.old_ropes, self.new_ropes))
   
    self.data = self._clean_data(self.document)
    if sub_location:
      self.data = self.data[self.data.location.apply(lambda x: all(item in x for item in sub_location))]
    else:  # for use in the title
      self.sub_location = ['total']

    all_types = self.data['type'].unique()
    trad_types = [t for t in all_types if 'Trad' in t]
    sport_types = [t for t in all_types if 'Sport' in t and 'Trad' not in t]

    self.style_options = {}
    if trad_types:
      self.style_options['trad'] = trad_types
    if sport_types:
      self.style_options['sport'] = sport_types


  def make_pyramid(self, pyramid_styles=None, lead_styles=['Redpoint','Pinkpoint','Onsight']):
    # Split Trad and Sport data
    if pyramid_styles == None:
      pyramid_styles = [list(self.style_options.keys())[0]]
    self.styles = {}
    for p in pyramid_styles:
      try:
        self.styles[p] = self.data[(self.data['type'].isin(self.style_options[p])) & (self.data['lead_style'].isin(lead_styles))]
      except KeyError:
        pass

    self.pyramids = {}
    self.titles = {}
    for key,style in self.styles.items():   # likely unnecessary going forward, perhaps split boulders from routes
      if not style.empty:
        top_pyramid = style
        top_pyramid.grade = style.grade.apply(self._x_round)
        top_grades = top_pyramid.grade.unique()
        top_grades.sort()
        top_pyramid.grade = top_pyramid.grade.apply(self._grade_to_letter)
        self.pyramids[key] = top_pyramid

    self.grades_list = '0 1 2 3 4 5 6 7 7+ 8- 8 8+ 9- 9 9+'.split()
    self.numbs = '10 11 12 13 14 15'.split()
    self.letters =  list('abcd')
    for i in self.numbs:
      for j in self.letters:
        self.grades_list.append(i+j)


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
    data = data[data['style'] == 'Lead']
    data = data[data.grade.apply(lambda x: type(x) in [int,np.int64, float, np.float64])] # get rid of strings (ex WI)
    return data

  def _clean_grade(self, grade):
    grade = str(grade).split()[0]
    if grade[0] == '5':
      grade = self.ropes_convert[grade]
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

  def _grade_to_letter(self, grade):
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


    # TODO: make "none" a default argument, if none, return all (boulder maybe in future)
    # otherwise return sport, trad, etc. if 'sport' or 'trad' is included
  def show_pyramids(self, requested_pyramid_styles=None, lead_styles=['Redpoint','Pinkpoint','Onsight']):  # self.style_options[0] grabs the first key of dictionary, could be sport, trad, etc. point is it won't be empty  #NEW
    self.make_pyramid(pyramid_styles=requested_pyramid_styles, lead_styles=lead_styles)
    if requested_pyramid_styles == None: #NEW
      pyramid_styles = [list(self.style_options.keys())[0]] #NEW 
    else:
      pyramid_styles = [p for p in requested_pyramid_styles if p in self.pyramids] # check for bad input (choosing sport and trad if only sport exists)
    
    all_pyramid_styles = [self.pyramids[p] for p in pyramid_styles]

    top_pyramid = pd.concat([self.pyramids[p] for p in pyramid_styles], axis=0)
    top_pyramid['count'] = pd.Series([1 for x in range(len(top_pyramid.index))], index=top_pyramid.index)

    top_pyramid.grade = pd.Categorical(top_pyramid.grade, categories=self.grades_list, ordered=True)
    
    top_pyramid.sort_values('grade', ascending=False, inplace=True)
    top_grades = top_pyramid.grade.unique()[:6] # get top 6 grades (arbitrary choice, can be an option later)
    top_grades = top_grades.tolist()[::-1]
    top_pyramid = top_pyramid[top_pyramid.grade.isin(top_grades)]

    date = dt.now().strftime('%-d%b%Y')
    self.title = f"{self.climber}<br>{'+'.join(pyramid_styles)} pyramid<br>{self.sub_location[-1]} -- {date}" 
    fig = px.bar(top_pyramid, x="count", y="grade", orientation='h', hover_name='route', title=self.title )
    
    fig.layout.yaxis=dict(autorange="reversed")
    fig.layout.yaxis.type = 'category' # ESSENTIAL! otherwise just the numeric (9,8,7, etc.) data get shown. Order matters too. This must happen AFTER reversing the range
    #fig.show()
    return fig 


  def yearly_progress(self):
    years = []
    avgs = []
    labels = []
    for start, end in self.date_list:
      year = start[-4:]
      year_df = self.data[(self.data.date < end) & (self.data.date >= start)].sort_values('grade',ascending=False) # get year and arrange values
      year_df = year_df[~year_df['lead_style'].isin(['Fell/Hung', np.nan]) & ~year_df['style'].isin(['TR','Follow', np.nan])] # keep nans because at some piont Mountain Project included the tick type. Give benefit of doubt and assume they were all successful climbs
      year_df = year_df[:10]
    
      try:
        year_avg =  round(year_df.grade.mean(),1) 
        year_avg_grade = self._grade_to_letter(self._x_round(year_avg))
      except:
        year_avg = 0
        year_avg_grade = '5.0'
  
      years.append(year)
      avgs.append(year_avg)
      labels.append(year_avg_grade)
      
    avgs = [x if x != 0 else None for x in avgs] 
    #fig, ax = plt.subplots()
    
    #plt.plot(years, avgs)
    # change labels from numbers to letter grades
    #fig.canvas.draw()
    #old_labels = [item.get_text() for item in ax.get_yticklabels()]
    #new_labels = [self._grade_to_letter(self._x_round(float(label))) for label in old_labels]
    #ax.set_yticklabels(new_labels)
    #plt.show(); #TODO
    """
    bottom, top = floor(min(avgs)), ceil(max(avgs))
    label_range = sorted(list(set([float(x_round(grade)) for grade in new_ropes if (bottom <= grade <= top)])))
    # print(label_range)
    label_range_labels = [grade_to_letter(g) for g in label_range]
    """
    bottom, top = floor(min(avgs)), ceil(max(avgs))
    label_range = sorted(list(set([float(self._x_round(grade)) for grade in self.new_ropes if (bottom <= grade <= top)])))
    # print(label_range)
    label_range_labels = [self._grade_to_letter(g) for g in label_range]
    fig2 = go.Figure(data=go.Scatter(x=years, y=avgs))
    fig2.update_layout(yaxis = dict(
                     tickvals=label_range,
                      ticktext=label_range_labels))
    fig2.show()


  def suggest_pyramid(self, requested_pyramid_style=None):  # self.style_options[0] grabs the first key of dictionary, could be sport, trad, etc. point is it won't be empty  #NEW
    if requested_pyramid_style == None: #NEW
      pyramid_style = list(self.style_options.keys())[0] #NEW
    else:
      pyramid_style = requested_pyramid_style
    self.pyramid = self.pyramids[pyramid_style]
    self.scheme = [1,2,4,8,12] # may need to pass in later or set as "class global"
    
    self.top_index = self.grades_list.index(self.pyramid.grade[0]) + 1
    self.user_grade_count_dict = dict(zip(self.pyramid.grade, self.pyramid['count']))
    self.top_5_grades = self.grades_list[self.top_index : self.top_index - 5 : -1]
    self.top_5_count = [ self.user_grade_count_dict.get(grade,0) for grade in self.top_5_grades] # 2nd argument in .get() gives value to be returned if non-existent

    self.pyramid_copy = pd.DataFrame(zip(self.top_5_grades, self.top_5_count), columns = ['grade','count']).iloc[:5]
    self.pyramid_copy['ideal_count'] = self.scheme
    self.pyramid_copy['todo'] = self.pyramid_copy.ideal_count - self.pyramid_copy['count']
    self.pyramid_copy.todo = self.pyramid_copy.todo.apply(lambda x: 0 if (x < 1) else x) # negative numbers -> 0 
    return self.pyramid_copy

  def make_recommendations(self, area_url, pyramid_style='sport'):
    self.table = pd.read_html(area_url)[1]
    self.table = self.table[self.table.Difficulty.str.startswith('5.')]
    # grades
    self.grades = self.table.Difficulty.apply(lambda x: x.split()[0])
    self.grades = self.grades.apply(lambda x: self._x_round(self.ropes_convert[x])).apply(self._grade_to_letter) # remove V grades, convert to simplified letter grades
    # routes
    self.routes = self.table['Route Name'].apply(lambda x: ' '.join(x.split()[1:]))
    # putting them together
    self.recommendations_dict = {'grade':self.grades, 'route':self.routes}
    self.recommendations_df = pd.DataFrame(self.recommendations_dict)
    ########### redundant in "suggest_pyramids" method, consider making DRY (global?) #########
    self.top_index = self.grades_list.index(self.sport_pyramid.grade[0]) + 1
    self.user_grade_count_dict = dict(zip(self.sport_pyramid.grade, self.sport_pyramid['count']))
    self.top_5_grades = self.grades_list[self.top_index : self.top_index - 5 : -1] # list of top grades as string
    self.top_5_count = [ self.user_grade_count_dict.get(grade,0) for grade in self.top_5_grades] # 2nd argument in .get() gives value to be returned if non-existent
    ###################################################################################
    #another add in ##
    self.successful_climbs = self.data[(self.data.lead_style == 'Redpoint') | (self.data.lead_style =='Onsight')]
    self.successful_climbs.grade = self.successful_climbs.grade.apply(lambda x: self._grade_to_letter(self._x_round(x)))
    self.successful_climbs_stack = self.successful_climbs[['grade','route']]
    # successful_climbs_stack
    #end add in
    self.suggested_pyramid = self.suggest_pyramid(pyramid_style)
    self.recommendations_df = self.recommendations_df[self.recommendations_df.route.isin(self.successful_climbs_stack.route) == False] # returns area classics that haven't been climbed
    self.recommendations_df = self.recommendations_df[self.recommendations_df.grade.str.contains('|'.join(self.top_5_grades))][::-1].reset_index(drop=True) # returns the right grade range (| in the string will give an "or" effect)
    self.recommendations_df[self.recommendations_df.grade.isin(self.suggested_pyramid[self.suggested_pyramid.todo > 0].grade)] # remove grades within the suggested range that have been "overclimbed"
    # print(recommendations_df)
    return self.recommendations_df

