#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 7
# 「多」字右上角的小帽子
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, skip_coordinate):
        redo_travel=False

        CAP_HEIGHT_DISTANCE = 18

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 5
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                is_match_pattern = False

                #print(idx,"debug rule7:",format_dict_array[idx]['code'])

                # match: ?lllc
                
                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                if False:
                    print("-------------------------------")
                    for debug_idx in range(6):
                        print(debug_idx-2,"values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])

                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+3)%nodes_length]['t'] == 'l':
                            #if format_dict_array[(idx+4)%nodes_length]['t'] == 'c':
                            fail_code = 100
                            is_match_pattern = True

                # compare stroke_width
                if is_match_pattern:
                    #print(idx,"debug rule7:",format_dict_array[idx]['code'])
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+2)%nodes_length]['match_stroke_width']:
                        is_match_pattern = True
                    else:
                        # 這樣也可以，因為角度太小。
                        distance_1_to_3 = spline_util.get_distance(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                        #print("distance_1_to_3:", distance_1_to_3)
                        if distance_1_to_3 >= self.config.STROKE_WIDTH_MIN and distance_1_to_3 <= self.config.STROKE_WIDTH_MAX:
                            is_match_pattern = True


                # compare CAP_HEIGHT_DISTANCE
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    #print("format_dict_array[(idx+1)%nodes_length]['distance']:", format_dict_array[(idx+1)%nodes_length]['distance'])
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= CAP_HEIGHT_DISTANCE:
                        is_match_pattern = True

                # compare direction
                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0 :
                        if format_dict_array[(idx+1)%nodes_length]['x_direction'] > 0 :
                            if format_dict_array[(idx+2)%nodes_length]['x_direction'] > 0 :
                                if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                                    if format_dict_array[(idx+1)%nodes_length]['y_direction'] > 0 :
                                        if format_dict_array[(idx+2)%nodes_length]['y_direction'] < 0 :
                                            if format_dict_array[(idx+3)%nodes_length]['y_direction'] < 0 :
                                                if format_dict_array[(idx+3)%nodes_length]['x_direction'] < 0 :
                                                    is_match_pattern = True
                if not is_match_pattern:
                    #print(idx,"debug fail_code7:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #7")
                    #print(idx,"debug rule7:",format_dict_array[idx]['code'])

                    center_x = int((format_dict_array[(idx+2)%nodes_length]['x']+format_dict_array[(idx+3)%nodes_length]['x'])/2)
                    #center_y = int((format_dict_array[(idx+2)%nodes_length]['y']+format_dict_array[(idx+3)%nodes_length]['y'])/2)
                    center_y = format_dict_array[(idx+2)%nodes_length]['y']+3
                    #print("center x,y:", center_x, center_y)

                    x0 = format_dict_array[(idx+1)%nodes_length]['x']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y']
                    x1 = format_dict_array[(idx+2)%nodes_length]['x']
                    y1 = format_dict_array[(idx+2)%nodes_length]['y']
                    
                    x0_offset = format_dict_array[(idx+1)%nodes_length]['x'] - x0
                    y0_offset = format_dict_array[(idx+1)%nodes_length]['y'] - y0

                    x2 = format_dict_array[(idx+3)%nodes_length]['x']
                    y2 = format_dict_array[(idx+3)%nodes_length]['y']
                    x2_offset = 0
                    y2_offset = 0

                    #print("new offset0:", x0_offset, y0_offset)
                    #print("new offset2:", x2_offset, y2_offset)

                    # 斜線上的「內縮」的新坐標。
                    new_x1=x0+x0_offset
                    new_y1=y0+y0_offset
                    new_x2=x2+x2_offset
                    new_y2=y2+y2_offset
                    #print("new x1,y1:", new_x1, new_y1)
                    #print("new x2,y2:", new_x2, new_y2)

                    center_x_p0 = int((center_x + new_x1)/2) - 3
                    center_x_p2 = int((center_x + new_x2)/2) + 3
                    center_y_p0 = int((center_y + new_y1)/2) - 3
                    center_y_p2 = int((center_y + new_y2)/2) + 3

                    # re-center again
                    #center_x = int((new_x1+new_x2)/2)

                    # update #2
                    new_code = ' %d %d %d %d %d %d c 1\n' % (center_x_p0, center_y + 1, center_x_p0, center_y+1, center_x, center_y)
                    dot_dict={}
                    dot_dict['x']=center_x
                    dot_dict['y']=center_y
                    dot_dict['t']='c'
                    dot_dict['code']=new_code
                    format_dict_array[(idx+2)%nodes_length]=dot_dict

                    # append new #3
                    end_x = format_dict_array[(idx+3)%nodes_length]['x']
                    end_y = format_dict_array[(idx+3)%nodes_length]['y']
                    new_code = ' %d %d %d %d %d %d c 1\n' % (center_x_p2, center_y_p2, center_x_p2, center_y_p2, new_x2, new_y2)
                    dot_dict={}
                    dot_dict['x']=new_x2
                    dot_dict['y']=new_y2
                    dot_dict['t']='c'
                    dot_dict['code']=new_code
                    format_dict_array[(idx+3)%nodes_length]=dot_dict

                    # cache transformed nodes.
                    skip_coordinate.append([format_dict_array[idx]['x'],format_dict_array[idx]['y']])
                    # we generated nodes
                    skip_coordinate.append([center_x,center_y])
                    # next_x,y is used for next rule!
                    #skip_coordinate.append([new_x2,new_y2])

                    redo_travel=True
                    #resume_idx = -1
                    resume_idx = idx
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, skip_coordinate
