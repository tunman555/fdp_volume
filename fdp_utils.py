import json
import math
from haversine import haversine,inverse_haversine,Direction
from plotly import graph_objs as go
import numpy as np

with open('./src/point.json','r') as f:
    point_json =json.load(f)
    
with open('./src/arc.json','r') as f:
    arc_json = json.load(f)


with open('./src/sector.json','r') as f:
    sector_json = json.load(f)
    
with open('./src/fdp_volume.json','r') as f:
    fdp_volume = json.load(f)

with open('./src/layer.json' , 'r') as f:
    layer_json = json.load(f)
    
def coor2dd(point):
    lat = point[:6]
    lon = point[7:14]
    lat_dms = (float(lat[:2]) + float(lat[2:4])/60 + float(lat[4:6])/(60*60))
    lon_dms = (float(lon[:3]) + float(lon[3:5])/60 + float(lon[5:7])/(60*60))
    return lat_dms,lon_dms

def latlon2xy(center,point):
    cen_lat,cen_lon = center[0],center[1]
    point_lat,point_lon = point[0],point[1]

    if  point_lat >= cen_lat and point_lon >= cen_lon :
        px = haversine((cen_lat,cen_lon),(cen_lat,point_lon))
        py = haversine((cen_lat,cen_lon),(point_lat,cen_lon))

    elif  point_lat >= cen_lat and point_lon <= cen_lon:
        px = -haversine((cen_lat,cen_lon),(cen_lat,point_lon))
        py = haversine((cen_lat,cen_lon),(point_lat,cen_lon))

    elif point_lat <= cen_lat and point_lon >= cen_lon:
        px = haversine((cen_lat,cen_lon),(cen_lat,point_lon))
        py = -haversine((cen_lat,cen_lon),(point_lat,cen_lon))

    else  :
        px = -haversine((cen_lat,cen_lon),(cen_lat,point_lon))
        py = -haversine((cen_lat,cen_lon),(point_lat,cen_lon))
    return px,py

def xy2latlon(center,point):
    cen_lat,cen_lon = center
    x,y =point[0],point[1]
    
    lon = inverse_haversine((center),x,Direction.EAST)[1]
    lat = inverse_haversine((center),y,Direction.NORTH)[0]
    return (lat,lon)

def get_new_center(start_xy,end_xy,r3):
    x1,y1 = start_xy[0],start_xy[1]
    x2,y2 = end_xy[0],end_xy[1]

    k = (x1**2 - x2**2 +y1**2 - y2**2)
    a = 4*((x1+x2)**2 + (y1+y2)**2)
    b = ((8*(x1+x2)*(y1+y2)*x1) - (4*k*(y1+y2)) - (8*((x1+x2)**2)))
    c =k**2 -(4*(x1+x2)*x1*k) + 4*((x1+x2)**2)*(x1**2 +y1**2 -r3**2)
    
    if b**2 -(4*a*c) < 0 :
        c =k**2 -(4*(x1-x2)*x1*k) - 4*((x1-x2)**2)*(x1**2 +y1**2 -r3**2)
        
    if  y1==y2:

        y3_1 = y1
        x3_1 = (x1 + x2)/2

        return (x3_1,y3_1)
    elif x1 == x2 :

        x3_1 = x1
        y3_1 = (y1 + y2)/2
        return (x3_1,y3_1)
    
    else:
        y3_1 = (-b + math.sqrt(b**2 -(4*a*c)) )/(2*a)
        y3_2 = (-b - math.sqrt(b**2 -(4*a*c)) )/(2*a)

        x3_1 = (k - (2*y3_1*(y1-y2)))/ (2*(x1-x2))
        x3_2 = (k - (2*y3_2*(y1-y2)))/ (2*(x1-x2))
    
    if x3_1 **2 + y3_1 **2 < x3_2 **2 + y3_2**2 :
        p3 = (x3_1,y3_1)
    else : 
        p3 = (x3_2,y3_2)
    return p3

