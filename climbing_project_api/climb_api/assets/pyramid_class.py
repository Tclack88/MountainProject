import pandas as pd
import numpy as np
from math import floor, ceil
from datetime import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

class Pyramid:
  def __init__(self,document):
    self.document = document
    self.climber = document.split('/')[-2].replace('-',' ').title()
    self.grade_chart = pd.read_html("https://www.mountainproject.com/international-climbing-grades")
    self.old_ropes = self.grade_chart[0].YDSUSA[:-1].to_list()
    self.new_ropes = [0,0,0,0,1,2,3,4,5,6,7,7.4,8,8.4,8.8,9,9.4,9.8]+list(np.round(np.arange(10,16,.1),1))
    self.ropes_convert = dict(zip(self.old_ropes, self.new_ropes))
   
    self.data = self._clean_data(self.document)
    # Split Trad and Sport data
    self.trad = self.data[(self.data['type'] == 'Trad') | (self.data['type'] == 'Trad, Sport') | (self.data['type'] == 'Trad, Alpine') | (self.data['type'] == 'Trad, Aid')]
    self.sport = self.data[(self.data['type'] == 'Sport') | (self.data['type'] == 'Sport, TR')]
    self.trad_rp = self.trad[self.trad.lead_style.isin(['Redpoint','Pinkpoint'])]
    self.trad_os = self.trad[self.trad.lead_style == 'Onsight']
    self.trad_os.grade.apply(self._x_round).value_counts().sort_index(ascending=False)
    self.sport_rp = self.sport[self.sport.lead_style.isin(['Redpoint','Pinkpoint'])]
    self.sport_os = self.sport[self.sport.lead_style == 'Onsight']

    self.sport_combined = pd.concat([self.sport_rp,self.sport_os], axis=0)
    self.trad_combined = pd.concat([self.trad_rp, self.trad_os], axis=0)
    self.styles = [self.sport_combined, self.trad_combined]
    date = dt.now().strftime('%-d%b%Y')
    self.pyramids = []
    self.titles = []
    for i, style in enumerate(self.styles):
      if not style.empty:
        self.title = f"{self.climber}\n{style.iloc[0]['type'].split(',')[0]} pyramid \n as of {date}\n"
        self.top_pyramid = style.grade.apply(self._x_round).value_counts().sort_index(ascending=False).iloc[:6].reset_index()
        self.top_pyramid.columns = ('grade','count')
        self.top_pyramid.grade = self.top_pyramid.grade.apply(self._grade_to_letter)
        self.pyramids.append(self.top_pyramid)
        self.titles.append(self.title)
    
    self.sport_pyramid = self.pyramids[0]
    self.trad_pyramid = self.pyramids[1]

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

  # @staticmethod
  def _clean_data(self,document):
    data = pd.read_csv(document)
    data.Date = pd.to_datetime(data.Date)
    length_data = data[['Date', 'Length']]
    self.yearly_mileage = self._sum_miles(length_data)
    data = data[['Date','Route', 'Rating', 'Style', 'Lead Style', 'Route Type']]
    
    data = data.rename(columns = (dict(zip(data.columns,['date', 'route', 'grade', 'style', 'lead_style', 'type']))))
    data.grade = data.grade.apply(self._clean_grade)
    data = data[data['style'] == 'Lead']
    data = data[data.grade.apply(lambda x: type(x) in [int,np.int64, float, np.float64])] # get rid of strings (ex WI)
    return data

  # @staticmethod
  def _clean_grade(self, grade):
    grade = str(grade).split()[0]
    if grade[0] == '5':
      grade = self.ropes_convert[grade]
    return grade

  # @staticmethod
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

  # @staticmethod
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

  def _grade_to_number(self, grade):
    letter_map = {'a':'.0', 'b':'.25', 'c':'.5', 'd':'.75', '-':'.0', '+':'.8'}
    if grade[-1].isnumeric() == False:
      grade = grade[:-1] + letter_map[grade[-1]]
      print(grade)
    else:
      grade += '.4'
      print(grade)


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
    ##########################################################################################################
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


    # TODO: make "none" a default argument, if none, return all (boulder maybe in future)
    # otherwise return sport, trad, etc. if 'sport' or 'trad' is included
  def show_pyramids(self,pyramid_style='sport'):
    if pyramid_style == 'sport':
      self.style = self.styles[0]
      self.top_pyramid = self.pyramids[0]
      self.title = self.titles[0]
    elif pyramid_style == 'trad':
      self.style = self.styles[1]
      self.top_pyramid = self.pyramids[1]
      self.title = self.titles[1]
    #sb.barplot(y='grade', x='count', data=self.top_pyramid, color='green')
    print('top pyramid')
    print(self.top_pyramid)
    fig = px.bar(self.top_pyramid, x="count", y="grade", orientation='h')
    fig.layout.yaxis=dict(autorange="reversed")
    #fig.show()
    #plt.title(self.title)
    #plt.show()
    print(self.top_pyramid)
    print('\n\n\t\ttop 10')
    print(self.style.sort_values('grade',ascending=False).head(10))
    return fig # I think I want none because I just want to display pyramids for now. Else return self.pyramids


  # TODO: run show_pyramid first to establish trad or sport pyramid or.... pull stuff out of show_pyramid first into __init__ 
  # making show_pyramids into something smaller. REASON: show_pyramids has to be called before suggest_pyramid because it establishes
  # what self.sport_pyramid and self.trad_pyramid are
  def suggest_pyramid(self, pyramid_style='sport'):
    if pyramid_style == 'sport':
      self.pyramid = self.sport_pyramid
    elif pyramid_style == 'trad':
      self.pyramid = self.trad_pyramid
    # else:
    #   print('perform method "show_pyramid" first')
    #   return None
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
