# `gpsgrabber.py`

Non-standard python libraries and Linux utilities needed:

        BeautifulSoup   -       pip3 install python3-bs4
        gpsbabel        -       sudo apt install gpsbabel


## Purpose:
Provide an automated, no-effort service to scrape GPS coordinates for all walls in a climbing location from Mountain Project. Read the [blog writeup](https://tclack88.github.io/blog/code/2019/10/12/mountain-project-GPS.html) for more code detail

## How to Use:
0. If you don't already have an account, make one at [mountain project](mountainproject.com). Go to the area you're interested in and get that URL as well
1. visit their [API](mountainproject.com/data) and copy your unique API key
2. Download and open `gpsgrabber.py`
3. Paste your API key there and change the default UL to whichever area you're interested in
4. You'll be prompted to name the file (spaces will be replaced with underscores), just plug in your GPS device and drag and drop the newly created .gpx file there

![mountain project climbs on the GPS][https://tclack88.github.io/blog/assets/mproj/gps_collage.png]

<hr>

# `csv_scraping.ipynb`


Non-standard python libraries needed:

        BeautifulSoup   -       pip3 install python3-bs4


The purpose of this notebook is to gather a collection of random users on mountain project into a dataframe for analysis. This collection is seeded from a bunch of names. As is, the most popular baby names (1op 100 male and female) from 1985 act as the seeds, but a list can do well. To use this yourself, either set "possible\_users" equal to a list of names you want, or change the date and page number in the cell:
```python

# Grab names to seed the search (most popular male and female names from 1985)
name_url = "https://www.weddingvendors.com/baby-names/popular/1985/?page=1" # vary page number for more samples, I collected up to 6 for the data in my github

source = requests.get(name_url).text
soup = BeautifulSoup(source,'html.parser')
names = soup.find_all('td', class_='n')
possible_users = []
for name in names:
  possible_user = name.text
  possible_users.append(possible_user)
```

The csv files labeled "climber\_data" 1-6 represent my data scrapes, each took about an hour to gather, so thumbrule: 200 names/hour

The features I've engineered are ok, I'm sure there are more

# `mproj_analysis.ipynb`

This represents the analysis part I've done on the above collected data, see the data better presented [on my blog](https://tclack88.github.io/blog/personal/2019/09/27/climber-analysis.html)
