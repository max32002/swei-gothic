#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 3
# 處理三點「水」
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule):
        redo_travel=False
        check_first_point = False

        MERGE_NEAR_POINTS_ACCURACY = 20

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 4
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y']] in skip_coordinate:
                    continue

                if [format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y']] in skip_coordinate:
                    continue

                if format_dict_array[(idx+0)%nodes_length]['code'] in skip_coordinate_rule:
                    if is_debug_mode:
                        print("match skip skip_coordinate_rule +0:",[format_dict_array[(idx+0)%nodes_length]['code']])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[649,214]]
                    if not([format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": val#3:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False

                # for:脚 811A「月」slide_percent_1: 0.84
                SLIDE_1_PERCENT_MIN = 0.50
                SLIDE_1_PERCENT_MAX = 1.80

                slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'])
                slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'],format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                if is_debug_mode:
                    print("slide_percent_1:",slide_percent_1)
                    print("slide_percent_2:",slide_percent_2)

                # 合併斜線：.uni811A 「脚」月上的斜線，分成二段。
                check_more_merge_stroke_condition = False
                if format_dict_array[(idx+0)%nodes_length]['distance'] > 150:
                    if format_dict_array[(idx+1)%nodes_length]['distance'] < 50:
                        if format_dict_array[(idx+2)%nodes_length]['distance'] < 50:
                            if format_dict_array[(idx+3)%nodes_length]['distance'] > 150:
                                if (format_dict_array[(idx+1)%nodes_length]['distance']+format_dict_array[(idx+2)%nodes_length]['distance']) >= 30:
                                    if (format_dict_array[(idx+1)%nodes_length]['distance']+format_dict_array[(idx+2)%nodes_length]['distance']) <= 120:
                                        check_more_merge_stroke_condition = True
                #print("check_more_merge_stroke_condition 1:", check_more_merge_stroke_condition)
                if check_more_merge_stroke_condition:
                    check_more_merge_stroke_condition = False
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                            if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                                check_more_merge_stroke_condition = True
                #print("check_more_merge_stroke_condition 2:", check_more_merge_stroke_condition)
                if check_more_merge_stroke_condition:
                    check_more_merge_stroke_condition = False
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+3)%nodes_length]['x_direction']:
                        if format_dict_array[(idx+1)%nodes_length]['x_direction'] == format_dict_array[(idx+0)%nodes_length]['x_direction']:
                            if format_dict_array[(idx+1)%nodes_length]['x_direction'] == format_dict_array[(idx+2)%nodes_length]['x_direction']:
                                check_more_merge_stroke_condition = True
                #print("check_more_merge_stroke_condition 3:", check_more_merge_stroke_condition)
                if check_more_merge_stroke_condition:
                    check_more_merge_stroke_condition = False
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+3)%nodes_length]['y_direction']:
                        if format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+3)%nodes_length]['y_direction']:
                            if format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+2)%nodes_length]['y_direction']:
                                check_more_merge_stroke_condition = True
                #print("check_more_merge_stroke_condition 4:", check_more_merge_stroke_condition)
                if check_more_merge_stroke_condition:
                    check_more_merge_stroke_condition = False
                    if slide_percent_1 >= SLIDE_1_PERCENT_MIN and slide_percent_1 <= SLIDE_1_PERCENT_MAX:
                        # for:脚 811A「月」slide_percent_2: 1.98
                        if slide_percent_2 >= 1.96:
                            check_more_merge_stroke_condition = True
                #print("check_more_merge_stroke_condition 5:", check_more_merge_stroke_condition)
                if check_more_merge_stroke_condition:
                    # start to merge line.
                    format_dict_array[(idx+1)%nodes_length]['distance'] = (format_dict_array[(idx+1)%nodes_length]['distance']+format_dict_array[(idx+2)%nodes_length]['distance'])

                    new_code = ' %d %d l 1\n' % (format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y'])
                    format_dict_array[(idx+3)%nodes_length]['t'] = 'l'
                    format_dict_array[(idx+3)%nodes_length]['code'] = new_code
                    #print("new +3 code:", new_code)

                    del format_dict_array[(idx+2)%nodes_length]

                    if idx > (idx+2)%nodes_length:
                        idx +=1
                    nodes_length = len(format_dict_array)


                # 格式化例外：.31881 「閒」的上面的斜線。
                # convert ?cc? => ?cl?
                DISTANCE_IN_LINE_ACCURACY = 0.06
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                                # 上邊或下邊，其中一條為接進水平線。
                                if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy'] or format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                                    x1=format_dict_array[(idx+1)%nodes_length]['x']
                                    y1=format_dict_array[(idx+1)%nodes_length]['y']
                                    x2=format_dict_array[(idx+2)%nodes_length]['x']
                                    y2=format_dict_array[(idx+2)%nodes_length]['y']
                                    x2_1 = format_dict_array[(idx+2)%nodes_length]['x1']
                                    y2_1 = format_dict_array[(idx+2)%nodes_length]['y1']
                                    x2_2 = format_dict_array[(idx+2)%nodes_length]['x2']
                                    y2_2 = format_dict_array[(idx+2)%nodes_length]['y2']
                                    if spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY) and spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY):
                                        #print("convert c to l!")
                                        format_dict_array[(idx+2)%nodes_length]['x']=x2
                                        format_dict_array[(idx+2)%nodes_length]['y']=y2
                                        format_dict_array[(idx+2)%nodes_length]['t']='l'
                                        new_code = ' %d %d l 1\n' % (x2, y2)
                                        format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                                        # [IMPORTANT] if change code, must triger check_first_point=True
                                        check_first_point=True

                # it's hard to handle, "complex" case in one time.
                # if let match case is fewer, it will match more condition.
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        fail_code = 100
                        is_match_pattern = True

                # compare stroke_width
                if is_match_pattern:
                    fail_code = 200
                    #print(idx,"debug rule3:",format_dict_array[idx]['code'])
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                        is_match_pattern = True

                # compare NEXT_DISTANCE_MIN
                if is_match_pattern:
                    fail_code = 210
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.NEXT_DISTANCE_MIN:
                        is_match_pattern = True

                # check slide#1
                # 去除部份情況
                if is_match_pattern:
                    if slide_percent_1 < SLIDE_1_PERCENT_MIN:
                        is_match_pattern = False
                    if slide_percent_1 > SLIDE_1_PERCENT_MAX:
                        is_match_pattern = False


                # 做例外排除，滿神奇的，會剛好被match.
                if is_match_pattern:
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                            is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                            is_match_pattern = False
                    if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+3)%nodes_length]['y_equal_fuzzy']:
                            is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                            is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                            is_match_pattern = False
                    if format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+3)%nodes_length]['x_equal_fuzzy']:
                            is_match_pattern = False

                # compare direction
                if is_match_pattern:
                    fail_code = 400
                    #print(idx,"debug rule3:",format_dict_array[idx]['code'])
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['y_direction']:
                            is_match_pattern = True

                    # 追加例外：源 的下面小的水平腳
                    # 下面的 code, 直接讓 match=True, 需要小心處理！
                    # 二條「垂直線」。
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                            # [重要]這個方向性，要相反! 
                            if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['y_direction']:
                                is_match_pattern = True

                    # 二條「平行線」
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                            # [重要]這個方向性，要相反! 
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                                is_match_pattern = True

                    # 追加例外：屑和備 的下面小的水平腳，由於無法套到 +0t x_equal_fuzzy, 也無法套到Rule#1.
                    # allow 
                    if format_dict_array[(idx+1)%nodes_length]['t']=='c':
                        if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                            if format_dict_array[(idx+0)%nodes_length]['y'] > format_dict_array[(idx+1)%nodes_length]['y']:
                                # y axis 微距
                                if format_dict_array[(idx+0)%nodes_length]['y'] - format_dict_array[(idx+1)%nodes_length]['y'] <= 22:
                                    # 橫向的線。
                                    if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:
                                        # 曲線往右下角長.
                                        # x1,y2 must between.
                                        if format_dict_array[(idx+1)%nodes_length]['x1'] >= format_dict_array[(idx+1)%nodes_length]['x'] :
                                            if format_dict_array[(idx+1)%nodes_length]['x2'] >= format_dict_array[(idx+1)%nodes_length]['x'] :
                                                if format_dict_array[(idx+1)%nodes_length]['x1'] <= format_dict_array[(idx+0)%nodes_length]['x'] :
                                                    if format_dict_array[(idx+1)%nodes_length]['x2'] <= format_dict_array[(idx+0)%nodes_length]['x'] :
                                                        # 力量要向下。
                                                        if format_dict_array[(idx+1)%nodes_length]['y1'] <= format_dict_array[(idx+0)%nodes_length]['y'] :
                                                            if format_dict_array[(idx+1)%nodes_length]['y2'] <= format_dict_array[(idx+0)%nodes_length]['y'] :
                                                                is_match_pattern = True


                # don't access the case for rule#1 & rule#2
                if is_match_pattern:
                    fail_code = 600
                    # must match horizonal or vertal equal.
                    if format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['t']=='l':
                            is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+1)%nodes_length]['t']=='l':
                            is_match_pattern = False


                # check from bmp file.
                if is_match_pattern:
                    fail_code = 700
                    is_match_pattern = False

                    bmp_x1 = format_dict_array[(idx+0)%nodes_length]['x']
                    bmp_y1 = format_dict_array[(idx+0)%nodes_length]['y']
                    bmp_x2 = format_dict_array[(idx+1)%nodes_length]['x']
                    bmp_y2 = format_dict_array[(idx+1)%nodes_length]['y']
                    bmp_x3 = format_dict_array[(idx+2)%nodes_length]['x']
                    bmp_y3 = format_dict_array[(idx+2)%nodes_length]['y']
                    bmp_x4 = format_dict_array[(idx+3)%nodes_length]['x']
                    bmp_y4 = format_dict_array[(idx+3)%nodes_length]['y']
                    
                    # 精簡的比對，會出錯，例如「緫」、「縃」、「繳」的方。「解」的刀。「繫」的山。
                    #bmp_x2 = bmp_x1 + (5 * format_dict_array[(idx+0)%nodes_length]['x_direction'])
                    #bmp_x3 = bmp_x4 + (5 * format_dict_array[(idx+0)%nodes_length]['x_direction'])
                    #bmp_y2 = bmp_y1 + (5 * format_dict_array[(idx+0)%nodes_length]['y_direction'])
                    #bmp_y3 = bmp_y4 + (5 * format_dict_array[(idx+0)%nodes_length]['y_direction'])
                    
                    # full rectangle compare.
                    #inside_stroke_flag = self.is_inside_stroke(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4)

                    # compact triangle compare, 
                    # allow one coner match to continue
                    inside_stroke_flag2 = False
                    inside_stroke_flag1,inside_stroke_dict = self.test_inside_coner(bmp_x1, bmp_y1, bmp_x2, bmp_y2, bmp_x3, bmp_y3, self.config.STROKE_MIN, inside_stroke_dict)
                    #print("inside_stroke_flag1:",inside_stroke_flag1)
                    if not inside_stroke_flag1:
                        # test next coner
                        inside_stroke_flag2,inside_stroke_dict = self.test_inside_coner(bmp_x2, bmp_y2, bmp_x3, bmp_y3, bmp_x4, bmp_y4, self.config.STROKE_MIN, inside_stroke_dict)
                        #print("inside_stroke_flag2:",inside_stroke_flag2)

                    if inside_stroke_flag1 or inside_stroke_flag2:
                        is_match_pattern = True

                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #3:", fail_code)
                    else:
                        print("match rule #3:",idx)

                if is_match_pattern:
                    #print("match rule #3")
                    #print(idx,": debug rule3:",format_dict_array[idx]['code'])

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("generated_code#3:", generated_code)
                    skip_coordinate_rule.append(generated_code)

                    if self.config.PROCESS_MODE in ["D"]:
                        generated_code = format_dict_array[(idx+1)%nodes_length]['code']
                        #print("generated_code#3+1:", generated_code)
                        skip_coordinate_rule.append(generated_code)

                    is_goto_apply_round = True
                    # for D.Lucy
                    if self.config.PROCESS_MODE in ["D"]:
                        is_match_d_base_rule, fail_code = self.going_d_right(format_dict_array,idx)
                        is_goto_apply_round = is_match_d_base_rule
                        #is_goto_apply_round = False

                    if is_goto_apply_round:
                        center_x,center_y = self.apply_round_transform(format_dict_array,idx)
                        #print("center_x,center_y:", center_x,center_y)

                        # cache transformed nodes.
                        # 加了，會造成其他的誤判，因為「點」共用。例如「甾」的右上角。
                        #skip_coordinate.append([format_dict_array[idx]['x'],format_dict_array[idx]['y']])
                        
                        # we generated nodes
                        skip_coordinate.append([center_x,center_y])

                    # next_x,y is used for next rule!
                    # 加了，會造成其他的誤判，因為「點」共用。
                    #skip_coordinate.append([new_x2,new_y2])

                    # keep the new begin point [FIX]
                    # 加了，會造成其他的誤判，因為「點」共用。例如「甾」的右上角。
                    #skip_coordinate.append([new_x1,new_y1])

                    # to avoid same code apply twice.

                    redo_travel=True
                    check_first_point = True
                    resume_idx = -1
                    break

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule
