## imports
import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
import math
import geopandas
import os
import time
import openpyxl
import re

## graphs
# %matplotlib inline
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
from mpl_toolkits.axes_grid1 import make_axes_locatable
import plotly.graph_objects as go
import plotly.express as px


###---------
# custon functions
def getAccessToken():
    '''Gets Access Token for the session based on pre-defined client_id and client_secret. Sets auth_dict containing access token as global variable.'''
    global auth_dict # stores token
    cmd = 'curl -X POST -u '
    cmd = cmd + '\'' + client_id + ':' + client_secret +'\''
    cmd = cmd + ' -H \'Content-Type: application/x-www-form-urlencoded\'' 
    cmd = cmd + ' -d \'grant_type=client_credentials&scope=api_suburbperformance_read\''
    cmd = cmd + ' \'https://auth.domain.com.au/v1/connect/token\''
    returned_value = subprocess.check_output(cmd, shell = True)
    auth_dict = json.loads(returned_value.decode('utf8'))   
    

## housiing market example, copied
def parseJson(json_raw, plotGraph = True, verbose = True):
    import json
    import re
    beds = int(re.findall('\d{1}bd_', json_raw)[0].replace("bd_",""))

    # json_raw = 'data/Prahran_VIC_3181_2bd_house.json'
    f = open (json_raw, "r")
    text = f.read()
    f.close()
    
    if (len(re.findall('400 Bad Request', text)) == 0 and  len(re.findall('Internal Server Error', text)) == 0  ):
        json_list = json.loads(text)
        rawList = json_list['series']['seriesInfo']

        list_df = []

        for i in rawList:
            temp_dict = {}
            temp_dict['month'] = i['month']
            temp_dict['year'] = i['year']   
            temp_dict['year_month'] = str(i['year'])  + "_" + str(i['month'])

            for key, value in i['values'].items():
                temp_dict[key] = value

            list_df.append(temp_dict)

        df = pd.DataFrame(list_df)
        df['suburb'] = json_list['header']['suburb']
        df['propertyCategory'] = json_list['header']['propertyCategory']
        df['bedrooms'] = beds

        if plotGraph:
            plt.plot(df['year'],df['medianSoldPrice'], 'ob-')
            plt.title(str(beds) + " bedroom " + json_list['header']['propertyCategory'] + ", " + json_list['header']['suburb'] + ' (Annual data)'  )
            plt.show()   
        return(df)
    else:
        if (verbose): print("Insufficient data for:",json_raw)
        return([""])

### ----
def calculateGrowth_backup(df):
    df = df[~df['medianSoldPrice'].isnull()] # remove Nan and see remaining data
    if(df.shape[0] > 0 ): # num of non nan rows
        Y = np.log10(np.array(df.medianSoldPrice).reshape(-1,1))
    #     X = np.array(df.index).reshape(-1,1) # same order as df.year_month
        X = np.array(df.year - 2010).reshape(-1,1)
        reg = LinearRegression().fit(X = X, y = Y)

        stats_dict = {'suburb' : list(df.suburb.unique()),
                      'propertyCategory' : list(df.propertyCategory.unique()),
                      'bedrooms' : list(np.int_(df.bedrooms.unique())) ,
                    'R-squared': round(reg.score(X, Y),2),
                     'log10_growth' : list(np.round(reg.coef_[0],4)),
                     'log10_intercept' : list(np.round(reg.intercept_,2)),
                     'linear_growth' : [round(10**c,4) for c in list(reg.coef_[0])],
                     'linear_intercept' : [int(10**c) for c in list(reg.intercept_)],
                      'N' : df.shape[0],
                      'starting_price' : list(df[df.year == df.year.min()].loc[:,'medianSoldPrice']),
                     'final_price' : list(df[df.year == df.year.max()].loc[:,'medianSoldPrice']) }
    else:
        stats_dict = {'suburb' : list(df.suburb.unique()),
              'propertyCategory' : list(df.propertyCategory.unique()),
              'bedrooms' : list(np.int_(df.bedrooms.unique())) ,
            'R-squared': None,
             'log10_growth' : None,
             'log10_intercept' : None,
             'linear_growth' : None,
             'linear_intercept' : None,
            'N' : df.shape[0],
              'starting_price' : None,
             'final_price' : None}
        
    return(pd.DataFrame(stats_dict))