def circle_intersect(p1,p2,r1,r2):
    x1,y1 = p1[0],p1[1]
    x2,y2 = p2[0],p2[1]
    
    Dx = x2-x1
    Dy = y2-y1
    D = round(math.sqrt(Dx**2 + Dy**2),5)
    
    chorddistance = (r1**2 - r2**2 +D**2)/(2*D)
    halfchordlength = math.sqrt(r1**2 - chorddistance**2)
    chordmidx = x1 + (chorddistance*Dx)/D
    chordmidy = y1 + (chorddistance*Dy)/D
    
    I1 = (round(chordmidx + (halfchordlength*Dy)/D, 5),
          round(chordmidy - (halfchordlength*Dx)/D, 5))
    theta1 = round(math.degrees(math.atan2(I1[1]-y1, I1[0]-x1)),5)
    I2 = (round(chordmidx - (halfchordlength*Dy)/D, 5),
          round(chordmidy + (halfchordlength*Dx)/D, 5))
    theta2 = round(math.degrees(math.atan2(I2[1]-y1, I2[0]-x1)),5)

    return (I2, I1)

def get_arc(p_start,p_stop,center,n):
    """
    all arguments are in cartesian coordinate
    """
    #r = round(math.sqrt((p_start[0] - center[0])**2 + (p_start[1] - center[1])**2),5)
    #c = round(math.sqrt((p_start[0] - p_stop[0])**2 + (p_start[1] - p_stop[1])**2),5)
    #theta =  math.degrees(math.acos((2*r**2 - c**2) /(2*r**2)))
    a = round(math.sqrt((p_start[0] - center[0])**2 + (p_start[1] - center[1])**2),5)
    b = round(math.sqrt((p_stop[0] - center[0])**2 + (p_stop[1] - center[1])**2),5)
    c = round(math.sqrt((p_start[0] - p_stop[0])**2 + (p_start[1] - p_stop[1])**2),5)

    theta =  math.degrees(math.acos(round((a**2 + b**2 - c**2)/(2*a*b),5)))
    
    #r2 = math.sqrt((2*r**2) * (1-math.cos(math.radians(theta/n))))
    r2 = math.sqrt((2*a**2) * (1-math.cos(math.radians(theta/n))))
    
    tmp_p2 = p_start
    arc_point = []
    for i in range(n-1):
        #target = circle_intersect(center,tmp_p2,r,r2)[1]
        target = circle_intersect(center,tmp_p2,a,r2)[1]
        arc_point.append(target)
        tmp_p2 = target

    return  arc_point

def get_arc_list_coor(arc_name):
    """ Create a list of arc by estimating a curve on circle"""
    arc = arc_json[arc_name]

    start_point = coor2dd(point_json[arc['start_point']])
    end_point = coor2dd(point_json[arc['end_point']])
    center_point = coor2dd(arc['center_point'])
    
    start_xy = latlon2xy(center_point,start_point)
    end_xy = latlon2xy(center_point,end_point)
    
    r1 = round(math.sqrt(start_xy[0]**2 + start_xy[1]**2),5)
    r2 = round(math.sqrt(end_xy[0]**2 + end_xy[1]**2),5)
    r3 = (r1 + r2) / 2

    center = get_new_center(start_xy,end_xy,r3) # The center that two points were cross by
    
    arc_list = get_arc(start_xy,end_xy,center,20)
    new_center = xy2latlon(center_point,center)
    
    #arc_coor = arc_list_to_coor(center_point,arc_list) 
    arc_coor = arc_list_to_coor(center_point,arc_list) 
        
    return arc_coor

def arc_list_to_coor(center,arc_list):
    """ Convert a list of arc to dd lat lon"""
    arc_list_coor = []
    for point in arc_list:
        coor = xy2latlon(center,point)
        arc_list_coor.append(coor)
    return arc_list_coor

def add_start_end(arc_list,start_point,end_point):
	lat,lon = [],[]

	lat.append(start_point[0])
	lon.append(start_point[1])

	for i in arc_list:
	    lat.append(i[0])
	    lon.append(i[1])
	    

	lat.append(end_point[0])
	lon.append(end_point[1])
	return (lat,lon)

def get_polygon(volume_name):
    """ 
    create polygon from volume name in LAT LON 
    """
    points = fdp_volume[volume_name]['points']
    polygon_list = []
    for i,point in enumerate(points):

        if point in point_json:
            p = point_json[point]
            coor = coor2dd(p)
            polygon_list.append(coor)
        else :
            before_point = points[i-1]
            after_point = points[i+1]
            arc_list = get_arc_polygon(point)

            if chk_ccw(before_point,point,after_point):

                arc_list.reverse()
            polygon_list = polygon_list + arc_list 
    return polygon_list

def chk_ccw(before_point,arc_name,after_point):
    start_point = arc_json[arc_name]['start_point']
    end_point = arc_json[arc_name]['end_point']

    if start_point != before_point and after_point != end_point:
        return True
    else :
        return False

