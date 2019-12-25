#!/usr/bin/env python3

# Finished 1 Oct 2019 - (about 2 weeks spread out start to finish)
# The purpose of this program is to get gps coordinates for all the "walls"
# In any climbing area specified. The output is a gpx file which will have
# the area subwalls labeled in your GPS and each route and their details
# (grade, whether it's trad or sport, number of pitches) as a comment

from bs4 import BeautifulSoup
import requests
import os
import re
import pandas as pd

# Requirements:
# gpsbabel    -   sudo apt install gpsbabel

#####################################################################
#                                                                   #
#               Enter area url and API key here                     #
#                                                                   #
#####################################################################

# An example climbing area in Southern California
############
# WARNING: #
############
# avoid going to high up (eg. all routes in California)
# Not only will this take a while, but all the traffic comming from your
# api-key will likely raise flags and your account may be suspended 
# or worse: the entire api is removed and no one else can enjoy
url = "https://www.mountainproject.com/area/105931166/central-pinnacles"

# Visit mountainproject.com/data (provided you are signed in) to get your key
api_key = "#########-################################"


# used to reduce lists of lists (and possibly of more lists) to a single list
# additional feature added: remove Nonetype entries
# Copied from Rosetta Code
def flatten(lst):
    outlist = sum( ([x] if not isinstance(x, list) else flatten(x) for x in lst), [] )
    outlist = [i for i in outlist if i] # removes Nonetype (introduced for blank areas)
    return outlist



def find_sub_areas(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source,'html.parser')
    sublinks = []
    lef_navs = soup.find_all('div',class_='lef-nav-row')
    if len(lef_navs) == 0:      # no "lef_navs" means we are at the lowest page
        return find_routes(url) # with just the wall. We return just route links
    for lef_nav in lef_navs:
        links = lef_nav.findChildren('a')
        sublinks.append([link['href'] for link in links])
    print("-"*80)
    print("\nnumber of sub areas:",len(lef_navs))
    print("\nhere are the links:")
    sublinks = flatten(sublinks)
    print(sublinks)
    print("#"*20)
    deeper_sublinks = []
    for sublink in sublinks:
        deeper_sublink = find_sub_areas(sublink)
        print("\ndeeper_sublinks:")
        print(deeper_sublink)
        deeper_sublinks.append(deeper_sublink)
    return deeper_sublinks



# find_routes will return the urls for all the routes on a wall
def find_routes(url):
    route_links = []
    source = requests.get(url).text
    soup = BeautifulSoup(source,'html.parser')
    routes = soup.find('table',id='left-nav-route-table')
    # some times a blank subarea exists and the above id does not
    try:
        routes = routes.findChildren('a')
        route_links.append([route['href'] for route in routes])
        route_links = flatten(route_links)
        return route_links
    except:
        pass



# group_routes clusters route ids in groups of 100
# mountain project API only allows groups of 100 or fewer
def group_routes(route_ids,n=100):
    for ids in range(0,len(route_ids),n):
        yield (route_ids[ids:ids+n])


# create_dataframe will return a data frame from a json object.
# Each json object comes from each group of 100 route from 'group_routes'
def create_dataframe(json):
    df = pd.DataFrame(json)
    df['route'] = df.name.astype(str)+'-'+df.type.astype(str)+\
    '-'+df.rating.astype(str)+'-'+df.pitches.astype(str)+'p'
    cols = ['route','location','longitude','latitude']
    df = df[cols]
    df.location = df.location.apply(lambda x: '-'.join(x))
    print("DF:\n",df)
    return df



# request_routes utilizes group_routes and create_dataframe, it makes the API
# request from  mountainproject for each route group which returns a json object
# the json is then turned into a dataframe, and parsed for relevant information
# then clustered into one master dataframe
def request_routes(route_groups):
    dfs = []
    for route_group in route_groups:
        route_group = ','.join(route_group)
        url_start = "https://www.mountainproject.com/data/get-routes?routeIds="
        url_end = "&key="+api_key # my MP key
        request_string = url_start + route_group + url_end
        request = requests.get(request_string)
        json = request.json()['routes']
        print("JSON:\n",json)
        df = create_dataframe(json)
        dfs.append(df)
    return dfs



all_routes = find_sub_areas(url)

all_routes = flatten(all_routes)
print(all_routes)
print('\n^',len(all_routes),"routes in total")

route_ids = []

for route in all_routes:
    match = re.findall('\d+',route)[0]  # The first number is always the route id
                                        # If any number appear in route name, they
                                        # will be ignored (\d+ is one or more digits)
    route_ids.append(match)

route_groups = list(group_routes(route_ids))
dfs = request_routes(route_groups) # list of dataframes
df = pd.concat(dfs)

##### Create String to be saved to csv ####
csv_string = 'Latitude,Longitude,Name,Description'

locs = df.location.unique()
groups = df.groupby('location')
for loc in locs:
    group = groups.get_group(loc)
    lat,long = group.iloc[0].latitude, group.iloc[0].longitude
    cmt = ('   '.join(group.route.to_list())).replace(',','')  
    # cmt is a string list of routes separated by double underscore. 
    # we remove any potential pre-existing commas, to avoid errors in the created CSV
    name = (group.iloc[0].location.split('-')[-1]).replace(',','') 
    # start with newline char, remove commas just in case
    newline = ','.join(['\n'+str(lat),str(long),name,cmt])
    csv_string += newline


#### Prompt user to create name and save file locally
filename = input ("what do you want to name this? ")

filename = filename.strip().replace(' ','_')

csv_filename = filename+'.csv'
gpx_filename = filename+'.gpx'


csv_file = open(csv_filename,'w')
csv_file.write(csv_string)
csv_file.close()


create_command = "gpsbabel -i unicsv -f "+csv_filename+" -o gpx -F "+gpx_filename
remove_command = "rm "+csv_filename
os.system(create_command)
os.system(remove_command)

print("A file has been created:",gpx_filename)