## --
def calculateGrowth_wide(df, factor = 'medianSoldPrice'):
    assert factor in df.columns, "Column " + factor + " not found in df"
    df = df[~df[factor].isnull()] # remove Nan and see remaining data
    if(df.shape[0] > 2 ): # num of non nan rows
        Y = np.log10(np.array(df[factor]).reshape(-1,1))
    #     X = np.array(df.index).reshape(-1,1) # same order as df.year_month
        X = np.array(df.year - 2010).reshape(-1,1)
        reg = LinearRegression().fit(X = X, y = Y)

        stats_dict = {'suburb' : list(df.suburb.unique()),
                      'propertyCategory' : list(df.propertyCategory.unique()),
                      'bedrooms' : list(np.int_(df.bedrooms.unique())),
                    #   'Type' :  factor,
                    factor + '_R-squared': round(reg.score(X, Y),2),
                    factor + '_log10_growth' : list(np.round(reg.coef_[0],4)),
                    factor + '_log10_intercept' : list(np.round(reg.intercept_,2)),
                    factor + '_linear_growth' : [round(10**c,4) for c in list(reg.coef_[0])],
                    factor + '_percent_growth' : [100*(round(10**c,4) - 1) for c in list(reg.coef_[0])],
                    # factor + '_linear_intercept' : [int(10**c) for c in list(reg.intercept_)],
                     factor + '_N' : df.shape[0],
                     factor + '_starting_price' : list(df[df.year == df.year.min()].loc[:,factor]),
                    factor + '_final_price' : list(df[df.year == df.year.max()].loc[:,factor]) }
    else:
        stats_dict = {'suburb' : list(df.suburb.unique()),
              'propertyCategory' : list(df.propertyCategory.unique()),
              'bedrooms' : list(np.int_(df.bedrooms.unique())),
            #   'Type' : factor,
           factor + '_R-squared': None,
            factor + '_log10_growth' : None,
            factor + '_log10_intercept' : None,
            factor + '_linear_growth' : None,
            factor + '_percent_growth' : None,
            # factor + '_linear_intercept' : None,
           factor + '_N' : df.shape[0],
             factor + '_starting_price' : None,
            factor + '_final_price' : None}
        
    return(pd.DataFrame(stats_dict))


## 
def calculateGrowth_long(df, factor = 'medianSoldPrice'):
    assert factor in df.columns, "Column " + factor + " not found in df"
    df = df[~df[factor].isnull()] # remove Nan and see remaining data
    if(df.shape[0] > 0 ): # num of non nan rows
        Y = np.log10(np.array(df[factor]).reshape(-1,1))
    #     X = np.array(df.index).reshape(-1,1) # same order as df.year_month
        X = np.array(df.year - 2010).reshape(-1,1)
        reg = LinearRegression().fit(X = X, y = Y)

        stats_dict = {'suburb' : list(df.suburb.unique()),
                      'propertyCategory' : list(df.propertyCategory.unique()),
                      'bedrooms' : list(np.int_(df.bedrooms.unique())),
                      'Type' :  factor,
                    'R-squared': round(reg.score(X, Y),2),
                   'log10_growth' : list(np.round(reg.coef_[0],4)),
                   'log10_intercept' : list(np.round(reg.intercept_,2)),
                   'linear_growth' : [round(10**c,4) for c in list(reg.coef_[0])],
                   'percent_growth' : [100*(round(10**c,4) - 1) for c in list(reg.coef_[0])],
                    #'linear_intercept' : [int(10**c) for c in list(reg.intercept_)],
                    'N' : df.shape[0],
                    'starting_price' : list(df[df.year == df.year.min()].loc[:,factor]),
                   'final_price' : list(df[df.year == df.year.max()].loc[:,factor]) }
    else:
        stats_dict = {'suburb' : list(df.suburb.unique()),
              'propertyCategory' : list(df.propertyCategory.unique()),
              'bedrooms' : list(np.int_(df.bedrooms.unique())),
              'Type' : factor,
          'R-squared': None,
           'log10_growth' : None,
           'log10_intercept' : None,
           'linear_growth' : None,
           'percent_growth' : None,
            #'linear_intercept' : None,
          'N' : df.shape[0],
            'starting_price' : None,
           'final_price' : None}
        
    return(pd.DataFrame(stats_dict))