def get_arc_polygon(point):
    arc_list = get_arc_list_coor(point)
    start_point = coor2dd(point_json[arc_json[point]['start_point']])
    end_point = coor2dd(point_json[arc_json[point]['end_point']])
    
    arc_list.insert(0,start_point)
    arc_list.append(end_point)
    
    return arc_list

def find_center_and_max(polygon):
    center={}
    max_lat,max_lon = polygon[0][0],polygon[0][1]
    min_lat,min_lon = polygon[0][0],polygon[0][1]
    for i in polygon:
        if i[0] > max_lat : max_lat=i[0]
        if i[1] > max_lon :max_lon =i[1]
        if i[0] <min_lat : min_lat =i[0]
        if i[1] <min_lon :min_lon =i[1]
    center['lat'] = (min_lat + max_lat)/2    
    center['lon'] = (min_lon + max_lon)/2
    return center,(min_lat,min_lon),(max_lat,max_lon)

def get_zoom(min_,max_):
    max_bound = max(abs(max_[0]-min_[0]), abs(max_[1]-min_[1])) * 111
    zoom = 11.5 - np.log(max_bound)
    return zoom 

def create_volume_plot(volume_name):
    polygon=get_polygon(volume_name)
    center,min_,max_ = find_center_and_max(polygon)
    zoom = get_zoom(min_,max_)

    poly_plot=[]
    for i in polygon:
        poly_plot.append([[i][0][1],[i][0][0]])
    
    mapbox_token=open('./mapbox_token.txt').read().strip()
    
    fig = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = [center['lon']], lat = [center['lat']],
    marker = {'size': 1, 'color': ["cyan"]}))

    fig.update_layout(mapbox_accesstoken=mapbox_token,
        mapbox = {
            'style': "dark",
            'center': center,
            'zoom': zoom, 'layers': [{
                'source': {
                    'type': "FeatureCollection",
                    'features': [{
                        'type': "Feature",
                        'geometry': {
                            'type': "MultiPolygon",
                            'coordinates': [[poly_plot]]
                        }
                    }]
                },
                'opacity':0.3,'type': "fill", 'below': "traces", 'color': "red"}]},
        margin = {'l':0, 'r':0, 'b':0, 't':0})
        
    return fig

def get_box(layer):
    if "-" in layer :
        start = layer.split('-')[0]
        stop = layer.split('-')[1]
        
        return (layer_json[start]['lower'],layer_json[stop]['upper'])
    else:
        return layer_json[layer]['lower'],layer_json[layer]['upper']

def get_latlon(polygon_list):
    lat,lon=[],[]
    for i in polygon_list:
        for j in i:
            lat.append(j[0])
            lon.append(j[1])
        lat.append(None)
        lon.append(None)
    return lat,lon

def find_center_sector(lat,lon):
    center={}
    max_lat,max_lon = lat[0],lon[0]
    min_lat,min_lon = lat[0],lon[0]
    for i,j in zip(lat,lon):

        if i ==None :continue
        if i > max_lat : 
            max_lat=i
        if j > max_lon :
            max_lon =j
        if i <min_lat : 
            min_lat =i
        if j <min_lon :
            min_lon =j

    center['lat'] = (min_lat + max_lat)/2    
    center['lon'] = (min_lon + max_lon)/2
    return center,(min_lat,min_lon),(max_lat,max_lon)


def create_sector_plot(sector_name):
    volume_list = sector_json[sector_name]['volume']
    polygon_list = []

    for volume_name in volume_list:
        polygon_list.append(get_polygon(volume_name))

    lat,lon = get_latlon(polygon_list)
    center,min_,max_ = find_center_sector(lat,lon)
    zoom = get_zoom(min_,max_)

    mapbox_token=open('./mapbox_token.txt').read().strip()

    fig = go.Figure(go.Scattermapbox(
    mode = "lines",fill="toself",opacity=0.1,
    lon = lon, lat = lat))

    fig.update_layout(mapbox_accesstoken=mapbox_token,
        mapbox = {'style': "dark", 'center': {'lon': center['lon'], 'lat': center['lat']}, 'zoom': zoom},
        showlegend = False,
        margin = {'l':0, 'r':0, 'b':0, 't':0})

    return fig

