import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, MultiPolygon


South_mw_pop=gpd.read_file('data\south_mw_pop.shp')
BT_city_landuse_general=gpd.read_file('data\BT_landuse_general.shp')
BT_city_HCs=gpd.read_file('data\BT_city_HCs.gpkg')
BT_city_roads=gpd.read_file('data\BT_city_roads.gpkg')

# converting shapefiles to to_WGS_1984_UTM_Zone_36S

def to_WGS_1984_UTM_Zone_36S(shapeFiles, projection= 'EPSG:32736'):
    try:
        for shapeFile in shapeFiles:
            shapeFile.crs=projection            
    except Exception:
        print("error creating projection")

def merge(shapeFile1,shapeFile2):    
    if shapeFile2.crs != shapeFile1.crs:
        to_WGS_1984_UTM_Zone_36S([shapeFile1,shapeFile2])
    return gpd.overlay(shapeFile1, shapeFile2, how='union', keep_geom_type=False)

def difference(shapeFile1, shapeFile2):
    if shapeFile2.crs != shapeFile1.crs:
        to_WGS_1984_UTM_Zone_36S([shapeFile1,shapeFile2])
    return gpd.overlay(shapeFile1,shapeFile2, how='difference', keep_geom_type=False) 
    
to_WGS_1984_UTM_Zone_36S([South_mw_pop,BT_city_landuse_general,BT_city_HCs,BT_city_roads])

'''
brainStorm

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

BT_roads_100m_buffer=BT_city_roads.buffer(100)
BT_residential_100m_buffer=BT_residential.buffer(100)
Bt_city_govt_health_facilities_1000m_buffer=BT_city_govt_hospitals.buffer(1000)

#dissolving and visualization :

dissoved_BT_roads_100m_buffer=BT_roads_100m_buffer.to_frame().dissolve(as_index=False)
dissoved_BT_residential=BT_residential_100m_buffer.to_frame().dissolve(as_index=False)
dissolved_Bt_city_govt_health_facilities_1000m_buffer=Bt_city_govt_health_facilities_1000m_buffer.to_frame().dissolve(as_index=False)


#----------------------------------------------------------------

merged_1=merge(dissoved_BT_residential,dissoved_BT_roads_100m_buffer)

merged_1.to_file('scr\outputfiles\merged_1.shp')
# ax=merged_1.plot(zorder=1)
# dissolved_Bt_city_govt_health_facilities_1000m_buffer.plot(ax=ax,alpha=.5,zorder=2,color='red')
# plt.show()

differenced_layer=difference(merged_1,dissolved_Bt_city_govt_health_facilities_1000m_buffer)

dissolved_gdf=differenced_layer.dissolve(as_index=False)
differenced_layer.to_file('scr\outputfiles\differenced_layer.shp')
dissolved_gdf.plot()
plt.show()



print(differenced_layer.columns)



