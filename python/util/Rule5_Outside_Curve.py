#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule
import math

# RULE # 5
# check outside curve
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, stroke_dict, key, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log):
        redo_travel=False
        check_first_point = False

        # default: 1.33(small,inside), 1.49(large,outside)
        # MIN 的值，若設在 0.80 以下，「幺」的內角會套到。
        SLIDE_10_PERCENT_MIN = 0.70
        SLIDE_10_PERCENT_MAX = 1.80

        spline_dict = stroke_dict[key]

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

                is_debug_mode = False
                #is_debug_mode = True

                # 這個效果滿好玩的，「口」會變成二直，二圓。
                if self.config.PROCESS_MODE in ["HALFMOON"]:
                    idx_previuos = (idx -1 + nodes_length) % nodes_length
                    if format_dict_array[idx_previuos]['code'] in apply_rule_log:
                        continue

                detect_code = format_dict_array[(idx+0)%nodes_length]['code']
                if detect_code in apply_rule_log:
                    if is_debug_mode:
                        print("match skip apply_rule_log +0:",detect_code)
                        pass
                    continue

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                detect_code = format_dict_array[(idx+2)%nodes_length]['code']
                if detect_code in generate_rule_log:
                    if is_debug_mode:
                        print("match skip generate_rule_log +2:",detect_code)
                        print("current code:",format_dict_array[(idx+0)%nodes_length]['code'])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[80,198],[82,187]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue
                        pass

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": values#5:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                undo_changes = []

                is_match_pattern = False

                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y1']
                #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # 向下最少 20 點，才能開始長大。
                NEED_TO_EXTEND_DISTANCE_MIN = 15
                # 鄰居要夠長，才能借長度。
                NEED_TO_EXTEND_DISTANCE_SIBLING_MIN = 110
                # 左右 offset <= 8
                NEED_TO_EXTEND_X_OFFSET = 8


                # for .3187, 「力」、「馬」、「号」 系列，有奇怪的停頓點。
                #0 : values for rule1:  286 731 l 1
                #1 : values for rule1:  482 731 l 1
                #2 : values for rule1:  482 702 l 1
                #3 : values for rule1:  475 513 466 441 444 416 c 0
                # PS: for case. 3180, 借高度的，增加先決條件。x_direction + y_direction 要盡量相同。
                # PS: for case. 21324, 「林」，白色部份，不應該被「借高度」。
                is_extend_lag = False
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        # almost vertical.
                        #if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['y_direction'] < 0:
                            # match small distance
                            if abs(format_dict_array[(idx+2)%nodes_length]['x']-format_dict_array[(idx+1)%nodes_length]['x']) <= NEED_TO_EXTEND_X_OFFSET:
                                # not enough long.
                                if format_dict_array[(idx+1)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_MIN:
                                    if format_dict_array[(idx+1)%nodes_length]['distance'] < self.config.OUTSIDE_ROUND_OFFSET:
                                        if format_dict_array[(idx+2)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_SIBLING_MIN:
                                            # 好長哦，借一些來用用。
                                            if format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+2)%nodes_length]['y_direction']:
                                                # extend to new coordinate.
                                                #print("match extend")
                                                is_extend_lag = True

                # 成功的情況下，增加例外。
                # PS: for case. 3180,
                # for debug.
                #is_extend_lag = False
                if is_extend_lag:
                    if format_dict_array[(idx+1)%nodes_length]['x_direction'] !=0:
                        if format_dict_array[(idx+1)%nodes_length]['x_direction'] != format_dict_array[(idx+2)%nodes_length]['x_direction']:
                            is_extend_lag = False

                # 成功的情況下，增加例外。
                # PS: for case. 21324,
                # white mode, 不處理。
                if is_extend_lag:
                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                    if not inside_stroke_flag:
                        is_extend_lag = False

                # PS: 該「先長腳」還是等其他所有的判斷都成立，再長腳，應該是後者比較好。目前是使用問題較多的前者。
                #print("is_extend_lag:", is_extend_lag)
                if is_extend_lag:
                    extend_x,extend_y=spline_util.two_point_extend(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'], -1 * self.config.OUTSIDE_ROUND_OFFSET)

                    #print("new coordinate:",extend_x,extend_y)
                    format_dict_array[(idx+2)%nodes_length]['x']=extend_x
                    format_dict_array[(idx+2)%nodes_length]['y']=extend_y
                    new_code = ' %d %d l 1\n' % (extend_x, extend_y)
                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                    # [IMPORTANT] if change code, must triger check_first_point=True
                    check_first_point=True

                    # manuall compute distance for PREVIOUS dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                    #print("new distance #1:",new_distance)
                    format_dict_array[(idx+1)%nodes_length]['distance']=new_distance

                    # manuall compute distance for NEXT dot.
                    new_distance = spline_util.get_distance(extend_x,extend_y,format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    #print("new distance #2:",new_distance)
                    format_dict_array[(idx+2)%nodes_length]['distance']=new_distance

                # for .31725(uni7E0F)縏, 「殳」系列，左上角有奇怪的停頓點。
                #-1 : val:  486 655 464 676 494 687 c 1 -( 108 )
                # 0 : val:  577 717 571 729 571 764 c 2 -( 43 )
                # 1 : val:  571 807 l 1 -( 257 )
                # 2 : val:  828 807 l 1 -( 80 )

                # 因為「縏」筆畫很擠，只設 90
                NEED_TO_EXTEND_DISTANCE_SIBLING_MIN = 90

                extend_lag_flag = False
                idx_previuos = (idx+nodes_length-1)%nodes_length
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        # almost vertical.
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0:
                            # match small distance
                            if abs(format_dict_array[(idx+0)%nodes_length]['x']-format_dict_array[(idx+1)%nodes_length]['x']) <= NEED_TO_EXTEND_X_OFFSET:
                                # not enough long.
                                if format_dict_array[(idx+0)%nodes_length]['distance'] >= NEED_TO_EXTEND_DISTANCE_MIN:
                                    if format_dict_array[(idx+0)%nodes_length]['distance'] < self.config.OUTSIDE_ROUND_OFFSET:
                                        if format_dict_array[idx_previuos]['distance'] >= NEED_TO_EXTEND_DISTANCE_SIBLING_MIN:
                                            # 好長哦，借一些來用用。
                                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[idx_previuos]['y_direction']:
                                                extend_lag_flag = True
                                                # for 「絮」左上角的「女」的右上角。
                                                if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                                                    if format_dict_array[idx_previuos]['y_equal_fuzzy']:
                                                        # direction is different, cancel
                                                        extend_lag_flag = False

                # white mode, 不處理。
                if extend_lag_flag:
                    x0 = format_dict_array[(idx+0)%nodes_length]['x']
                    y0 = format_dict_array[(idx+0)%nodes_length]['y']
                    x1 = format_dict_array[(idx+1)%nodes_length]['x']
                    y1 = format_dict_array[(idx+1)%nodes_length]['y']
                    x2 = format_dict_array[(idx+2)%nodes_length]['x']
                    y2 = format_dict_array[(idx+2)%nodes_length]['y']

                    # use more close coordinate.
                    #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
                    if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                        x0 = format_dict_array[(idx+1)%nodes_length]['x2']
                        y0 = format_dict_array[(idx+1)%nodes_length]['y2']
                    if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                        x2 = format_dict_array[(idx+2)%nodes_length]['x1']
                        y2 = format_dict_array[(idx+2)%nodes_length]['y1']
                    #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict)
                    #print("inside_stroke_flag:", inside_stroke_flag)
                    if not inside_stroke_flag:
                        extend_lag_flag = False

                if extend_lag_flag:
                    # extend to new coordinate.
                    #print("match extend lag")
                    extend_x,extend_y=spline_util.two_point_extend(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'], -1 * self.config.OUTSIDE_ROUND_OFFSET)

                    offset_x = extend_x - format_dict_array[(idx+0)%nodes_length]['x']
                    offset_y = extend_y - format_dict_array[(idx+0)%nodes_length]['y']

                    #print("old coordinate:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'])
                    #print("new coordinate:",extend_x,extend_y)
                    #print("offset:",offset_x,offset_y)
                    format_dict_array[(idx+0)%nodes_length]['x']=extend_x
                    format_dict_array[(idx+0)%nodes_length]['y']=extend_y

                    old_code_string = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("orig code +0:", old_code_string)
                    old_code_array = old_code_string.split(' ')
                    if format_dict_array[(idx+0)%nodes_length]['t']=='c':
                        old_code_array[1] = str(int(float(old_code_array[1]))+offset_x)
                        old_code_array[2] = str(int(float(old_code_array[2]))+offset_y)
                        old_code_array[3] = str(int(float(old_code_array[3]))+offset_x)
                        old_code_array[4] = str(int(float(old_code_array[4]))+offset_y)
                        old_code_array[5] = str(extend_x)
                        old_code_array[6] = str(extend_y)
                    else:
                        old_code_array[1] = str(extend_x)
                        old_code_array[2] = str(extend_y)
                    new_code = ' '.join(old_code_array)
                    format_dict_array[(idx+0)%nodes_length]['code'] = new_code
                    #print("new_code +0:", new_code)
                    self.apply_code(format_dict_array,idx)

                    # [IMPORTANT] if change code, must triger check_first_point=True
                    check_first_point=True

                    undo_changes.append([idx,old_code_string])

                    # manuall compute distance for PREVIOUS dot.
                    #print("befor +0 distance:", format_dict_array[(idx+0)%nodes_length]['distance'])
                    #print("befor -1 distance:", format_dict_array[(idx-1+nodes_length)%nodes_length]['distance'])
                    format_dict_array[(idx+0)%nodes_length]['distance']=self.current_distance(format_dict_array,(idx+0)%nodes_length)
                    format_dict_array[(idx-1+nodes_length)%nodes_length]['distance']=self.current_distance(format_dict_array,(idx-1+nodes_length)%nodes_length)
                    #print("after +0 distance:", format_dict_array[(idx+0)%nodes_length]['distance'])
                    #print("after -1 distance:", format_dict_array[(idx-1+nodes_length)%nodes_length]['distance'])


                # pre-format for 「甾」系列的《
                #+0 : values for rule5:  548 428 516 414 501 441 c 1 -( 215 )
                #+1 : values for rule5:  495 471 448 555 396 629 c 1 -( 190 )
                #+2 : values for rule5:  437 694 464 745 488 796 c 1 -( 52 )
                LONG_EDGE_DISTANCE=110

                # PS: >= 0.01 很可怕，ex:「叔」系列。
                # PS: 目前已停用 is_match_convert_l_direction
                DISTANCE_IN_LINE_ACCURACY = 0.001

                idx_previuos = (idx+nodes_length-1)%nodes_length
                # converted by our others rule.
                #if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':

                #PS: 舊的code 會在這裡做 convert c to l 的轉換，目的是為了要match llc or cll 之類的 case.
                #    這段code 
                is_match_convert_l_direction = False

                # ... 判斷特定條件，讓 is_match_convert_l_direction = True
                # 修改為不使用。
                # 較好的解法，應該是無視 llc or cll , 通通做套用。

                if is_match_convert_l_direction:
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                        x1=format_dict_array[(idx+0)%nodes_length]['x']
                        y1=format_dict_array[(idx+0)%nodes_length]['y']
                        x2=format_dict_array[(idx+1)%nodes_length]['x']
                        y2=format_dict_array[(idx+1)%nodes_length]['y']
                        x2_1 = format_dict_array[(idx+1)%nodes_length]['x1']
                        y2_1 = format_dict_array[(idx+1)%nodes_length]['y1']
                        x2_2 = format_dict_array[(idx+1)%nodes_length]['x2']
                        y2_2 = format_dict_array[(idx+1)%nodes_length]['y2']
                        if spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY) and spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY):
                            #print("convert c to l#1!")
                            format_dict_array[(idx+1)%nodes_length]['x']=x2
                            format_dict_array[(idx+1)%nodes_length]['y']=y2
                            format_dict_array[(idx+1)%nodes_length]['t']='l'
                            new_code = ' %d %d l 1\n' % (x2, y2)
                            format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                            # [IMPORTANT] if change code, must triger check_first_point=True
                            check_first_point=True

                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                        x1=format_dict_array[(idx+1)%nodes_length]['x']
                        y1=format_dict_array[(idx+1)%nodes_length]['y']
                        x2=format_dict_array[(idx+2)%nodes_length]['x']
                        y2=format_dict_array[(idx+2)%nodes_length]['y']
                        x2_1 = format_dict_array[(idx+2)%nodes_length]['x1']
                        y2_1 = format_dict_array[(idx+2)%nodes_length]['y1']
                        x2_2 = format_dict_array[(idx+2)%nodes_length]['x2']
                        y2_2 = format_dict_array[(idx+2)%nodes_length]['y2']
                        if spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY) and spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY):
                            #print("convert c to l#2!")
                            format_dict_array[(idx+2)%nodes_length]['x']=x2
                            format_dict_array[(idx+2)%nodes_length]['y']=y2
                            format_dict_array[(idx+2)%nodes_length]['t']='l'
                            new_code = ' %d %d l 1\n' % (x2, y2)
                            format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                            # [IMPORTANT] if change code, must triger check_first_point=True
                            check_first_point=True


                is_match_pattern = True

                # =============================================
                # [IMPORTANT] 這條線以下，不要增追加可能的 case, 開始做排除
                # =============================================

                # 對太短邊做處理會出問題。
                if is_match_pattern:
                    if format_dict_array[(idx+0)%nodes_length]['distance'] <= 2:
                        is_match_pattern = False
                if is_match_pattern:
                    if format_dict_array[(idx+1)%nodes_length]['distance'] <= 2:
                        is_match_pattern = False

                # for D.Lucy
                if self.config.PROCESS_MODE in ["D","DEL"]:
                    fail_code = 131
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_d_right(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule

                # for RightBottom
                if self.config.PROCESS_MODE in ["RIGHTBOTTOM"]:
                    fail_code = 132
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_rightbottom_direction(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule

                # for XD
                if self.config.PROCESS_MODE in ["XD"]:
                    fail_code = 133
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_xd_down(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule

                # for RAINBOW
                if self.config.PROCESS_MODE in ["RAINBOW","BOW"]:
                    fail_code = 134
                    #print("before is_match_pattern:", is_match_pattern)
                    if is_match_pattern:
                        is_match_d_base_rule, fail_code = self.going_rainbow_up(format_dict_array,idx)
                        is_match_pattern = is_match_d_base_rule
                    #print("after is_match_pattern:", is_match_pattern)

                # compare distance, muse large than our "large round"
                if is_match_pattern:
                    fail_code = 200
                    is_match_pattern = False
                    #distance_min = self.config.OUTSIDE_ROUND_OFFSET
                    # PS: 如果是使用 distance_min=OUTSIDE_ROUND_OFFSET, 有一個待解問題。
                    #     U+5646 噆的「旡」的右邊，有一個角沒有套到效果，不知為何Rule#5 & Rule#99 都沒套到。
                    distance_min = self.config.ROUND_OFFSET
                    if format_dict_array[(idx+0)%nodes_length]['distance'] >= distance_min:
                        if format_dict_array[(idx+1)%nodes_length]['distance'] >= distance_min:
                            is_match_pattern = True

                # data been overwrite by pre-format code.
                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']

                # use more close coordinate.
                #print("orig x0,y0,x2,y2:", x0,y0,x2,y2)
                if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                    x_from = x0
                    y_from = y0
                    x_center = format_dict_array[(idx+1)%nodes_length]['x2']
                    y_center = format_dict_array[(idx+1)%nodes_length]['y2']
                    x0 = x_center
                    y0 = y_center
                if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                    x_from = x2
                    y_from = y2
                    x_center = format_dict_array[(idx+2)%nodes_length]['x1']
                    y_center = format_dict_array[(idx+2)%nodes_length]['y1']
                    x2 = x_center
                    y2 = y_center
                #print("new x0,y0,x2,y2:", x0,y0,x2,y2)

                previous_x,previous_y=0,0
                next_x,next_y=0,0

                # skip small angle
                # for case:.3180 「㚓」裡的大，因角度太小，變成圓角，不好看！
                slide_percent_1 = 0
                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    # PS: 使用結束 x,y，會造成更誤判，因為沒有另外儲存 rule#5 處理記錄，會造成重覆套用。
                    #slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                    slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)

                    if is_debug_mode:
                        print("slide_percent 1:", slide_percent_1)
                        print("data end:",format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                        print("data virtual:",x0,y0,x1,y1,x2,y2)
                        print("SLIDE_10_PERCENT_MIN:", SLIDE_10_PERCENT_MIN)
                        print("SLIDE_10_PERCENT_MAX:", SLIDE_10_PERCENT_MAX)

                    if slide_percent_1 >= SLIDE_10_PERCENT_MIN and slide_percent_1 <= SLIDE_10_PERCENT_MAX:
                        is_match_pattern = True
                    #else:
                    # 暫時沒有找到當初要解決的字是那一個。
                    # 但這段 code 會讓線條產生內凹，參考看看 𫣆 u2B8C6 的 思 裡的心。
                    if False:
                        # try real point.
                        # for case 「_」(忘記是那一個字）字的力的右上角。
                        # PS: 「加」(忘記是那一個字）字算是例外，一般的字，不應檢查到這裡。
                        if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+1)%nodes_length]['x2']==format_dict_array[(idx+1)%nodes_length]['x1'] and format_dict_array[(idx+1)%nodes_length]['y2']==format_dict_array[(idx+1)%nodes_length]['y1']:
                                pass
                            else:
                                # x1 != x2
                                # 這個「不相等」的情況，滿特別，允許例外。
                                # PS: 後來發現，沒有很特別，還滿常見的，如果使用下面註解裡的值，幾乎都會套用到效果。
                                #x0 = format_dict_array[(idx+0)%nodes_length]['x']
                                #y0 = format_dict_array[(idx+0)%nodes_length]['y']
                                pass
                        
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+2)%nodes_length]['x2']==format_dict_array[(idx+2)%nodes_length]['x1'] and format_dict_array[(idx+2)%nodes_length]['y2']==format_dict_array[(idx+2)%nodes_length]['y1']:
                                pass
                            else:
                                # x1 != x2
                                # 這個「不相等」的情況，滿特別，允許例外。
                                # PS: 後來發現，沒有很特別，還滿常見的，如果使用下面註解裡的值，幾乎都會套用到效果。
                                #x2 = format_dict_array[(idx+2)%nodes_length]['x']
                                #y2 = format_dict_array[(idx+2)%nodes_length]['y']
                                pass

                        slide_percent_1 = spline_util.slide_percent(x0,y0,x1,y1,x2,y2)
                        #print("slide_percent_1 - B:", slide_percent_1)
                        #print("1-B data:", x0,y0,x1,y1,x2,y2)
                        if slide_percent_1 >= SLIDE_10_PERCENT_MIN and slide_percent_1 <= SLIDE_10_PERCENT_MAX:
                            is_match_pattern = True
                    
                # 從成功的項目裡，排除已轉彎的項目。
                if is_match_pattern:
                    # ex: 「扌」和「糸」下方的水平腳
                    #is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[(idx+1)%nodes_length]['y_direction']:
                                # allow some accuracy
                                #if format_dict_array[(idx+1)%nodes_length]['x']==format_dict_array[(idx+2)%nodes_length]['x1']:
                                if abs(format_dict_array[(idx+1)%nodes_length]['x']-format_dict_array[(idx+2)%nodes_length]['x1'])<=4:
                                    is_match_pattern = False

                    # ex: 「繞」右下方的勾
                    #+0 : values for rule1:  771 -2 775 -5 798 -5 c 2xc050
                    #+1 : values for rule1:  875 -5 l 2
                    #+2 : values for rule1:  887 -5 891 -5 894 64 c 1
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['t']=='c':
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == format_dict_array[(idx+1)%nodes_length]['x_direction']:
                                # allow some accuracy
                                #if format_dict_array[(idx+1)%nodes_length]['y']==format_dict_array[(idx+2)%nodes_length]['y1']:
                                if abs(format_dict_array[(idx+1)%nodes_length]['y']-format_dict_array[(idx+2)%nodes_length]['y1'])<=4:
                                    center_x = int((format_dict_array[(idx+1)%nodes_length]['x']-format_dict_array[(idx+2)%nodes_length]['x'])/2)
                                    #print("center_x:", center_x)
                                    # 力量線過半，即為曲線。
                                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] > 0:
                                        #go right
                                        if format_dict_array[(idx+2)%nodes_length]['x1'] >= center_x:
                                            is_match_pattern = False
                                    else:
                                        #go left
                                        if format_dict_array[(idx+2)%nodes_length]['x1'] <= center_x:
                                            is_match_pattern = False


                # data been overwrite by pre-format code.
                x0 = format_dict_array[(idx+0)%nodes_length]['x']
                y0 = format_dict_array[(idx+0)%nodes_length]['y']
                x1 = format_dict_array[(idx+1)%nodes_length]['x']
                y1 = format_dict_array[(idx+1)%nodes_length]['y']
                x2 = format_dict_array[(idx+2)%nodes_length]['x']
                y2 = format_dict_array[(idx+2)%nodes_length]['y']
                # PS: to test inside_stroke_flag, please use real position instead of x1,y1.

                # compare distance, must large than our "large round"
                is_apply_large_corner = False

                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False

                    stroke_debug_mode = False
                    #stroke_debug_mode = True      # debug.

                    inside_stroke_flag,inside_stroke_dict = self.test_inside_coner(x0, y0, x1, y1, x2, y2, self.config.STROKE_WIDTH_MIN, inside_stroke_dict, debug_mode=stroke_debug_mode)
                    #print(idx,"debug rule1+0:",format_dict_array[idx]['code'])
                    #print(idx,"debug rule1+3:",format_dict_array[(idx+3)%nodes_length]['code'])
                    #print("x1=%d\ny1=%d\nx2=%d\ny2=%d\nx3=%d\ny3=%d" % (previous_x, previous_y, x1, y1, next_x, next_y))
                    #print("y_offset=", self.bmp_y_offset)

                    if is_debug_mode:
                        print("inside_stroke_flag:", inside_stroke_flag)
                        print('data:', x0, y0, x1, y1, x2, y2)

                    if inside_stroke_flag:
                        # match outside large conver.
                        #print("match large coner")
                        #print(idx,"large rule5:",format_dict_array[idx]['code'])
                        is_apply_large_corner = True
                        is_match_pattern = True
                    else:
                        fail_code = 410
                        # 使用圖片去猜，會有遇到 X 這種斜邊的判斷，有點難。
                        # 改用手動輸入的 default stroke width 來判斷 line join.

                        join_debug_mode = False
                        #join_debug_mode = True      # debug.

                        join_flag = self.join_line_check(x0,y0,x1,y1,x2,y2, debug_mode=join_debug_mode)
                        join_flag_1 = join_flag
                        join_flag_2 = None
                        if not join_flag:
                            fail_code = 420
                            join_flag = self.join_line_check(x2,y2,x1,y1,x0,y0)
                            join_flag_2 = join_flag
                            pass
                        
                        #if False:
                        if is_debug_mode:
                            print("join_flag_1:",join_flag_1)
                            print("join_flag_1 data:",x0,y0,x1,y1,x2,y2)
                            print("join_flag_2:",join_flag_2)
                            print("join_flag_2 data:",x2,y2,x1,y1,x0,y0)
                            print("final join flag:", join_flag)

                        if not join_flag:
                            #print("match small coner")
                            #print(idx,"small rule5:",format_dict_array[idx]['code'])
                            is_match_pattern = True
                            #is_apply_small_corner = True
                            #pass

                if is_debug_mode:
                    if not is_match_pattern:
                        print("idx:", idx,", debug fail_code #5:", fail_code)
                    else:
                        print("match rule #5:",idx)

                if is_match_pattern:
                    #print("match rule #5")
                    #print(idx,"debug rule5:",format_dict_array[idx]['code'])

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("apply_rule_log:", generated_code)
                    apply_rule_log.append(generated_code)

                    # make coner curve
                    round_offset = self.config.OUTSIDE_ROUND_OFFSET
                    # large curve, use small angle.
                    # start to resize round offset size.
                    resize_round_angle = 1.30
                    if slide_percent_1 >= resize_round_angle:
                        slide_percent_diff = 2.0 - slide_percent_1
                        slide_percent_total = 2.0 - slide_percent_diff
                        slide_percent_diff_percent = slide_percent_diff/slide_percent_total
                        round_offset_diff = self.config.OUTSIDE_ROUND_OFFSET - self.config.ROUND_OFFSET
                        round_offset_diff_added = int(round_offset_diff * slide_percent_diff_percent)
                        round_offset = self.config.ROUND_OFFSET + round_offset_diff_added

                    if not is_apply_large_corner:
                        round_offset = self.config.INSIDE_ROUND_OFFSET

                    is_goto_apply_round = True
                    center_x,center_y = -9999,-9999
                    next_x, next_y = -9999,-9999

                    if self.config.PROCESS_MODE in ["TOOTHPASTE"]:
                        is_match_direction_base_rule, fail_code = self.going_toothpaste(format_dict_array,idx)
                        is_goto_apply_round = is_match_direction_base_rule

                    if is_goto_apply_round:
                        format_dict_array, previous_x, previous_y, next_x, next_y = self.make_coner_curve(round_offset,format_dict_array,idx,apply_rule_log, generate_rule_log, stroke_dict, key)

                    # we generated nodes
                    # skip_coordinate 決定都拿掉，改用 apply_rule_log
                    # 因為只有作用在2個coordinate.
                    if self.config.PROCESS_MODE in ["HALFMOON"]:
                        # 加了這行，會讓「口」的最後一個角，無法套到。
                        #skip_coordinate.append([previous_x,previous_y])
                        pass


                    check_first_point = True
                    redo_travel=True
                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx
                    break
                    #redo_travel=True
                    #resume_idx = -1
                    #break
                else:
                    # cancel all un-finished chages!
                    if check_first_point:
                        for undo_item in undo_changes:
                            undo_idx = undo_item[0]
                            undo_code = undo_item[1]
                            #print("undo idx:",undo_item[0],undo_item[1])
                            format_dict_array[undo_idx]['code'] = undo_code
                            self.apply_code(format_dict_array,undo_idx)
                            
                            #print("befor +0 distance:", format_dict_array[(undo_idx+0)%nodes_length]['distance'])
                            #print("befor -1 distance:", format_dict_array[(undo_idx-1+nodes_length)%nodes_length]['distance'])
                            format_dict_array[(undo_idx+0)%nodes_length]['distance']=self.current_distance(format_dict_array,(undo_idx+0)%nodes_length)
                            format_dict_array[(undo_idx-1+nodes_length)%nodes_length]['distance']=self.current_distance(format_dict_array,(undo_idx-1+nodes_length)%nodes_length)
                            #print("after +0 distance:", format_dict_array[(undo_idx+0)%nodes_length]['distance'])
                            #print("after -1 distance:", format_dict_array[(undo_idx-1+nodes_length)%nodes_length]['distance'])

                    check_first_point = False

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)

        return redo_travel, resume_idx, inside_stroke_dict, apply_rule_log, generate_rule_log
