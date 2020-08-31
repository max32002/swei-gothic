#!/usr/bin/env python3
#encoding=utf-8

# distance between two points
from math import hypot

def slide_percent(x1,y1,x2,y2,x3,y3):
    percent = -1
    distance_offset=200.0
    previous_x,previous_y=two_point_extend(x1,y1,x2,y2,-1 * distance_offset)
    next_x,next_y=two_point_extend(x3,y3,x2,y2,-1 * distance_offset)
    d3 = get_distance(previous_x,previous_y,next_x,next_y)
    if d3 > 0:
        percent = d3/distance_offset
        if percent > 2.0:
            percent = 2.0
    return percent

# PS: 呼叫函數前，請先確定 distance_offset 不為 0，因為無法判斷要放在 from 還是 end.
def two_point_extend(x1,y1,x2,y2,distance_offset):
    distance = get_distance(x1,y1,x2,y2)
    distance_percent = 1
    if distance_offset != 0 and distance != 0:
        distance_percent = (distance_offset / distance)

    x_offset = int((x2-x1) * distance_percent)
    y_offset = int((y2-y1) * distance_percent)
    
    # 斜線上的「內縮」的新坐標。
    new_x=x2+x_offset
    new_y=y2+y_offset

    return new_x,new_y


def is_xyz_on_line(x1,y1,x2,y2,x3,y3,accuracy=0.01):
    ret=False
    dist_1 = get_distance(x1,y1,x3,y3)
    dist_2 = get_distance(x2,y2,x3,y3)
    
    dist_compare = dist_1 + dist_2
    dist_full = get_distance(x2,y2,x1,y1)
    dist_diff = abs(dist_full-dist_compare)

    compare_accuracy = dist_full * accuracy
    if compare_accuracy <= 2:
        compare_accuracy = 2
        #distance too short, need more accuracy.
        if dist_full <= 100:
            compare_accuracy = 1
    
    #print("dist_full:", dist_full)
    #print("dist_compare:", dist_compare)
    #print("dist_diff:",dist_diff)
    #print("compare_accuracy:", compare_accuracy)

    if dist_diff <= compare_accuracy:
        ret = True
    return ret

def get_distance(x1,y1,x2,y2):
    dist = int(hypot(x2 - x1, y2 - y1))
    return dist

def average(lst): 
    return sum(lst) / len(lst) 

def is_same_direction_list(args,deviation=0):
    ret = True
    args_average=average(args)
    #print("args_average:", args_average)

    direction = -1
    if args[0] <= args_average:
        direction = 1
    
    idx=0
    args_count = len(args)
    for item in args:
        idx+=1
        if idx == args_count:
            break

        if direction==1:
            if (args[idx]+deviation)<item and (args[idx]-deviation)<item:
                ret = False
                break
        else:
            if (args[idx]+deviation)>item and (args[idx]-deviation)>item:
                ret = False
                break
    return ret

def is_same_direction(*args,deviation=0):
    return self.is_same_direction_list(args,deviation=deviation)

# common functions.
def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def field_right(s, first, is_include_symbol=False):
    try:
        start = s.index(first )
        if not is_include_symbol:
            start += len(first )
        return s[start:]
    except ValueError:
        return ""

def field_left(s, first, is_include_symbol=False):
    try:
        start = s.index(first )
        if is_include_symbol:
            start += len(first )
        return s[:start]
    except ValueError:
        return ""

def two_point_extend_next(x1,y1,x2,y2):
    new_x, new_y = x2,y2
    for distance_offset in range(2,12):
        new_x,new_y=two_point_extend(x1,y1,x2,y2,distance_offset)
        if not new_x == x2:
            break
        if not new_y == y2:
            break
    return new_x, new_y

# for test functions.
if __name__ == '__main__':
    x1,y1=1,1
    x2,y2=10,10
    
    distance_offset = 15
    distance = get_distance(x1,y1,x2,y2)
    print("distance:",distance)
    #distance_offset = distance
    new_x,new_y=two_point_extend(x2,y2,x1,y1,-1*distance_offset)
    print("new x,y:",new_x,new_y)
    
    #new_x,new_y=two_point_extend_next(x1,y1,x2,y2)
    #print("new x,y:",new_x,new_y)