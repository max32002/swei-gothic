#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 1
# 橫線，的方頭轉圓頭。
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule,only_mark_log):
        redo_travel=False
        check_first_point = False

        # 如果是二條水平行，誤差值應小於 distance * 4%
        DISTANCE_COMPARE_ACCURACY = 0.9

        SKIP_SMALL_DISTANCE = 20

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

                if [format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip dot +1:",[format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y']])
                        pass
                    continue

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

                if [format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y']] in skip_coordinate:
                    if is_debug_mode:
                        print("match skip dot +0:",[format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y']])
                        pass
                    continue

                if format_dict_array[(idx+0)%nodes_length]['code'] in skip_coordinate_rule:
                    if is_debug_mode:
                        print("match skip skip_coordinate_rule +0:",[format_dict_array[(idx+0)%nodes_length]['code']])
                        pass
                    continue

                is_debug_mode = False
                #is_debug_mode = True

                if is_debug_mode:
                    debug_coordinate_list = [[923,620]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": val#1:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False

                if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                    is_match_pattern = True

                if is_match_pattern:
                    fail_code = 100
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                            is_match_pattern = True

                # 格式化例外：.31884 「禾」上面的斜線。
                # 一般是 match ?ll?, 要來match ?lc?
                # convert ?cl? => ?ll?
                DISTANCE_IN_LINE_ACCURACY = 0.06
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+1)%nodes_length]['match_stroke_width']:
                            if format_dict_array[(idx+0)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+2)%nodes_length]['x_direction']:

                            # 上邊或下邊，其中一條為接進水平線。
                            # 「禾」是有水平。
                            # for case:.31757 「辱」的小勾，沒有進入水平。
                            #if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy'] or format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                                x1=format_dict_array[(idx+1)%nodes_length]['x']
                                y1=format_dict_array[(idx+1)%nodes_length]['y']
                                x2=format_dict_array[(idx+2)%nodes_length]['x']
                                y2=format_dict_array[(idx+2)%nodes_length]['y']
                                x2_1 = format_dict_array[(idx+2)%nodes_length]['x1']
                                y2_1 = format_dict_array[(idx+2)%nodes_length]['y1']
                                x2_2 = format_dict_array[(idx+2)%nodes_length]['x2']
                                y2_2 = format_dict_array[(idx+2)%nodes_length]['y2']
                                test_1 = spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY)
                                test_2 = spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY)
                                #print("compare data 1:" , x1,y1,x2,y2,x2_1,y2_1)
                                #print("compare data 2:" , x1,y1,x2,y2,x2_2,y2_2)
                                #print("test1,2:" , test_1, test_2)
                                if test_1 and test_2:
                                    #print("convert c to l!")
                                    format_dict_array[(idx+2)%nodes_length]['x']=x2
                                    format_dict_array[(idx+2)%nodes_length]['y']=y2
                                    format_dict_array[(idx+2)%nodes_length]['t']='l'
                                    new_code = ' %d %d l 1\n' % (x2, y2)
                                    format_dict_array[(idx+2)%nodes_length]['code'] = new_code

                                    # [IMPORTANT] if change code, must triger check_first_point=True
                                    check_first_point=True

                                    is_match_pattern = True

                # let special rule do it.
                if is_match_pattern:
                    fail_code = 110

                    #print(idx,"debug rule1:",format_dict_array[idx]['code'])
                    # PS: just need check idx+0 & idx+2
                    for debug_idx in range(3):
                        if format_dict_array[(idx+debug_idx)%nodes_length]['distance'] <= SKIP_SMALL_DISTANCE:
                            is_match_pattern = False

                # compare direction
                if is_match_pattern:
                    #print(idx,"debug rule1:",format_dict_array[idx]['code'])
                    fail_code = 200
                    is_match_pattern = False

                    #print(idx,"stroke_width:",format_dict_array[(idx+1)%nodes_length]['match_stroke_width'])
                    #print(idx,"distance 1:",format_dict_array[(idx+1)%nodes_length]['distance'])
                    #print(idx,"y_equal_fuzzy 0:", format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy'])
                    #print(idx,"y_equal_fuzzy 2:", format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy'])

                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                            is_match_pattern = True
                            # match 水平、左右橫線的出頭。

                    # 如果不是水平線的情況下，也行。（加強版，支援斜線）
                    if not is_match_pattern:
                        #if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.STROKE_MAX:
                        if True:
                            # mayby is edge.
                            #if format_dict_array[(idx+2)%nodes_length]['distance'] > self.config.STROKE_MAX:
                            if True:
                                #print(idx,"debug rule1:",format_dict_array[idx]['code'])

                                new_distance = format_dict_array[(idx+2)%nodes_length]['distance']
                                distance_percent = format_dict_array[(idx+0)%nodes_length]['distance'] / new_distance

                                x_diff = format_dict_array[(idx+3)%nodes_length]['x']-format_dict_array[(idx+2)%nodes_length]['x']
                                y_diff = format_dict_array[(idx+3)%nodes_length]['y']-format_dict_array[(idx+2)%nodes_length]['y']
                                x_diff_new = int(x_diff * distance_percent)
                                y_diff_new = int(y_diff * distance_percent)

                                x_compare=format_dict_array[(idx+2)%nodes_length]['x'] + x_diff_new
                                y_compare=format_dict_array[(idx+2)%nodes_length]['y'] + y_diff_new

                                compare_distance = spline_util.get_distance(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],x_compare,y_compare)
                                target_stroke_width = format_dict_array[(idx+1)%nodes_length]['distance']
                                distance_diff = format_dict_array[(idx+1)%nodes_length]['distance']-compare_distance
                                distance_accuracy_1 = int(DISTANCE_COMPARE_ACCURACY * format_dict_array[(idx+0)%nodes_length]['distance'])
                                distance_accuracy_2 = int(DISTANCE_COMPARE_ACCURACY * format_dict_array[(idx+2)%nodes_length]['distance'])
                                distance_accuracy_max = distance_accuracy_1
                                if distance_accuracy_2 > distance_accuracy_max:
                                    distance_accuracy_max = distance_accuracy_2

                                if False:
                                    print("#1 compare x,y:", x_compare, y_compare)
                                    print("#1 compare distance:",  compare_distance)
                                    print("#1 point-1 distance (stroke_width):", target_stroke_width)
                                    print("distance_diff:", distance_diff)
                                    print("#1 point-0 distance:",  format_dict_array[(idx+0)%nodes_length]['distance'])
                                    print("distance_accuracy:", distance_accuracy_max)

                                if abs(distance_diff) <= distance_accuracy_max:
                                    is_match_pattern = True
                                else:
                                    # advance compare with x1,y1
                                    if format_dict_array[(idx+3)%nodes_length]['t']=='c':
                                        # compare with curve#1
                                        new_distance = spline_util.get_distance(format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y'],format_dict_array[(idx+3)%nodes_length]['x1'],format_dict_array[(idx+3)%nodes_length]['y1'])
                                        if new_distance > 0:
                                            distance_percent = format_dict_array[(idx+0)%nodes_length]['distance'] / new_distance

                                            x_diff = format_dict_array[(idx+3)%nodes_length]['x1']-format_dict_array[(idx+2)%nodes_length]['x']
                                            y_diff = format_dict_array[(idx+3)%nodes_length]['y1']-format_dict_array[(idx+2)%nodes_length]['y']
                                            x_diff_new = int(x_diff * distance_percent)
                                            y_diff_new = int(y_diff * distance_percent)

                                            x_compare=format_dict_array[(idx+2)%nodes_length]['x'] + x_diff_new
                                            y_compare=format_dict_array[(idx+2)%nodes_length]['y'] + y_diff_new
                                            compare_distance = spline_util.get_distance(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],x_compare,y_compare)
                                            distance_diff = format_dict_array[(idx+1)%nodes_length]['distance']-compare_distance
                                            #print("#2 compare x,y:", x_compare, y_compare)
                                            #print("#2 compare distance:",  compare_distance)
                                            #print("#2 point-1 distance:",  format_dict_array[(idx+1)%nodes_length]['distance'])
                                            if abs(distance_diff) < distance_accuracy_max:
                                                is_match_pattern = True


                # compare NEXT_DISTANCE_MIN
                if is_match_pattern:
                    fail_code = 210
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.NEXT_DISTANCE_MIN:
                        is_match_pattern = True

                
                # for case "加" 的力的右上角。
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
                        is_match_pattern = True
                        fail_code = 410

                        # 不可以都同方向。
                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == -1:
                            if format_dict_array[(idx+2)%nodes_length]['y_direction'] == -1:
                                is_match_pattern = False
                                fail_code = 420

                        if format_dict_array[(idx+0)%nodes_length]['y_direction'] == 1:
                            if format_dict_array[(idx+2)%nodes_length]['y_direction'] == 1:
                                is_match_pattern = False
                                fail_code = 430

                        # 在同方向情況下，有例外。
                        if is_match_pattern == False:
                            if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy'] and format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                                is_match_pattern = True

                # check from bmp file.
                if is_match_pattern:
                    is_match_pattern = False
                    fail_code = 500

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
                        print(idx,": debug fail_code #1:", fail_code)
                    else:
                        print(idx,": match rule #1")

                if is_match_pattern:
                    #print("match rule #1")
                    #print(idx,"debug rule1:",format_dict_array[idx]['code'])

                    # to avoid same code apply twice.
                    nodes_length = len(format_dict_array)
                    generated_code = format_dict_array[(idx+0)%nodes_length]['code']
                    #print("generated_code#1:", generated_code)
                    skip_coordinate_rule.append(generated_code)

                    if self.config.PROCESS_MODE in ["D"]:
                        generated_code = format_dict_array[(idx+1)%nodes_length]['code']
                        #print("generated_code#1 +1:", generated_code)
                        skip_coordinate_rule.append(generated_code)

                    if not only_mark_log:
                        center_x,center_y = self.apply_round_transform(format_dict_array,idx)

                        # cache transformed nodes.
                        # 加了，會造成其他的誤判，因為「點」共用。
                        #skip_coordinate.append([format_dict_array[idx]['x'],format_dict_array[idx]['y']])

                        # we generated nodes
                        skip_coordinate.append([center_x,center_y])

                    # next_x,y is used for next rule!
                    # 加了，會造成其他的誤判，因為「點」共用。
                    #skip_coordinate.append([new_x2,new_y2])

                    # keep the new begin point [FIX]
                    # 加了，會造成其他的誤判，因為「點」共用。例如「甾」的右上角。
                    #skip_coordinate.append([new_x1,new_y1])

                    redo_travel=True
                    check_first_point = True

                    # current version is not stable!, redo will cuase strange curves.
                    # [BUT], if not use -1, some case will be lost if dot near the first dot.
                    resume_idx = -1
                    #resume_idx = idx -1
                    break

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule
