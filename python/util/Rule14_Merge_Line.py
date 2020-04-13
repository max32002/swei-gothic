#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 14
# 有 first point 的關係，有時會有一小段的直線。
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx):
        redo_travel=False

        EUQAL_ACCURACY = 2

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)

        rule_need_lines = 5
        fail_code = -1
        #print("nodes_length:", nodes_length)
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                #print(idx,": debug rule14:",format_dict_array[idx]['code'])

                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']]==[341,405]) :
                    #continue

                #if True:
                if False:
                    print("-" * 20)
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule5:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False


                x0 = format_dict_array[idx]['x']
                y0 = format_dict_array[idx]['y']
                #x1 = self.config.DEFAULT_COORDINATE_VALUE
                #y1 = self.config.DEFAULT_COORDINATE_VALUE

                idx_next1 = (idx + 1) % nodes_length
                x1 = format_dict_array[idx_next1]['x']
                y1 = format_dict_array[idx_next1]['y']

                idx_next2 = (idx + 2) % nodes_length
                x2 = format_dict_array[idx_next2]['x']
                y2 = format_dict_array[idx_next2]['y']

                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        fail_code = 100
                        is_match_pattern = True

                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False

                    distance_1 = format_dict_array[idx]['distance']
                    distance_2 = format_dict_array[idx_next1]['distance']
                    distance_full = spline_util.get_distance(x0,y0,x2,y2)
                    #print("distance 1,2,3:",distance_1,distance_2,distance_full)
                    #is_match_pattern = True
                    if abs(distance_full - (distance_1+distance_2)) <= EUQAL_ACCURACY:
                        is_match_pattern = True

                if not is_match_pattern:
                    #print(idx,"debug fail_code #14:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #14")
                    #print(idx,": debug rule14:",format_dict_array[idx]['code'])

                    del format_dict_array[idx_next1]

                    redo_travel=True
                    #resume_idx = idx
                    #index changed!
                    resume_idx = -1
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)

        # for debug
        #redo_travel=False

        return redo_travel, resume_idx