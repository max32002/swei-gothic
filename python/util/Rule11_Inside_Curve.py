#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 11
# check inside curve
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
        redo_travel=False

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 3
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                if format_dict_array[(idx+0)%nodes_length]['code']=='c':
                    x0 = format_dict_array[(idx+0)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+0)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['code']=='c':
                    x2 = format_dict_array[(idx+0)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+0)%nodes_length]['y1']

                # debug purpose:
                #if not(x1==842 and y1==753):
                #if not(x1==772 and y1==693):
                #if not(x1==630 and y1==580):
                #if not(x1==699 and y1==247):
                #if False:
                    #continue

                #if not([x1,y1]==[535,647]) :
                    #continue

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                #if format_dict_array[(idx+0)%nodes_length]['x']==806:
                #if True:
                if False:
                    print("-" * 20)
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])

                # match
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    fail_code = 100
                    is_match_pattern = True

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= self.config.ROUND_OFFSET:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= self.config.ROUND_OFFSET:
                            is_match_pattern = True

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                if is_match_pattern:
                    fail_code = 300
                    previous_x,previous_y=spline_util.two_point_extend(x0,y0,x1,y1,-1 * self.config.OUTSIDE_ROUND_OFFSET)
                    next_x,next_y=spline_util.two_point_extend(x2,y2,x1,y1,-1 * self.config.OUTSIDE_ROUND_OFFSET)
                    d3 = spline_util.get_distance(previous_x,previous_y,next_x,next_y)
                    if d3 <= self.config.OUTSIDE_ROUND_OFFSET * 0.5:
                        #print("match too small angel.")
                        is_match_pattern = False

                    # skip almost line triangle
                    if is_match_pattern:
                        fail_code = 310
                        if d3 >= self.config.OUTSIDE_ROUND_OFFSET * 1.5:
                            is_match_pattern = False

                # stroke in while area. @_@;
                is_apply_large_corner = False
                if is_match_pattern:
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                            inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_MIN, inside_stroke_dict)
                            if inside_stroke_flag:
                                is_apply_large_corner = True
                                #print("match is_apply_large_corner:",x1,y1)

                if not is_apply_large_corner:
                    if is_match_pattern:
                        fail_code = 400
                        is_match_pattern = False

                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2)
                        #print("check1_flag:",join_flag)
                        if not join_flag:
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            #print("check2_flag:",join_flag)

                        #print("final join flag:", join_flag)
                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass

                if not is_match_pattern:
                    #print(idx,"debug fail_code #5:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #11")
                    #print(idx,"debug rule11+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule11+1:",format_dict_array[(idx+1)%nodes_length]['code'])
                    #print(idx,"debug rule11+2:",format_dict_array[(idx+2)%nodes_length]['code'])

                    # make coner curve
                    round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    if not is_apply_large_corner:
                        round_offset = self.config.INSIDE_ROUND_OFFSET

                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx)

                    # cache transformed nodes.
                    # we generated nodes
                    # 因為只有作用在2個coordinate. 
                    skip_coordinate.append([previous_x,previous_y])

                    redo_travel=True

                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx
                    break
                    #redo_travel=True
                    #resume_idx = -1
                    #break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
