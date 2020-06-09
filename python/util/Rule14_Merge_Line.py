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

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[525,666]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        #continue
                        pass
                    else:
                        print("="*30)
                        print("index:", idx)
                        for debug_idx in range(8):
                            print(debug_idx-2,": val#14:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

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
                    if is_debug_mode:
                        print("distance_full:",distance_full)
                        print("distance 1,2,(sum):",distance_1,distance_2,(distance_1+distance_2))
                        print("EUQAL_ACCURACY:", EUQAL_ACCURACY)
                    #is_match_pattern = True
                    if abs(distance_full - (distance_1+distance_2)) <= EUQAL_ACCURACY:
                        is_match_pattern = True

                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    if is_debug_mode:
                        print("slide_percent 1:", slide_percent_1)
                        print("slide_percent 1 dat:", format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])

                    if slide_percent_1 >= 1.99 and slide_percent_1 >= 1.99:
                        is_match_pattern = True


                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #14:", fail_code)
                    else:
                        print("="*30)
                        print("match rule #14:",idx)
                        print("currence code+0:", format_dict_array[idx]['code'])
                        print("currence code+1:", format_dict_array[idx_next1]['code'])

                if is_match_pattern:
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