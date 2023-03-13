import json
import math
from haversine import haversine,inverse_haversine,Direction

with open('./point.json','r') as f:
    point_json =json.load(f)
    
with open('arc.json','r') as f:
    arc_json = json.load(f)


with open('./sector.json','r') as f:
    sector_json = json.load(f)
    
with open('./fdp_volume.json','r') as f:
    fdp_volume = json.load(f)

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
    if theta2 > theta1:
        I1, I2 = I2, I1
        
    return (I1, I2)

def get_arc(p_start,p_stop,center,n):
    """
    all arguments are in cartesian coordinate
    """

    a = round(math.sqrt((p_start[0] - center[0])**2 + (p_start[1] - center[1])**2),5)
    b = round(math.sqrt((p_stop[0] - center[0])**2 + (p_stop[1] - center[1])**2),5)
    c = round(math.sqrt((p_start[0] - p_stop[0])**2 + (p_start[1] - p_stop[1])**2),5)

    theta =  math.degrees(math.acos(round((a**2 + b**2 - c**2)/(2*a*b),5)))

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
    #center = (0,0)
    center = ((start_xy[0] +  end_xy[0])/2,  (start_xy[1] +  end_xy[1])/2 )
    
    arc_list = get_arc(start_xy,end_xy,center,20)
    
    #new_center_point = ((start_point[0] + end_point[0])/2 , (start_point[1] + end_point[1]) /2)
    arc_coor = arc_list_to_coor(center_point,arc_list) 
    
    arc_list_offset = []

    for i in arc_list:
        x_offset = i[0] - center[0]
        y_offset = i[1] - center[1]
        arc_list_offset.append((x_offset,y_offset))
        
    return arc_coor

def arc_list_to_coor(center,arc_list):
    """ Convert a list of arc to dd lat lon"""
    arc_list_coor = []
    for point in arc_list:
        coor = xy2latlon(center,point)
        arc_list_coor.append(coor)
    return arc_list_coor

def add_start_end(arc_list,start_point,end_point):
	x,y = [],[]
	x.append(start_point[0])
	y.append(start_point[1])

	for i in arc_list:
	    x.append(i[0])
	    y.append(i[1])
	    

	x.append(end_point[0])
	y.append(end_point[1])
	return (x,y)
