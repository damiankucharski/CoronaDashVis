from bs4 import BeautifulSoup
import bs4
import requests
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
from plotly import tools
import plotly.offline as py
import plotly.graph_objs as go
import plotly.express as px



def make_series(trs, rowspans = [0 for i in range(19)]):
    result = []
    iterator = iter(trs)
    for i, element in enumerate(rowspans):
        if element == 0:
            next_iter = next(iterator)
            result.append(next_iter)
        else:
            result.append(0)
            rowspans[i] -= 1
    
    return np.array(result).reshape(1,-1), rowspans

def make_cumulative(data):
    
    data = copy.deepcopy(data)

    for i, element in enumerate(data[1:], start = 1):
        data[i] += data[i-1]
    
    return data
    
def stripFromPage(bs,tag):
    return re.sub("<td.*>","",str(bs).replace("<{}>".format(tag),"").replace("</{}>".format(tag),"").replace("\xa0","").replace("–","0"))[:-1]


def create_to_plot_frame(tabela):
    latitudes = [51.1, 53.0, 51.24, 52.73, 51.75, 50.06, 52.23, 50.668, 50.04, 53.13, 54.35, 50.265, 50.866, 53.778, 52.4, 53.428]
    longtitudes = [17.0, 18.0, 22.56, 15.24, 19.456, 19.945, 21.01, 17.92, 22.0, 23.168, 18.646, 19.02, 20.6, 20.48, 16.925, 14.55]
    capitals = ['Wrocław', "Bydgoszcz", "Lublin", "Gorzów Wielkopolski", "Łodź", "Kraków", "Warszawa", "Opole", "Rzeszów", "Białystok", "Gdańsk", "Katowice", "Kielce", "Olsztyn", "Poznań", "Szczecin"]
    voivodes = ['Dolnośląskie','Kujawsko-pomorskie','Lubelskie','Lubuskie','Łudzkie','Małopolskie','Mazowieckie','Opolskie','Podkarpackie','Podlaskie','Pomorksie','Śląskie','Świętokrzyskie','Warmińsko-Mazurskie','Wielkopolskie','Zachodnio-pomorskie']
    
    final_frame = pd.DataFrame()
    for i in range(len(tabela)):
        
        to_plot_frame = pd.DataFrame(np.array([latitudes, longtitudes, [cumulative for cumulative in tabela.iloc[i,19:]],[growth for growth in tabela.iloc[i,3:19]], voivodes]).T, columns = ['lat', 'long', 'sick', 'growth', 'Województwo'])
        
        ########### TO SET AS FLOATS THERE IS A BUG THAT CAN BE FIXED LIKE THAT
        to_plot_frame.iloc[:,:-1] = to_plot_frame.iloc[:,:-1].astype(float) 
        to_plot_frame.iloc[:,1] = to_plot_frame.iloc[:,1].astype(float) 
        to_plot_frame.iloc[:,:-1] = to_plot_frame.iloc[:,:-1].astype(float) 
        ###########
        to_plot_frame['markersize'] = np.log(to_plot_frame['sick'] + 1) / np.log(2) * 50 
        to_plot_frame.index = [dates_vals[i] for j in range(len(capitals))]

        final_frame = pd.concat([final_frame, to_plot_frame])

    
    return final_frame


def toDateString(ind):
    arr = str(ind).replace(" ","").split(".")
    final = '2020-' + arr[1] + '-' + arr[0]
    return final


html_doc = requests.get('https://pl.wikipedia.org/wiki/Pandemia_COVID-19_w_Polsce#Statystyki').text
soup = BeautifulSoup(html_doc, 'html.parser')
x = str(soup.find_all('table', {'class':'wikitable mw-collapsible'}))
soup = BeautifulSoup(x, 'html.parser')
rows = [row for row in soup.find_all('tr')]

dicts = {}
dates = []
for row in rows[3:-3]:
    date = row.findAll('th',text=True)[0]
    data = stripFromPage(date,'td')
    data2 = row.findAll('td',text=True)
    arr = [stripFromPage(x,'td') for x in data2]
    dicts[date] = arr
    dates.append(date)

dicts[dates[0]] =  ['1','1','0','1']

rowspans = [0,0,0,2,13,6,0,7,5,4,7,7,13,10,4,10,2,5,2]
results, rowspans = make_series(dicts[dates[0]], rowspans)
kolumny = ['Narastająco','Dzienny przyrost','Przyrost w %','Dolnośląskie','Kujawsko-pomorskie','Lubelskie','Lubuskie','Łudzkie','Małopolskie','Mazowieckie','Opolskie','Podkarpackie','Podlaskie','Pomorksie','Śląskie','Świętokrzyskie','Warmińsko-Mazurskie','Wielkopolskie','Zachodnio-pomorskie']
tabela = pd.DataFrame(results, columns = kolumny)


for date in dates[1:]:
    wartosci = dicts[date]
    results, rowspans = make_series(wartosci, rowspans)
    df_length = len(tabela)
    tabela.loc[df_length] = results[0]

tabela.iloc[:,3:] = tabela.iloc[:,3:].astype(int) 
dates_vals = [re.search("<th>(.*)\n</th>", str(date)).group(1) for date in dates]
tabela.index = dates_vals

cumulative = pd.DataFrame(np.array([make_cumulative(tabela[x]) for x in tabela.iloc[:,3:].columns]).T, columns = "Cum " + np.array(tabela.iloc[:,3:].columns))
cumulative.index = dates_vals
tabela = pd.concat([tabela, cumulative], axis=1)

test = create_to_plot_frame(tabela)
test['Data'] = test.index
test.reset_index(drop=True, inplace=True) 
test['Data'] = test['Data'] + ' '
test['date'] = np.array([toDateString(x) for x in test['Data']])

cumulative = px.line(test, x="date", y="sick", color="Województwo", line_group="Województwo", hover_name="Województwo",
        line_shape="spline", render_mode="svg")

# py.plot(fig, filename='cumulative.html')

growth = px.line(test, x="date", y="growth", color="Województwo", line_group="Województwo", hover_name="Województwo",
        line_shape="spline", render_mode="svg")

# py.plot(fig, filename='growth.html')

px.set_mapbox_access_token('pk.eyJ1Ijoic2xham5pIiwiYSI6ImNrYW1odTVmNTBsc3Eyem12djI1b3JydmgifQ.hXr-PSsntocVN7UuiU7FIQ')

mapa = px.scatter_mapbox(test, lat="lat", lon="long",     color="sick", size="markersize",
                color_continuous_scale=px.colors.sequential.Purpor, size_max=15, zoom=5,animation_frame="Data", height = 700)

# py.plot(fig, filename='map.html')