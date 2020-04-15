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

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
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

                # 要轉換的原來的角，第3點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+2)%nodes_length]['x'],format_dict_array[(idx+2)%nodes_length]['y']] in skip_coordinate:
                    continue

                # 要轉換的原來的角，第4點，不能就是我們產生出來的曲線結束點。
                if [format_dict_array[(idx+3)%nodes_length]['x'],format_dict_array[(idx+3)%nodes_length]['y']] in skip_coordinate:
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                is_match_pattern = False

                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']]==[740, -7]):
                    #continue

                #print("-"*20)
                #print(idx,"debug rule3:",format_dict_array[idx]['code'])
                
                #if format_dict_array[(idx+0)%nodes_length]['x']==804:
                if False:
                #if True:
                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(6):
                        print(debug_idx-2,"values for rule3:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],'(',format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['distance'],')')


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

                if not is_match_pattern:
                    #print(idx,"debug fail_code3:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #3")
                    #print(idx,": debug rule3:",format_dict_array[idx]['code'])
                    
                    if False:
                    #if True:
                    #if format_dict_array[idx]['x']==831:
                        print("#"*40)
                        for debug_idx in range(6):
                            target_idx = (idx+debug_idx+nodes_length-2)%nodes_length
                            print(debug_idx-2,": values for rule1:",format_dict_array[target_idx]['code'])
                            print("...direction x,y:",format_dict_array[target_idx]['x_direction'],',',format_dict_array[target_idx]['y_direction'], '==' ,format_dict_array[target_idx]['distance'])
                    
                    center_x,center_y = self.apply_round_transform(format_dict_array,idx)


                    # 因為「先內縮」的關係，造成 curvy1_x2,y2 的方向可能是錯誤的！
                    # 先套上 offset
                    '''
                    if format_dict_array[(idx+1)%nodes_length]['t']=="c":
                        # 上一個點，可能在內縮後的右邊。
                        # 這個直接加 offset 會產生「奇怪的曲線」
                        curvy1_x2=format_dict_array[(idx+1)%nodes_length]['x2'] + x1_offset
                        curvy1_y2=format_dict_array[(idx+1)%nodes_length]['y2'] + y1_offset

                        format_dict_array[(idx+1)%nodes_length]['x2']=curvy1_x2
                        format_dict_array[(idx+1)%nodes_length]['y2']=curvy1_y2
                        old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                        old_code_array = old_code_string.split(' ')

                        # 如果前一條線很長。
                        if format_dict_array[(idx+0)%nodes_length]['distance'] > self.config.ROUND_OFFSET * 2:
                            # x1 過中線。
                            # for case: .31710 的 火🔥，下面解法：火會從曲線變直線。
                            tmp_center_x = int((x0+x1)/2)
                            if format_dict_array[(idx+0)%nodes_length]['x_direction']>0:
                                if int(float(old_code_array[1])) > tmp_center_x:
                                    old_code_array[1] = str(int(old_code_array[1]) + x1_offset)
                            if format_dict_array[(idx+0)%nodes_length]['x_direction']<0:
                                if int(old_code_array[1]) < tmp_center_x:
                                    old_code_array[1] = str(int(old_code_array[1]) - x1_offset)

                        old_code_array[3] = str(curvy1_x2)
                        old_code_array[4] = str(curvy1_y2)
                        new_code = ' '.join(old_code_array)
                        format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                    # 不知在寫什麼的 code... 開始。
                    if format_dict_array[(idx+3)%nodes_length]['t']=="c":
                        curvy2_x1=format_dict_array[(idx+3)%nodes_length]['x1'] + x2_offset
                        curvy2_y1=format_dict_array[(idx+3)%nodes_length]['y1'] + y2_offset

                        format_dict_array[(idx+3)%nodes_length]['x1']=curvy2_x1
                        format_dict_array[(idx+3)%nodes_length]['y1']=curvy2_y1
                        old_code_string = format_dict_array[(idx+3)%nodes_length]['code']
                        old_code_array = old_code_string.split(' ')
                        old_code_array[1] = str(curvy2_x1)
                        old_code_array[2] = str(curvy2_y1)
                        new_code = ' '.join(old_code_array)
                        format_dict_array[(idx+3)%nodes_length]['code'] = new_code
                    # 不知在寫什麼的 code... 結束。

                    # 因為「先內縮」的關係，造成 curvy1_x2,y2 的方向可能是錯誤的！
                    # fix x1,y1
                    if format_dict_array[(idx+1)%nodes_length]['t']=="c":
                        curvy1_x1=format_dict_array[(idx+1)%nodes_length]['x1']
                        curvy1_y1=format_dict_array[(idx+1)%nodes_length]['y1']
                        curvy1_x2=format_dict_array[(idx+1)%nodes_length]['x2']
                        curvy1_y2=format_dict_array[(idx+1)%nodes_length]['y2']
                        #print("curvy1_x1,y1:", curvy1_x1,curvy1_y1)
                        is_wrong_direction = False
                        
                        # for case: _Identity.310.glyph
                        if format_dict_array[(idx+0)%nodes_length]['x_direction']>0:
                            if curvy1_x1 > new_x1:
                                is_wrong_direction = True

                        if format_dict_array[(idx+0)%nodes_length]['x_direction']<0:
                            if curvy1_x1 < new_x1:
                                is_wrong_direction = True

                        #print("is_wrong_direction:", is_wrong_direction)
                        if is_wrong_direction:
                            format_dict_array[(idx+1)%nodes_length]['x1']=new_x1
                            format_dict_array[(idx+1)%nodes_length]['y1']=new_y1
                            old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                            old_code_array = old_code_string.split(' ')
                            
                            # for case: .31710 的 火🔥，下面解法：火會從曲線變直線。
                            # 只有較短的線做 overwrite, 一般應該是 add offset.
                            if format_dict_array[(idx+0)%nodes_length]['distance'] < self.config.ROUND_OFFSET * 2:
                                old_code_array[1] = str(new_x1)
                                old_code_array[2] = str(new_y1)
                                old_code_array[3] = str(new_x1)
                                old_code_array[4] = str(new_y1)
                            new_code = ' '.join(old_code_array)
                            format_dict_array[(idx+1)%nodes_length]['code'] = new_code
                            #print("udpate +1 curvy1_x2,y2 code as (before):", old_code_string)
                            #print("udpate +1 curvy1_x2,y2 code as (after):", new_code)

                        # for case: .31893 「繞」的尾巴，內縮後會超過 t0
                        if format_dict_array[(idx+0)%nodes_length]['y_direction']>0:
                            #print("['y_direction']>0")
                            #print("curvy1_y1 y0:", curvy1_y1, y0)
                            if curvy1_y1 < y0:
                                format_dict_array[(idx+1)%nodes_length]['y1']=y0
                                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                                old_code_array = old_code_string.split(' ')
                                old_code_array[2] = str(y0)
                                new_code = ' '.join(old_code_array)
                                format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                            if curvy1_y2 < y0:
                                format_dict_array[(idx+1)%nodes_length]['y2']=y0
                                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                                old_code_array = old_code_string.split(' ')
                                old_code_array[4] = str(y0)
                                new_code = ' '.join(old_code_array)
                                format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                        if format_dict_array[(idx+0)%nodes_length]['y_direction']<0:
                            #print("['y_direction']<0")
                            if curvy1_y1 > y0:
                                format_dict_array[(idx+1)%nodes_length]['y1']=y0
                                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                                old_code_array = old_code_string.split(' ')
                                old_code_array[2] = str(y0)
                                new_code = ' '.join(old_code_array)
                                format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                            if curvy1_y2 > y0:
                                format_dict_array[(idx+1)%nodes_length]['y2']=y0
                                old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                                old_code_array = old_code_string.split(' ')
                                old_code_array[4] = str(y0)
                                new_code = ' '.join(old_code_array)
                                format_dict_array[(idx+1)%nodes_length]['code'] = new_code

                    # 因為「先內縮」的關係，造成 curvy1_x2,y2 的方向可能是錯誤的！
                    # fix x2,y2
                    if format_dict_array[(idx+1)%nodes_length]['t']=="c":
                        curvy1_x2=format_dict_array[(idx+1)%nodes_length]['x2']
                        curvy1_y2=format_dict_array[(idx+1)%nodes_length]['y2']
                        #print("curvy1_x2,y2:", curvy1_x2,curvy1_y2)
                        is_wrong_direction = False
                        
                        # for case: _Identity.310.glyph
                        if format_dict_array[(idx+0)%nodes_length]['x_direction']>0:
                            if curvy1_x2 > new_x1:
                                is_wrong_direction = True

                        if format_dict_array[(idx+0)%nodes_length]['x_direction']<0:
                            if curvy1_x2 < new_x1:
                                is_wrong_direction = True

                        #print("is_wrong_direction:", is_wrong_direction)
                        if is_wrong_direction:
                            format_dict_array[(idx+1)%nodes_length]['x2']=new_x1
                            format_dict_array[(idx+1)%nodes_length]['y2']=new_y1
                            old_code_string = format_dict_array[(idx+1)%nodes_length]['code']
                            old_code_array = old_code_string.split(' ')
                            old_code_array[3] = str(new_x1)
                            old_code_array[4] = str(new_y1)
                            new_code = ' '.join(old_code_array)
                            format_dict_array[(idx+1)%nodes_length]['code'] = new_code
                    '''

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

                    redo_travel=True
                    check_first_point = True
                    resume_idx = -1
                    break

        if check_first_point:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