def update_dataset():

    f = open('./tmp/datasets.asf','r')
    
    txt = f.read().splitlines()
    lines =[]
    for line in txt:
        if line[:2] != '--':
             lines.append(line)

    for index,line in enumerate(lines) :
        if "/POINTS/" in line:
            start_point=index
        if "/ARCS/" in line:
            end_point=index
        if "/ARCS/" in line:
            start_arc=index
        if "/RHUMB_LINES/" in line:
            end_arc=index
        if "/VOLUME/" in line:
            start_volume=index
        if "/SECTOR/" in line:
            end_volume=index
        if "/SECTOR/" in line:
            start_sec=index
        if "/MIL_AREA/" in line:
            end_sec=index
        if "/LAYER/" in line:
            start_layer=index
        if "/VOLUME/" in line:
            end_layer=index
        
    layer_txt = lines[start_layer+1 :end_layer-1]
    point_txt=lines[start_point+1 :end_point-1]
    arc_txt=lines[start_arc+1 :end_arc-1]
    volume_txt= lines[start_volume+1 :end_volume-1]
    sector_txt = lines[start_sec+1 :end_sec-1]

    fdp_volume = {}

    for index,line in enumerate(volume_txt):
        if line[:2] == "--": continue
        if line.count("|") !=2:continue
        
        first_item = line.split('|')[0]
        if not first_item.isspace() :
            i=1
            volume_name = line.split('|')[0].strip()
            level = line.split('|')[1].strip()
            points = line.split('|')[2]
            points_list = points.split()
            
            fdp_volume[volume_name] = {}
            fdp_volume[volume_name]['level'] = level
            fdp_volume[volume_name]['points'] = points_list        
            
            while volume_txt[index + i][:2] != "--" and volume_txt[index + i].split('|')[0].isspace() and volume_txt[index + i].count("|")==2:
                if index+i == len(volume_txt)-1: 
                    break
                points = volume_txt[index+i].split('|')[2]
                points_list = points.split()
                fdp_volume[volume_name]['points'].extend(points_list)
                i = i+1

    arc_json={}
    for index,arc in enumerate(arc_txt):
        if arc[:2] =="--" or arc=="" or arc=="  ":
            continue
        arc_name = arc.split('|')[0].strip()
        start_point = arc.split('|')[1].strip()
        end_point = arc.split('|')[2].strip()
        center_point = arc.split('|')[3].strip()
        
        arc_json[arc_name] = {}
        arc_json[arc_name]['start_point'] = start_point
        arc_json[arc_name]['end_point'] = end_point
        arc_json[arc_name]['center_point'] = center_point

    with open("./tmp/arc.json","w") as outfile:
        json.dump(arc_json,outfile)

    point_json={}
    for index,point in enumerate(point_txt):
        if point[:2] =="--" or point=="                                               " or point=="" or point=="                            ":
            continue
        point_name = point.split('|')[0].strip()
        coor = point.split('|')[1].strip()

        point_json[point_name] = coor

    with open("./tmp/point.json","w") as outfile:
        json.dump(point_json,outfile)

    sector_json={}

    for index,line in enumerate(sector_txt):
        if line[:2] == "--": continue
        if line.count("|") !=2:continue
        
        first_item = line.split('|')[0]
        if not first_item.isspace() :
            i=1
            sector_name = line.split('|')[0].strip()
            
            volumes = line.split('|')[2].strip()
            volume_list = [s.strip() for s in volumes.split('+')]
            if len(volume_list[-1].split()) > 1 :
                tmp = volume_list[-1].split()[0]
                volume_list[-1] = tmp
            sector_json[sector_name] = {}

            sector_json[sector_name]['volume'] = volume_list
            
            while index != len(sector_txt) -1 and sector_txt[index + i][:2] != "--" and sector_txt[index + i].split('|')[0].isspace() and sector_txt[index + i].count("|")==2: 
                volumes = sector_txt[index+i].split('|')[2].strip()
                volume_list = [ s.strip() for s in volumes.split('+')]
                if len(volume_list[-1].split()) !=1 :
                    tmp = volume_list[-1].split()[0]
                    volume_list[-1] = tmp
                volume_list =filter(None,volume_list)
                sector_json[sector_name]['volume'].extend(volume_list)
                i= i+1

    with open('./tmp/sector.json','w') as outfile:
        json.dump(sector_json,outfile)

    layer_json = {}
    for line in layer_txt :
        if line =='' or line[:2]=="--": continue
        layer = line.split('|')[0].strip()
        layer_json[layer] = {}
        start_fl = line.split('|')[2].split()[1]
        end_fl = line.split('|')[2].split()[3]
        layer_json[layer]['lower'] =  start_fl
        layer_json[layer]['upper'] =  end_fl

    with open('./tmp/layer.json','w') as outfile:
        json.dump(layer_json,outfile)

        