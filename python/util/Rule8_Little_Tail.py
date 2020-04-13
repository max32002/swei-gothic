#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util
from . import Rule

# RULE # 8
# 「段」左邊的小尾巴。解決內縮 33px 後，內凹的問題。
# PS: 因為 array size change, so need redo.
class Rule(Rule.Rule):
    def __init__(self):
        pass

    def apply(self, spline_dict, resume_idx, inside_stroke_dict,skip_coordinate):
        redo_travel=False

        # clone
        format_dict_array=[]
        format_dict_array = spline_dict['dots'][1:]
        format_dict_array = self.caculate_distance(format_dict_array)

        nodes_length = len(format_dict_array)
        #print("orig nodes_length:", len(spline_dict['dots']))
        #print("format nodes_length:", nodes_length)
        #print("resume_idx:", resume_idx)

        rule_need_lines = 6
        fail_code = -1
        if nodes_length >= rule_need_lines:
            for idx in range(nodes_length):
                if idx <= resume_idx:
                    # skip traveled nodes.
                    continue

                if [format_dict_array[idx]['x'],format_dict_array[idx]['y']] in skip_coordinate:
                    continue

                is_match_pattern = False

                #print(idx,"debug rule8:",format_dict_array[idx]['code'])


                #if not([format_dict_array[idx]['x'],format_dict_array[idx]['y']] == [463,776]):
                    #continue

                #if True:
                if False:
                    print("="*30)
                    print("index:", idx)
                    for debug_idx in range(8):
                        print(debug_idx-2,"values for rule8:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['code'],"x_direction:",format_dict_array[(idx+debug_idx+nodes_length-2)%nodes_length]['x_direction'])

                # match: ?llll?
                if format_dict_array[(idx+1)%nodes_length]['t'] == 'l':
                    if format_dict_array[(idx+2)%nodes_length]['t'] == 'l':
                        if format_dict_array[(idx+3)%nodes_length]['t'] == 'l':
                            if format_dict_array[(idx+4)%nodes_length]['t'] == 'l':
                                fail_code = 100
                                is_match_pattern = True

                # compare stroke_width
                if is_match_pattern:
                    #print(idx,"debug rule8:",format_dict_array[idx]['code'])
                    fail_code = 200
                    is_match_pattern = False
                    if format_dict_array[(idx+2)%nodes_length]['match_stroke_width']:
                        is_match_pattern = True

                if is_match_pattern:
                    #print(idx,"debug rule8:",format_dict_array[idx]['code'])
                    fail_code = 210
                    if format_dict_array[(idx+1)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                        is_match_pattern = False
                    if format_dict_array[(idx+3)%nodes_length]['distance'] >= self.config.OUTSIDE_ROUND_OFFSET:
                        is_match_pattern = False

                if is_match_pattern:
                    fail_code = 300
                    is_match_pattern = False
                    if format_dict_array[(idx+0)%nodes_length]['x_equal_fuzzy']:
                        if format_dict_array[(idx+4)%nodes_length]['x_equal_fuzzy']:
                            is_match_pattern = True
                        
                # compare direction
                if is_match_pattern:
                    fail_code = 400
                    is_match_pattern = False

                    #left side go top
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] > 0 :
                        if format_dict_array[(idx+4)%nodes_length]['y_direction'] > 0 :
                            is_match_pattern = True

                    #right side go bottom
                    if format_dict_array[(idx+0)%nodes_length]['y_direction'] < 0 :
                        if format_dict_array[(idx+4)%nodes_length]['y_direction'] < 0 :
                            is_match_pattern = True

                if is_match_pattern:
                    fail_code = 410
                    is_match_pattern = False
                    if format_dict_array[(idx+1)%nodes_length]['x_direction'] == -1 * format_dict_array[(idx+3)%nodes_length]['x_direction']:
                        if format_dict_array[(idx+1)%nodes_length]['y_direction'] == -1 * format_dict_array[(idx+3)%nodes_length]['y_direction']:
                            is_match_pattern = True

                    if format_dict_array[(idx+1)%nodes_length]['y_equal_fuzzy']:
                        if format_dict_array[(idx+3)%nodes_length]['y_equal_fuzzy']:
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

                if not is_match_pattern:
                    #print(idx,"debug fail_code8:", fail_code)
                    pass

                if is_match_pattern:
                    #print("match rule #8")
                    #print(idx,"debug rule8:",format_dict_array[idx]['code'])
                    if False:
                        for debug_idx in range(7):
                            print(debug_idx,"debug rule8-for-strange:",format_dict_array[(idx+debug_idx)%nodes_length]['code'])

                    center_x = int((format_dict_array[(idx+2)%nodes_length]['x']+format_dict_array[(idx+3)%nodes_length]['x'])/2)
                    center_y = int((format_dict_array[(idx+2)%nodes_length]['y']+format_dict_array[(idx+3)%nodes_length]['y'])/2)
                    #print("center x,y:", center_x, center_y)

                    x0 = format_dict_array[(idx+1)%nodes_length]['x']
                    y0 = format_dict_array[(idx+1)%nodes_length]['y']
                    x1 = format_dict_array[(idx+2)%nodes_length]['x']
                    y1 = format_dict_array[(idx+2)%nodes_length]['y']
                    x0_offset = 0
                    y0_offset = 0

                    x2 = format_dict_array[(idx+3)%nodes_length]['x']
                    y2 = format_dict_array[(idx+3)%nodes_length]['y']
                    x3 = format_dict_array[(idx+4)%nodes_length]['x']
                    y3 = format_dict_array[(idx+4)%nodes_length]['y']
                    x2_offset = 0
                    y2_offset = 0

                    #print("new offset0:", x0_offset, y0_offset)
                    #print("new offset2:", x2_offset, y2_offset)

                    # 斜線上的「內縮」的新坐標。
                    new_x1=x0+x0_offset
                    new_y1=y0+y0_offset
                    #new_x2=x2+x2_offset
                    #new_y2=y2+y2_offset
                    new_x2=x3
                    new_y2=y3
                    #print("new x1,y1:", new_x1, new_y1)
                    #print("new x2,y2:", new_x2, new_y2)

                    # curve #1
                    new_code = ' %d %d %d %d %d %d c 1\n' % (new_x1, new_y1, x1, y1, center_x, center_y)
                    dot_dict={}
                    dot_dict['x']=center_x
                    dot_dict['y']=center_y
                    dot_dict['t']='c'
                    dot_dict['code']=new_code
                    format_dict_array[(idx+2)%nodes_length]=dot_dict
                    #print("rule1 new_code:", new_code)

                    # curve #2
                    new_code = ' %d %d %d %d %d %d c 1\n' % (center_x, center_y, x2, y2, new_x2, new_y2)
                    dot_dict={}
                    dot_dict['x']=new_x2
                    dot_dict['y']=new_y2
                    dot_dict['t']='c'
                    dot_dict['code']=new_code
                    format_dict_array[(idx+3)%nodes_length]=dot_dict

                    del format_dict_array[(idx+4)%nodes_length]

                    # we generated nodes
                    skip_coordinate.append([center_x,center_y])

                    redo_travel=True
                    resume_idx = -1
                    resume_idx = idx
                    break

        if redo_travel:
            # check close path.
            self.reset_first_point(format_dict_array, spline_dict)


        return redo_travel, resume_idx, inside_stroke_dict,skip_coordinate