### ---

def isPointInROI2(lat, long, region = 'Melbourne', maxDistance = 30):
    major_city_coord = {'Melbourne' : {'lat': -37.814218,'long': 144.963526},
                    'Sydney' : {'lat': -33.87003635458607, 'long': 151.20745239732523},
                    'Parramatta' :{'lat': -33.815101579800746, 'long': 150.99980625492702}
                    }
    assert region in major_city_coord, "Location must be one of :" + major_city_coord.keys()
    '''Checks wheather a point on map falls within a square region of interest.
    length of the ROI is maxDistance x 2, with ref coord of melbourne as center (0,0).
    1 degree on lat and long is roughly 110 km. 
    '''    
    return((abs(lat - major_city_coord[region]['lat']) < (maxDistance/110)) &  (abs(long - major_city_coord[region]['long']) < (maxDistance/110)))



Melbourne_Center_Coord = {'lat': -37.814218,'long': 144.963526}
def isPointInROI(lat, long, maxDistance = 30):
    '''Checks wheather a point on map falls within a square region of interest.
    length of the ROI is maxDistance x 2, with ref coord of melbourne as center (0,0).
    1 degree on lat and long is roughly 110 km. 
    '''    
    return((abs(lat - Melbourne_Center_Coord['lat']) < (maxDistance/110)) &  (abs(long - Melbourne_Center_Coord['long']) < (maxDistance/110)))

### ---
def getMelbourneSuburbs(file="Australian_Post_Codes_Lat_Lon.csv", maxDistance = 30):
    '''Reads a file containing postcodes and locations (lat, long) and returns a DataFrame containing suburns within 30 km of Melbourne CBD.'''
    postcodes = pd.read_csv(file)
    postcodes = postcodes.query('state == "VIC"' )  
    postcodes['inROI'] = postcodes[ ['lat', 'lon'] ].apply(lambda x: isPointInROI(x[0], x[1], maxDistance = maxDistance) , axis = 1)
    postcodes = postcodes[(postcodes.inROI) & (postcodes['postcode'] < 3400) & (postcodes['postcode'] != 3409)]
    return(postcodes)

### ---
def getSinglePropertyStats_raw(my_property,my_bedrooms, my_postcode, my_suburb,
                               exportDir, 
                               my_state = 'VIC', 
                               my_periodSize='quarters'):
    '''Fetches data on a single query and dumps raw data that into exportDir '''
    fileName = exportDir + '/' + str(my_postcode) + '_' + my_suburb.replace(" ",'-') + '_' + my_state + '_' + my_bedrooms + 'bd_' + my_property + '_'+ my_periodSize + '_raw.json'
    if not os.path.exists(fileName):        
        q = '\'https://api.domain.com.au/v2/suburbPerformanceStatistics'
        q = q + '/' + my_state + '/' + my_suburb + '/' + str(my_postcode) +'?'    
        q = q + 'propertyCategory=' + my_property + '&bedrooms=' + my_bedrooms 
        q = q + '&periodSize='+ my_periodSize +'&startingPeriodRelativeToCurrent=2&totalPeriods=500\''
        url_request = 'curl -X GET -H \'Authorization: Bearer ' + auth_dict['access_token'] + '\''
        url_request = url_request + ' -H \'Content-Type: application/json\' ' 
        url_request = url_request + q
    #     print(url_request)
        q_response = subprocess.check_output(url_request, shell = True).decode('utf8')
    #     q_response_dict = json.loads(q_response)
        f = open(fileName, 'w')
        f.write(q_response)
        f.close()
        print("File written:", fileName)
    else:
        print("Data exists. Skipped:", fileName)

