#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 21
# 巛 符號
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log):
        redo_travel=False
        check_first_point = False

        # default: 1.33(small,inside), 1.49(large,outside)
        SLIDE_1_PERCENT_MIN = 1.08
        SLIDE_1_PERCENT_MAX = 1.58
        # default: 1.70(small,inside), 1.78-1.96(邋,908B)(large,outside)
        SLIDE_2_PERCENT_MIN = 1.50
        SLIDE_2_PERCENT_MAX = 1.99
        # default: 1.36(small,inside), 1.84(large,outside), 1.22(邋,908B)
        SLIDE_3_PERCENT_MIN = 1.11
        SLIDE_3_PERCENT_MAX = 1.90


        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)


        #print("hello, rule#21...")

        rule_need_lines = 7
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if format_dict_array[(idx+0)%nodes_length]['code'] in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +0:",[format_dict_array[(idx+0)%nodes_length]['code']])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[589,813]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(9):
                        print(debug_idx-2,": values for rule#21:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = True

                # match: ?cccccc
                # case: 繅 uni7E45
                # 497 799 l 2,39,40
                # 515 827 515 827 546 818 c 0,41,42 # +1, round curve generated point.
                # 577 810 577 810 556 783 c 0,43,44
                # 528 748 528 748 492 708 c 1,45,46 # +3, < center point.
                # 548 658 548 658 563 635 c 0,31,32
                # 581 607 581 607 553 595 c 0,33,34 # +5, round curve generated point.
                # 524 584 524 584 507 612 c 1,35,-1

                # case: 廵 uni5EF5 / 巡
                #0 : 623 666 623 666 656 781 c 1
                #1 : 665 812 665 812 699 804 c 1
                #2 : 734 796 734 796 725 765 c 1
                #3 : 699 681 693 673 606 467 c 1
                #4 : 721 252 721 252 755 142 c 1
                #5 : 764 111 764 111 730 97 c 1
                #6 : 696 83 696 83 688 115 c 1

                if is_match_pattern:
                    fail_code = 100
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                            # for 邋，+3 == 'l'
                            if True:
                            #if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                                if format_dict_array[(idx+4)%nodes_length]['t'] == 'c':
                                    if format_dict_array[(idx+5)%nodes_length]['t'] == 'c':
                                        if format_dict_array[(idx+6)%nodes_length]['t'] == 'c':
                                            is_match_pattern = True

                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    # PS: x direction > 0, go right, use inside round curve.
                    #     x direction < 0, go left, use outside round curve.
                    x_direction = format_dict_array[(idx+0)%nodes_length]['x_direction']
                    if x_direction != 0:
                        fail_code = 201
                        #if format_dict_array[(idx+1)%nodes_length]['x_direction'] == 1 or format_dict_array[(idx+1)%nodes_length]['x_direction'] == 0:
                        #fail_code = 211
                        if format_dict_array[(idx+2)%nodes_length]['x_direction'] == -1:
                            fail_code = 221
                            if format_dict_array[(idx+3)%nodes_length]['x_direction'] == 1:
                                fail_code = 231
                                #if format_dict_array[(idx+4)%nodes_length]['x_direction'] == -1:
                                if format_dict_array[(idx+5)%nodes_length]['x_direction'] == -1 * x_direction:
                                    fail_code = 241
                                    if format_dict_array[(idx+6)%nodes_length]['x_direction'] == -1:
                                        fail_code = 251
                                        is_match_pattern = True


                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    y_direction = format_dict_array[(idx+0)%nodes_length]['y_direction']
                    # PS: y_direction > 0, go right, use inside round curve.
                    #     y_direction < 0, go left, use outside round curve.
                    if y_direction != 0:
                        if format_dict_array[(idx+2)%nodes_length]['y_direction'] == -1 * y_direction:
                            if format_dict_array[(idx+3)%nodes_length]['y_direction'] == -1 * y_direction:
                                if format_dict_array[(idx+4)%nodes_length]['y_direction'] == -1 * y_direction:
                                    if format_dict_array[(idx+6)%nodes_length]['y_direction'] == 1 * y_direction:
                                        is_match_pattern = True

                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['code'] in generate_rule_log:
                        fail_code = 401
                        if format_dict_array[(idx+5)%nodes_length]['code'] in generate_rule_log:
                            is_match_pattern = True


                if is_match_pattern:
                    fail_code = 500
                    is_match_pattern = False
                    # must almost equal
                    # PS: 以「廵」為例，長邊 383 和 335，長度差 48,
                    #     383 * 0.15 = 57
                    #     335 * 0.17 = 56
                    if abs(format_dict_array[(idx+2)%nodes_length]['distance'] - format_dict_array[(idx+3)%nodes_length]['distance']) < (format_dict_array[(idx+2)%nodes_length]['distance'] * 0.17):
                        fail_code = 501
                        if format_dict_array[(idx+2)%nodes_length]['distance'] > format_dict_array[(idx+0)%nodes_length]['distance']:
                            if format_dict_array[(idx+2)%nodes_length]['distance'] > format_dict_array[(idx+1)%nodes_length]['distance']:
                                if format_dict_array[(idx+3)%nodes_length]['distance'] > format_dict_array[(idx+4)%nodes_length]['distance']:
                                    if format_dict_array[(idx+3)%nodes_length]['distance'] > format_dict_array[(idx+5)%nodes_length]['distance']:
                                        is_match_pattern = True

                if is_match_pattern:
                    fail_code = 600
                    is_match_pattern = False

                    slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    slide_percent_3 = spline_util.slide_percent(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],format_dict_array[(idx+4)%nodes_length]['x'],format_dict_array[(idx+4)%nodes_length]['y'])

                    #is_debug_mode = True
                    if is_debug_mode:
                        print("slide_percent 1:", slide_percent_1)
                        print("data:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                        print("slide_percent 2:", slide_percent_2)
                        print("data:",format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                        print("slide_percent 3:", slide_percent_3)
                        print("data:",format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'],format_dict_array[(idx+4)%nodes_length]['x'],format_dict_array[(idx+4)%nodes_length]['y'])

                    if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                        fail_code = 601
                        if slide_percent_2 >= SLIDE_2_PERCENT_MIN and slide_percent_2 <= SLIDE_2_PERCENT_MAX:
                            fail_code = 611
                            if slide_percent_3 >= SLIDE_3_PERCENT_MIN and slide_percent_3 <= SLIDE_3_PERCENT_MAX:
                                is_match_pattern = True

                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,": debug fail_code #21:", fail_code)
                    else:
                        print(idx,": match rule #21")

                if is_match_pattern:
                    is_apply_large_corner = False

                    x0 = format_dict_array[(idx+2)%nodes_length]['x']
                    y0 = format_dict_array[(idx+2)%nodes_length]['y']
                    x1 = format_dict_array[(idx+3)%nodes_length]['x']
                    y1 = format_dict_array[(idx+3)%nodes_length]['y']
                    x2 = format_dict_array[(idx+4)%nodes_length]['x']
                    y2 = format_dict_array[(idx+4)%nodes_length]['y']

                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                    #print("inside_stroke_flag:", inside_stroke_flag)
                    if inside_stroke_flag:
                        is_apply_large_corner = True

                    # make coner curve
                    #round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    # due to angle too large.
                    round_offset = self.config.ROUND_OFFSET
                    if not is_apply_large_corner:
                        round_offset = self.config.INSIDE_ROUND_OFFSET

                    format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx+2,apply_rule_log, generate_rule_log)

                    check_first_point = True
                    redo_travel=True
                    resume_idx = -1
                    break

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log
