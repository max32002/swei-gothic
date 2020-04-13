#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 4
# format curve coner as l conver
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx):
        redo_travel=False

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        EXPAND_MARGIN_ACCURACY = 0.03
        DISTANCE_IN_LINE_ACCURACY = 0.05

        # becasue of our new curve is regular triangle
        # skip merge this type of line.
        # PS: no used for NOW!
        REGULAR_TRIANGLE_RATE = 0.85

        rule_need_lines = 4
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_match_pattern = False

                #print(idx,"debug rule4:",format_dict_array[idx]['code'])
                
                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                if False:
                    print("-------------------------------")
                    for debug_idx in range(6):
                        print(debug_idx-2,"values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])

                #if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                        fail_code = 100
                        is_match_pattern = True

                # compare stroke_width
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                        is_match_pattern = True

                # compare NEXT_DISTANCE_MIN
                if is_match_pattern:
                    fail_code = 210
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.NEXT_DISTANCE_MIN:
                        is_match_pattern = True

                # compare direction
                if is_match_pattern:
                    #print(idx,"debug rule4:",format_dict_array[idx]['code'])
                    fail_code = 400
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                        # x 要相反，y 要相反！
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['y_direction']:
                            is_match_pattern = True
                        
                    # 水平線也OK.
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy'] and format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                        is_match_pattern = True
                    # vertical line 線也OK.
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy'] and format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                        is_match_pattern = True

                x1 = 0
                y1 = 0
                x2 = 0
                y2 = 0

                # compare internal value
                # to avoid destory our new curvy.
                if is_match_pattern:
                    #print(idx,"debug rule4:",format_dict_array[idx]['code'])
                    fail_code = 500
                    is_match_pattern = False

                    x1 = format_dict_array[(idx+1)%nodes_length]['x']
                    y1 = format_dict_array[(idx+1)%nodes_length]['y']
                    x2 = format_dict_array[(idx+2)%nodes_length]['x']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y']
                    dist_total = format_dict_array[(idx+1)%nodes_length]['distance']

                    x_max = x1
                    x_min = x1
                    if x2 > x1:
                        x_max=x2
                    else:
                        x_min=x2

                    y_max = y1
                    y_min = y1
                    if y2 > y1:
                        y_max=y2
                    else:
                        y_min=y2

                    # allow some accuracy
                    x_min = x_min - (EXPAND_MARGIN_ACCURACY * dist_total)
                    x_max = x_max + (EXPAND_MARGIN_ACCURACY * dist_total)
                    y_min = y_min - (EXPAND_MARGIN_ACCURACY * dist_total)
                    y_max = y_max + (EXPAND_MARGIN_ACCURACY * dist_total)

                    # all value in between.
                    #print("x_min,x_max:",x_min,x_max)
                    #print("y_min,y_max:",y_min,y_max)
                    
                    #print(idx,"debug rule4:",format_dict_array[(idx+2)%nodes_length]['code'])
                    x2_1 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2_1 = format_dict_array[(idx+2)%nodes_length]['y1']
                    x2_2 = format_dict_array[(idx+2)%nodes_length]['x2']
                    y2_2 = format_dict_array[(idx+2)%nodes_length]['y2']

                    is_all_in_range = False
                    # basic compare
                    if x2_1 > x_min and x2_1 < x_max:
                        if y2_1 > y_min and y2_1 < y_max:
                            if x2_2 > x_min and x2_2 < x_max:
                                if y2_2 > y_min and y2_2 < y_max:
                                    is_all_in_range = True

                    # dot in line compare
                    if is_all_in_range:
                        dist_xy1_1 = spline_util.get_distance(x2,y2,x2_1,y2_1)
                        dist_xy1_2 = spline_util.get_distance(x1,y1,x2_1,y2_1)
                        dist_xy2_1 = spline_util.get_distance(x2,y2,x2_2,y2_2)
                        dist_xy2_2 = spline_util.get_distance(x1,y1,x2_2,y2_2)

                        dist_xy1_total = dist_xy1_1 + dist_xy1_2
                        dist_xy2_total = dist_xy2_1 + dist_xy2_2
                        #print("dist_xy1_total:", dist_xy1_total)
                        #print("dist_xy2_total:", dist_xy2_total)
                        #print("dist_total:", dist_total)
                        if abs(dist_total-dist_xy1_total) <= dist_total * DISTANCE_IN_LINE_ACCURACY:
                            if abs(dist_total-dist_xy2_total) <= dist_total * DISTANCE_IN_LINE_ACCURACY:
                                is_match_pattern = True
                                pass

                # compare regular triangle
                # but some regular triangle is we want.
                #if is_match_pattern:
                if False:
                    #print(idx,"debug rule4:",format_dict_array[idx]['code'])
                    fail_code = 600
                    #is_match_pattern = False

                    diff_x = abs(x2-x1)
                    diff_y = abs(y2-y1)

                    if is_match_pattern:
                        if diff_y < 10 and diff_x < 10:
                            # too small range skip
                            is_match_pattern = False

                    if is_match_pattern:
                        if diff_y > 60 and diff_x > 60:
                            # too large range skip
                            is_match_pattern = False

                    if is_match_pattern:
                        if diff_y > 0 and diff_x >0:
                            diff_rate = diff_x / diff_y
                            if diff_rate > REGULAR_TRIANGLE_RATE:
                                # it's our new curve, skip
                                is_match_pattern = False


                if not is_match_pattern:
                    #print(idx,"debug fail_code3:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #4")
                    #print(idx,"debug rule4:",format_dict_array[idx]['code'])

                    # update #1
                    new_x = format_dict_array[(idx+2)%nodes_length]['x']
                    new_y = format_dict_array[(idx+2)%nodes_length]['y']
                    format_dict_array[(idx+2)%nodes_length]['t']= 'l'
                    old_code_string = " %d %d l 1\n" % (new_x, new_y)
                    format_dict_array[(idx+2)%nodes_length]['x']=new_x
                    format_dict_array[(idx+2)%nodes_length]['y']=new_y
                    format_dict_array[(idx+2)%nodes_length]['code'] = old_code_string

                    redo_travel=True
                    resume_idx = -1
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx
