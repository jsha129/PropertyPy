# Investigating Melbourne property market using python

The aim of this project is to estimate annual growth rate of properties by suburbs of Melbourne (Australia) using publicly available data. Slight modification of the code may enable performing similar analysis for different parts of Australia. The data also contains median rent for the same data although this aspect is not explored in detail here.  

NOTE: THIS IS NOT FINANCIAL ADVICE. PLEASE SEEK PROFESSIONAL ADVICE BEFORE ACTING ON THE RESULTS. 

Sources of some of the data is unknown. These data remains copyright of the respective parties. 

# Approach: 
(in brief)
The project relies of domain.com.au's API to fetch annual aggregated data, including median price, on property types and bedrooms and so on. The median prices is used for linear regression to estimate annual growth rate. The data is then overlapyed on Melbourne Map using a 3rd party app mapbox (https://plotly.com/python/mapbox-layers/).

Property type of 'House' with 3 or 4 bedrooms have been used here for example, but the analysis could be extended for 'apartment' or other type of dwelling. Please consult Domain API documentation. 

# How to use this

**For visulisation only, download this repo as zip file and open relevant html files.** 

- 3 bedroom houses in Melbourne (html): calculate_rates_and_visualise_3bd_Houses_Melbourne.html 

To run this on your local computer from scratch:

(1) Get your access token to the Domain API and mapbox.

(2) Run `get_yearly_data.ipynb` to retrieve data.

(3) Perform linear regression and visualise using `calculate_rates_and_visualise_*.ipynb`. Data is exported as Excel files. See separate files for 3bd and 4 bd houses. 

**Unfortunately, exporting files as Excel somehow interferes with geopanda conversion, hence, regression on available data must be performed prior to visualisation if running from scratch.**


# Approach in detail
Domain API requires postcode, suburb name, property type (house, apartment etc) for data retrival. Postcode and suburb name are provided by the `Australian_Post_Codes_Lat_Lon.csv` but we have to select the postcodes of interest. We first define centre of the location (aka Melbourne CBD) by latitudes and lontitudes in `Melbourne_Center_Coord = {'lat': -37.814218,'long': 144.963526}` dictionary, calculate distance of each of the suburbs present in the postcode csv using the pythagoras theorem (aka distance in 2D), selecting the suburbs that are within a pre-defined distance of 30 km. Initially, the distance calculated from the pythagoras theorem did not match google map's answer, which was attributed to earth's curvature that was ignored when using the pythagoras theorem. As a shortcut, the pre-defined distance was slightly increased to adjust for the earth's curvature. This empirical approach is not perfect but it works. The selected suburbs are requested to the domain API.

The domain API returns last 10 years of annual data in JSON format that is dumped into a directory. There is seasonality variation here, ie the data is reported for a given month when API calls were requested. The data is log-transformed and appreciation rate for each suburb is estimated using linear regression. Useful statistics such as R-squared, slope of the line and intercept from log10 transformed data and linearised annual growth are exported. Median dwelling price at the start and end of period are also reported for quick validation. 


Annual appreciation rate is colour-coded and  visualised onto Melbourne map for exploration. To achieve this, suburb boundaries in the form of polygon are retrieved `aus_poas.shp` from and stored in geopanda data frame (see https://spatialvision.com.au/blog-open-source-spatial-geopandas-part-1/). The geopanda is the passed to  mapbox (https://plotly.com/python/mapbox-layers/) for visualisation. 

# Data sources and services: 
(1) Domain.com.au API. Open an account and create a new project. Then, create OAuth id and secret followed by adding `Properties & Locations` API access to the project. It may take some a few days to get access to the API.

Specifically, we will be using the following API: https://developer.domain.com.au/docs/latest/apis/pkg_properties_locations/references/suburbperformance_get_bynamedsuburb/

General API info: https://developer.domain.com.au

Please play with this and `get_yearly_data.ipynb` to get successful authentication.


(2) Latitudes and longitudes of suburb postcodes. `Australian_Post_Codes_Lat_Lon.csv` - bit outdated, but still OK. This was downloaded from Australia post (https://auspost.com.au).

(3) Mapbox. https://docs.mapbox.com/help/getting-started/access-tokens/

(4) Geopanda with suburb shape coordinates. https://spatialvision.com.au/blog-open-source-spatial-geopandas-part-1/


