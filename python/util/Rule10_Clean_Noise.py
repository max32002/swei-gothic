#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 10
# 奇怪的 Noise
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx):
        redo_travel=False

        NOISE_DISTANCE = 4

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

                is_match_pattern = False

                #print(idx,": debug rule10:",format_dict_array[idx]['code'])

                x0 = format_dict_array[idx]['x']
                y0 = format_dict_array[idx]['y']

                idx_next = (idx + 1) % nodes_length
                x1 = format_dict_array[idx_next]['x']
                y1 = format_dict_array[idx_next]['y']

                compare_distance = spline_util.get_distance(x0,y0,x1,y1)
                if compare_distance <= NOISE_DISTANCE:
                    is_match_pattern = True

                if False:
                    print("-------------------------------")
                    for debug_idx in range(6):
                        print(debug_idx-2,": values for rule10:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'])


                if is_match_pattern:
                    #print("match rule #10")
                    #print(idx,": debug rule10:",format_dict_array[idx]['code'])
                    del format_dict_array[idx_next]

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