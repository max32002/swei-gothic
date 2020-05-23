#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 22
# 糸 和 厶 左下角內縮造成凹進去的洞。
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
        redo_travel=False
        check_first_point = False

        # default: 1.26
        SLIDE_1_PERCENT_MIN = 1.11
        SLIDE_1_PERCENT_MAX = 1.41
        # default: 1.96
        SLIDE_2_PERCENT_MIN = 1.86
        SLIDE_2_PERCENT_MAX = 2.0
        # default: 1.93
        SLIDE_3_PERCENT_MIN = 1.83
        SLIDE_3_PERCENT_MAX = 2.0

        # default: 1.74
        SLIDE_10_PERCENT_MIN = 1.64
        SLIDE_10_PERCENT_MAX = 1.84

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)

        #print("hello, rule#22...")

        rule_need_lines = 7
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[93,481]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": values for rule#21:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip dot +2:",[format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']])
                        pass
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip dot +3:",[format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y']])
                        pass
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip dot +0:",[format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y']])
                        pass
                    continue


                is_match_pattern = True

                # match: ccccccc?
                # case: 繈 uni7E48
                # 0: 81 475 81 475 93 481 c 1
                # 1: 64 466 64 466 52 497 c 1       # center point
                # 2: 41 529 41 529 74 536 c 1       # fix point
                # 3: 78 537 71 551 88 585 c 0
                # 4: 107 614 107 614 141 690 c 128
                # 5: 175 766 175 766 186 805 c 1
                # 6: 194 837 194 837 227 824 c 1    # center point
                # 7: 260 812 260 812 249 781 c 1
                # 8: 199 643 196 645 132 542 c 1


                if is_match_pattern:
                    fail_code = 100
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                            if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                                if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                                    if format_dict_array[(idx+4)%nodes_length]['t'] == 'c':
                                        if format_dict_array[(idx+5)%nodes_length]['t'] == 'c':
                                            if format_dict_array[(idx+6)%nodes_length]['t'] == 'c':
                                                if format_dict_array[(idx+7)%nodes_length]['t'] == 'c':
                                                    is_match_pattern = True

                match_case_node_8 = False
                match_case_node_7 = False

                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1:
                        fail_code = 201
                        if format_dict_array[(idx+1)%nodes_length]['x_direction'] == 1:
                            fail_code = 211
                            if format_dict_array[(idx+2)%nodes_length]['x_direction'] == 1:
                                fail_code = 221
                                if format_dict_array[(idx+3)%nodes_length]['x_direction'] == 1:
                                    fail_code = 231
                                    if format_dict_array[(idx+4)%nodes_length]['x_direction'] == 1:
                                        fail_code = 241
                                        if format_dict_array[(idx+5)%nodes_length]['x_direction'] == 1:
                                            fail_code = 241
                                            if format_dict_array[(idx+6)%nodes_length]['x_direction'] == 1:
                                                fail_code = 251

                                                if format_dict_array[(idx+7)%nodes_length]['x_direction'] == -1:
                                                        is_match_pattern = True
                                                        match_case_node_8 = True
                                            else:
                                                if format_dict_array[(idx+6)%nodes_length]['x_direction'] == -1:
                                                    is_match_pattern = True
                                                    match_case_node_7 = True



                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    if match_case_node_8:
                        #print("match_case_node_8 mode")
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == 1:
                            fail_code = 301
                            if format_dict_array[(idx+1)%nodes_length]['y_direction'] == 1:
                                fail_code = 311
                                if format_dict_array[(idx+2)%nodes_length]['y_direction'] == 1:
                                    fail_code = 321
                                    if format_dict_array[(idx+3)%nodes_length]['y_direction'] == 1:
                                        fail_code = 331
                                        if format_dict_array[(idx+4)%nodes_length]['y_direction'] == 1:
                                            fail_code = 341
                                            if format_dict_array[(idx+5)%nodes_length]['y_direction'] == 1:
                                                fail_code = 341
                                                if format_dict_array[(idx+6)%nodes_length]['y_direction'] == -1:
                                                    fail_code = 351
                                                    if format_dict_array[(idx+7)%nodes_length]['y_direction'] == -1:
                                                        is_match_pattern = True

                    if match_case_node_7:
                        #print("match_case_node_7 mode")
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == 1:
                            fail_code = 301
                            if format_dict_array[(idx+1)%nodes_length]['y_direction'] == 1:
                                fail_code = 311
                                if format_dict_array[(idx+2)%nodes_length]['y_direction'] == 1:
                                    fail_code = 321
                                    if format_dict_array[(idx+3)%nodes_length]['y_direction'] == 1:
                                        fail_code = 331
                                        if format_dict_array[(idx+4)%nodes_length]['y_direction'] == 1:
                                            fail_code = 341
                                            if format_dict_array[(idx+5)%nodes_length]['y_direction'] == -1:
                                                fail_code = 341
                                                if format_dict_array[(idx+6)%nodes_length]['y_direction'] == -1:
                                                    is_match_pattern = True

                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False
                    if match_case_node_8:
                        fail_code = 401
                        if [format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y']] in skip_coordinate:
                            fail_code = 411
                            if [format_dict_array[(idx+6)%nodes_length]['x'],format_dict_array[(idx+6)%nodes_length]['y']] in skip_coordinate:
                                is_match_pattern = True

                    if match_case_node_7:
                        fail_code = 451
                        if [format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y']] in skip_coordinate:
                            fail_code = 461
                            if [format_dict_array[(idx+5)%nodes_length]['x'],format_dict_array[(idx+5)%nodes_length]['y']] in skip_coordinate:
                                is_match_pattern = True


                if is_match_pattern:
                    fail_code = 500
                    is_match_pattern = False
                    if format_dict_array[(idx+3)%nodes_length]['distance'] > format_dict_array[(idx+0)%nodes_length]['distance']:
                        if format_dict_array[(idx+3)%nodes_length]['distance'] > format_dict_array[(idx+1)%nodes_length]['distance']:
                            if format_dict_array[(idx+3)%nodes_length]['distance'] > format_dict_array[(idx+2)%nodes_length]['distance']:
                                is_match_pattern = True

                if is_match_pattern:
                    fail_code = 600
                    is_match_pattern = False

                    slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    slide_percent_3 = spline_util.slide_percent(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],format_dict_array[(idx+4)%nodes_length]['x'],format_dict_array[(idx+4)%nodes_length]['y'])

                    slide_percent_10 = spline_util.slide_percent(format_dict_array[(idx+2)%nodes_length]['x2'],format_dict_array[(idx+2)%nodes_length]['y2'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                    center_x,center_y=spline_util.two_point_extend(format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],-1 * format_dict_array[(idx+1)%nodes_length]['distance'])
                    #print("center_x,center_y:",center_x,center_y)

                    #is_debug_mode = True
                    if is_debug_mode:
                        print("slide_percent 1:", slide_percent_1)
                        print("data:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                        print("slide_percent 2:", slide_percent_2)
                        print("data:",format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                        print("slide_percent 3:", slide_percent_3)
                        print("data:",format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],format_dict_array[(idx+4)%nodes_length]['x'],format_dict_array[(idx+4)%nodes_length]['y'])

                        print("slide_percent 10:", slide_percent_10)
                        print("data:",format_dict_array[(idx+2)%nodes_length]['x2'],format_dict_array[(idx+2)%nodes_length]['y2'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])

                    if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                        fail_code = 601
                        if slide_percent_2 >= SLIDE_2_PERCENT_MIN and slide_percent_2 <= SLIDE_2_PERCENT_MAX:
                            fail_code = 611
                            if slide_percent_3 >= SLIDE_3_PERCENT_MIN and slide_percent_3 <= SLIDE_3_PERCENT_MAX:
                                fail_code = 621
                                if slide_percent_10 >= SLIDE_10_PERCENT_MIN and slide_percent_10 <= SLIDE_10_PERCENT_MAX:
                                    fail_code = 621
                                    if format_dict_array[(idx+2)%nodes_length]['x'] >= center_x:
                                        is_match_pattern = True

                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,": debug fail_code #22:", fail_code)
                    else:
                        print(idx,": match rule #22")

                if is_match_pattern:
                    #print(idx,": match rule #22")
                    new_x,new_y=spline_util.two_point_extend(format_dict_array[(idx+2)%nodes_length]['x2'],format_dict_array[(idx+2)%nodes_length]['y2'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],-1 * int(self.config.ROUND_OFFSET/2))
                    format_dict_array[(idx+2)%nodes_length]['x'] = new_x
                    format_dict_array[(idx+2)%nodes_length]['y'] = new_y
                    old_code_string = format_dict_array[(idx+2)%nodes_length]['code']
                    old_code_array = old_code_string.split(' ')
                    old_code_array[5]=str(new_x)
                    old_code_array[6]=str(new_y)
                    new_code = ' '.join(old_code_array)
                    # only need update code, let formater to re-compute.
                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                    check_first_point = True



        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
