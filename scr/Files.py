import geopandas as gpd
from matplotlib import pyplot as plt

#loading shapeFiles

South_mw_pop=gpd.read_file('data\south_mw_pop.shp')
BT_city_landuse_general=gpd.read_file('data\BT_landuse_general.shp')
BT_city_HCs=gpd.read_file('data\BT_city_HCs.gpkg')
BT_city_roads=gpd.read_file('data\BT_city_roads.gpkg')

# function for converting shapefiles to to_WGS_1984_UTM_Zone_36S

def to_WGS_1984_UTM_Zone_36S(shapeFiles, projection= 'EPSG:32736'):
    try:
        for shapeFile in shapeFiles:
            shapeFile.crs=projection            
    except Exception:
        print("error creating projection")
        
# function for merging shapeFiles

def merge(shapeFile1,shapeFile2):    
    if shapeFile2.crs != shapeFile1.crs:
        to_WGS_1984_UTM_Zone_36S([shapeFile1,shapeFile2])
    return gpd.overlay(shapeFile1, shapeFile2, how='union', keep_geom_type=False)

#function for difference

def difference(shapeFile1, shapeFile2):
    if shapeFile2.crs != shapeFile1.crs:
        to_WGS_1984_UTM_Zone_36S([shapeFile1,shapeFile2])
    return gpd.overlay(shapeFile1,shapeFile2, how='difference', keep_geom_type=False) 

#function for buffering

def buffer(files):
    result=[]
    for file in files:
        buffer=file[0].buffer(file[1])
        result.append(buffer)
    return result

#function for buffering

def dissolve(files):
    result=[]
    for file in files:
        if type(file) == gpd.GeoDataFrame:
            _file=file.dissolve(as_index=False)
            result.append(_file)
        else:
            _file=file.to_frame().dissolve(as_index=False)
            result.append(_file)
        
    return result
        
        
#converting shapefiles to to_WGS_1984_UTM_Zone_36S
    
to_WGS_1984_UTM_Zone_36S([South_mw_pop,BT_city_landuse_general,BT_city_HCs,BT_city_roads])

'''
brainStorm
-----------------------------------------------------------------------------------------------------
1.	Data Collection:
•	Obtain GIS data for the city of Blantyre, including layers for existing government hospitals,
    residential areas, and road networks. This data can be sourced from local government authorities
    or open data repositories.
    
2.	Data Preprocessing:
•	Clean and preprocess the data. This may involve data conversion, format adjustments, and ensuring that
    all data layers are in a consistent coordinate system.
    
3.	Spatial Analysis:
•	Perform spatial analysis to identify suitable areas for hospital construction. For each criterion specified 
    (distance from existing hospitals, residential areas, and roads), we will need to calculate distances using 
    spatial analysis tools. We can use Python libraries like Geopandas and Shapely to perform these operations.
    
4.	Distance Calculation:
•	Calculate the distance from each potential location to the nearest existing government hospital, residential
    area, and road using GIS operations. This can be done using buffer operations, nearest neighbor analysis, or 
    other distance measurement tools.
    
5.	Overlay Analysis:
•	Combine the distance calculations from step 4 to create a composite suitability map. We can assign weights to 
    each criterion based on its importance. For example, being closer to existing hospitals might be more important 
    than proximity to roads.
    
6.	Spatial Query:
•	Use spatial query techniques to identify areas that meet all the specified criteria. For example, We can use 
    Python and GIS libraries to query the composite suitability map to find areas that are at least 1 km away from 
    existing hospitals, not more than 100 m away from residential areas, and not more than 100 m away from roads.
    
7.	Visualization:
•	Create a map that highlights the suitable areas for hospital construction. We can use libraries like Folium or 
    Matplotlib to visualize the results on a map.
8.	Optimization (Optional):
•	If We want to find the absolute best site for the new hospital, We can use optimization algorithms that take 
    into account the weighted criteria and constraints to identify the optimal location.
9.	Report Generation:
•	Generate reports and documentation of the analysis, including the selected site, distances, and any other 
    relevant information.
10.	Consultation and Decision-Making:
•	Share the results with relevant stakeholders, such as the Ministry of Health, city planners, and local 
    communities, to make an informed decision on the best site for the new hospital.

---------------------------------------------------------------------------------------------------------------------------

'''
#extracting Blantyre city and residential areas from south_mw_pop and BT_landuse_general respectively

BT_City_Clipped=South_mw_pop.loc[South_mw_pop['DISTRICT']=="Blantyre city"]
BT_residential=BT_city_landuse_general[BT_city_landuse_general['USE_GEN']=='Residential']

BT_residential.to_file('scr\outputfiles\BT_residential.shp')

BT_city_govt_hospitals=BT_city_HCs[BT_city_HCs['OWNER']=='MOH']
BT_city_govt_hospitals.to_file('scr\outputfiles\BT_city_govt_hospitals.shp')

# visualization :
# BT_city_govt_hospitals.plot()
# plt.show()

#buffering :

result=buffer([[BT_city_roads,100],[BT_residential,100],[BT_city_govt_hospitals,1000]])

BT_roads_100m_buffer,BT_residential_100m_buffer,Bt_city_govt_health_facilities_1000m_buffer=result


# #dissolving and visualization :

dissolves=dissolve([BT_roads_100m_buffer,BT_residential_100m_buffer,Bt_city_govt_health_facilities_1000m_buffer])

dissoved_BT_roads_100m_buffer,dissoved_BT_residential,dissolved_Bt_city_govt_health_facilities_1000m_buffer=dissolves


# merging

merged_1=merge(dissoved_BT_residential,dissoved_BT_roads_100m_buffer)

merged_1.to_file('scr\outputfiles\merged_1.shp')

# ax=merged_1.plot(zorder=1)
# dissolved_Bt_city_govt_health_facilities_1000m_buffer.plot(ax=ax,alpha=.5,zorder=2,color='red')
# plt.show()

# Excluding the land that is within a certain distance of existing hospitals

differenced_layer=difference(merged_1,dissolved_Bt_city_govt_health_facilities_1000m_buffer)

differenced_layer.to_file(r'scr\outputfiles\differenced_layer.shp')

# differenced_layer.plot()
# plt.show()


#dissolved_gdf=dissolve([differenced_layer])

#removing overlapping polygons
dissolved_gdf=dissolve([differenced_layer])
dissolved_gdf[0].plot()
plt.show()
dissolved_gdf[0].to_file('scr\outputfiles\dissolved.shp')
