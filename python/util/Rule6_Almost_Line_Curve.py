#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 6
# 簡化 c 為 l
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx):
        redo_travel=False

        EXPAND_MARGIN_ACCURACY = 0.03
        DISTANCE_IN_LINE_ACCURACY = 0.05

        # transform c to l for splash line.
        #大於等於 0.01 很醜！ex: 「㚞」的大，在 0.02變超細。
        SLASH_IN_LINE_ACCURACY = 0.002

        # 愈長的曲線變直線，更醜。
        SKIP_TOO_LONG_LINE_MERGE_DEFAULT = 90
        SKIP_TOO_LONG_LINE_MERGE = SKIP_TOO_LONG_LINE_MERGE_DEFAULT

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

                if is_debug_mode:
                    debug_coordinate_list = [[621,801]]
                    if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] in debug_coordinate_list):
                        continue

                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,": val#6:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'-(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')

                is_match_pattern = False

                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    fail_code = 100
                    is_match_pattern = True

                # for debug.
                #if format_dict_array[(idx+0)%nodes_length]['x'] != 698:
                    #is_match_pattern = False

                # only for 水平線/ vertical line.
                # remark for allow ALL line check.
                if is_match_pattern:
                #if False:
                    fail_code = 300
                    #is_match_pattern = False

                    is_slash_mode = True
                    #is_slash_mode = False
                    
                    #print(idx,"debug rule6 P0:",format_dict_array[(idx+0)%nodes_length]['code'])
                    # 水平線.
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        is_match_pattern = True
                        is_slash_mode = False

                    # vertical line.
                    if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        is_match_pattern = True
                        is_slash_mode = False

                    if is_slash_mode:
                        DISTANCE_IN_LINE_ACCURACY = SLASH_IN_LINE_ACCURACY

                x1 = format_dict_array[(idx+0)%nodes_length]['x']
                y1 = format_dict_array[(idx+0)%nodes_length]['y']
                x2 = format_dict_array[(idx+1)%nodes_length]['x']
                y2 = format_dict_array[(idx+1)%nodes_length]['y']

                x2_1 = format_dict_array[(idx+1)%nodes_length]['x1']
                y2_1 = format_dict_array[(idx+1)%nodes_length]['y1']
                x2_2 = format_dict_array[(idx+1)%nodes_length]['x2']
                y2_2 = format_dict_array[(idx+1)%nodes_length]['y2']

                if is_match_pattern:
                    #print(idx,"debug rule6 P0:",format_dict_array[(idx+0)%nodes_length]['code'])
                    fail_code = 300
                    is_match_pattern = False

                    test_1 = spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_1,y2_1,accuracy=DISTANCE_IN_LINE_ACCURACY)
                    test_2 = None
                    if x2_1 == x2_2 and y2_1 == y2_2:
                        test_2 = test_1
                    else:
                        test_2 = spline_util.is_xyz_on_line(x1,y1,x2,y2,x2_2,y2_2,accuracy=DISTANCE_IN_LINE_ACCURACY)
                    
                    #print("DISTANCE_IN_LINE_ACCURACY:", DISTANCE_IN_LINE_ACCURACY)
                    #print("test_1:", test_1)
                    #print("test_2:", test_2)
                    if test_1 and test_2:
                        is_match_pattern = True

                if is_match_pattern:
                    fail_code = 310
                    is_match_pattern = False
                    slide_percent_1 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],x2_1,y2_1,format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])
                    slide_percent_2 = None
                    if x2_1 == x2_2 and y2_1 == y2_2:
                        slide_percent_2 = slide_percent_1
                    else:
                        slide_percent_2 = spline_util.slide_percent(format_dict_array[(idx+0)%nodes_length]['x'],format_dict_array[(idx+0)%nodes_length]['y'],x2_2,y2_2,format_dict_array[(idx+1)%nodes_length]['x'],format_dict_array[(idx+1)%nodes_length]['y'])

                    if is_debug_mode:
                    #if False:
                        print("slide_percent 1:", slide_percent_1)
                        print("slide_percent 2:", slide_percent_2)

                    # for case 㜷 uni3737
                    # for 說 8AAA，要大於 1.980
                    if slide_percent_1 >= 1.982 and slide_percent_2 >= 1.982:
                        is_match_pattern = True

                # [important]: must reset to default, because variable in loop...
                SKIP_TOO_LONG_LINE_MERGE = SKIP_TOO_LONG_LINE_MERGE_DEFAULT
                if is_match_pattern:
                    # for 㜷, 的「女」斜邊，放大可以變成直線的長度。
                    # PS: 這個曲線變直線的解法不好！
                    #      應該可以無視 l+l 規則，直接在 c 上取點。
                    if format_dict_array[(idx+0)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+2+nodes_length)%nodes_length]['t'] == 'l':
                            # 超過 200 真的會影響到其他正常的字。例如 uni97DB 的曲線。
                            # 㜷 需要 length 280, 但 uni97DB 才 250 就讓線條線變粗。
                            SKIP_TOO_LONG_LINE_MERGE = 210
                
                # 太長會出問題，例如：的，絢 字。
                # PS: to dot+1, distance in +0
                if is_debug_mode:
                    print("+0 distance:", format_dict_array[(idx+0)%nodes_length]['distance'])
                    print("SKIP_TOO_LONG_LINE_MERGE:", SKIP_TOO_LONG_LINE_MERGE)

                if format_dict_array[(idx+0)%nodes_length]['distance'] >= SKIP_TOO_LONG_LINE_MERGE:
                    fail_code = 400
                    is_match_pattern = False
                    #print("SKIP_TOO_LONG_LINE_MERGE:", SKIP_TOO_LONG_LINE_MERGE)

                # 連續曲線變直線會怪怪：for case.26158:爬.
                # 連續曲線變直線會怪怪：for case:飹.
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+3)%nodes_length]['t'] == 'c':
                            if (format_dict_array[(idx+1)%nodes_length]['x_direction'] == format_dict_array[(idx+2)%nodes_length]['x_direction']) or format_dict_array[(idx+1)%nodes_length]['x_equal_fuzzy']:
                                if (format_dict_array[(idx+2)%nodes_length]['x_direction'] == format_dict_array[(idx+3)%nodes_length]['x_direction']) or format_dict_array[(idx+2)%nodes_length]['x_equal_fuzzy']:
                                    if (format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+2)%nodes_length]['y_direction']) or format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                                        if (format_dict_array[(idx+2)%nodes_length]['y_direction'] == format_dict_array[(idx+3)%nodes_length]['y_direction']) or format_dict_array[(idx+2)%nodes_length]['y_equal_fuzzy']:
                                            fail_code = 500
                                            is_match_pattern = False

                # 連續曲線變直線會怪怪：for case.26158:爬 / 飹 / 虞 865E / 
                if format_dict_array[(idx-1+nodes_length)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+0)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                            if (format_dict_array[(idx-1+nodes_length)%nodes_length]['x_direction'] == format_dict_array[(idx+0)%nodes_length]['x_direction']) or format_dict_array[(idx-1+nodes_length)%nodes_length]['x_equal_fuzzy']:
                                if (format_dict_array[(idx+0)%nodes_length]['x_direction'] == format_dict_array[(idx+1)%nodes_length]['x_direction']) or format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                                    if (format_dict_array[(idx-1+nodes_length)%nodes_length]['y_direction'] == format_dict_array[(idx+0)%nodes_length]['y_direction']) or format_dict_array[(idx-1+nodes_length)%nodes_length]['y_equal_fuzzy']:
                                        if (format_dict_array[(idx+0)%nodes_length]['y_direction'] == format_dict_array[(idx+1)%nodes_length]['y_direction']) or format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                                            fail_code = 510
                                            is_match_pattern = False

                # 連續曲線變直線會怪怪：for case:昴 uni6634.
                if format_dict_array[(idx+0)%nodes_length]['t'] == 'c':
                    if format_dict_array[(idx+1)%nodes_length]['t'] == 'c':
                        if format_dict_array[(idx+2+nodes_length)%nodes_length]['t'] == 'c':
                            if (format_dict_array[(idx+0)%nodes_length]['x_direction'] == format_dict_array[(idx+1)%nodes_length]['x_direction']) or format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                                if (format_dict_array[(idx+1+nodes_length)%nodes_length]['x_direction'] == format_dict_array[(idx+2)%nodes_length]['x_direction']) or format_dict_array[(idx+1+nodes_length)%nodes_length]['x_equal_fuzzy']:
                                    if (format_dict_array[(idx+0+nodes_length)%nodes_length]['y_direction'] == format_dict_array[(idx+1)%nodes_length]['y_direction']) or format_dict_array[(idx+0+nodes_length)%nodes_length]['y_equal_fuzzy']:
                                        if (format_dict_array[(idx+1)%nodes_length]['y_direction'] == format_dict_array[(idx+2)%nodes_length]['y_direction']) or format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                                            fail_code = 520
                                            is_match_pattern = False

                if is_debug_mode:
                    if not is_match_pattern:
                        print(idx,"debug fail_code #6:", fail_code)
                    else:
                        print("match rule #6:",idx)

                if is_match_pattern:
                    #print("="*30)
                    #print("match rule #6:",idx, format_dict_array[(idx+0)%nodes_length]['code'])

                    # use default
                    new_x = format_dict_array[(idx+1)%nodes_length]['x']
                    new_y = format_dict_array[(idx+1)%nodes_length]['y']

                    # 讓手的下面水平切齊。
                    # PS: 這個有優點，也有很多缺點！
                    # for: 「繈」uni7E48, 造成斜線，變成直線！進而造成 in stroke check fail!
                    #if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        # use parent x, maybe a little lower.
                        #new_x = format_dict_array[(idx+0)%nodes_length]['x']
                        #new_y = format_dict_array[(idx+1)%nodes_length]['y']
                    #if format_dict_array[(idx+0)%nodes_length]['y_equal_fuzzy']:
                        #new_x = format_dict_array[(idx+1)%nodes_length]['x']
                        #new_y = format_dict_array[(idx+0)%nodes_length]['y']

                    # 修改為，只有較短長度和距離下，才變直線。
                    if format_dict_array[(idx+0)%nodes_length]['distance']<=100:
                        if abs(format_dict_array[(idx+0)%nodes_length]['x']-format_dict_array[(idx+1)%nodes_length]['x'])<=3:
                            new_x = format_dict_array[(idx+0)%nodes_length]['x']
                        if abs(format_dict_array[(idx+0)%nodes_length]['y']-format_dict_array[(idx+1)%nodes_length]['y'])<=3:
                            new_y = format_dict_array[(idx+0)%nodes_length]['y']

                    format_dict_array[(idx+1)%nodes_length]['x']=new_x
                    format_dict_array[(idx+1)%nodes_length]['y']=new_y
                    format_dict_array[(idx+1)%nodes_length]['t']= 'l'
                    new_code_string = " %d %d l 1\n" % (new_x, new_y)
                    format_dict_array[(idx+1)%nodes_length]['code'] = new_code_string
                    #print("#6, new +1 code string:", new_code_string)

                    redo_travel=True
                    resume_idx = idx
                    #resume_idx = -1
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx
