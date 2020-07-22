#!/usr/bin/env python3
#encoding=utf-8

from . import spline_util

class Spline():
    config = None

    def __init__(self):
        pass

    def check_clockwise(self, spline_dict):
        clockwise = True
        area_total=0
        poly_lengh = len(spline_dict['dots'])
        #print('check poly: (%d,%d)' % (poly[0][0],poly[0][1]))
        for idx in range(poly_lengh):
            #item_sum = ((poly[(idx+1)%poly_lengh][0]-poly[(idx+0)%poly_lengh][0]) * (poly[(idx+1)%poly_lengh][1]-poly[(idx+0)%poly_lengh][1]))
            item_sum = ((spline_dict['dots'][(idx+0)%poly_lengh]['x']*spline_dict['dots'][(idx+1)%poly_lengh]['y']) - (spline_dict['dots'][(idx+1)%poly_lengh]['x']*spline_dict['dots'][(idx+0)%poly_lengh]['y']))
            #print(idx, poly[idx][0], poly[idx][1], item_sum)
            area_total += item_sum
        #print("area_total:",area_total)
        if area_total >= 0:
            clockwise = not clockwise
        return clockwise

    def assign_config(self, config):
        self.config = config

    def hello(self):
        print("world")

    def detect_bmp_data_top(self, bmp_image):
        threshold=0
        data_top=0
        #print("bmp_image.shape:", bmp_image.shape)
        if not bmp_image is None:
            # for PIL
            h,w = bmp_image.height,bmp_image.width

            is_match_data = False
            for y in range(h-2):
                if y==0:
                    continue
                if y>=h-3:
                    continue

                for x in range(w):
                    if bmp_image.getpixel((x, y)) == threshold and bmp_image.getpixel((x, y+1)) == threshold and bmp_image.getpixel((x, y-1)) == threshold:
                       #print("bingo:", x, y-1, bmp_image[x, y])
                       is_match_data = True
                       data_top=y-1
                       break
                if is_match_data:
                    break

        #print("data_top:", data_top)
        return data_top

    def detect_bmp_data_top_cv(self, bmp_image):
        threshold=0
        data_top=0
        #print("bmp_image.shape:", bmp_image.shape)
        if not bmp_image is None:
            # for OpenCV
            h, w, d = bmp_image.shape

            is_match_data = False
            for y in range(h-2):
                if y==0:
                    continue
                if y>=h-3:
                    continue

                for x in range(w):
                    if bmp_image[y, x][0] == threshold and bmp_image[y+1, x][0] == threshold and bmp_image[y-1, x][0] == threshold:
                       #print("bingo:", x, y-1, bmp_image[x, y])
                       is_match_data = True
                       data_top=y-1
                       break
                if is_match_data:
                    break

        #print("data_top:", data_top)
        return data_top


    def trace(self, stroke_dict, unicode_int, bmp_image):
        #print("trace")
        #print(stroke_dict)
        is_modified = False

        glyph_margin={}

        glyph_margin["top"]  = None
        glyph_margin["bottom"] = None
        glyph_margin["left"] = None
        glyph_margin["right"] = None

        if 1 in stroke_dict:
           for key in stroke_dict.keys():
                spline_dict = stroke_dict[key]
                self.detect_margin(spline_dict)

                if glyph_margin["top"] is None:
                    glyph_margin["top"]  = stroke_dict[key]["top"]
                    glyph_margin["bottom"] = stroke_dict[key]["bottom"]
                    glyph_margin["left"] = stroke_dict[key]["left"]
                    glyph_margin["right"] = stroke_dict[key]["right"]
 
                if glyph_margin["top"] < spline_dict["top"]:
                    glyph_margin["top"]  = spline_dict["top"]
                if glyph_margin["bottom"] > spline_dict["bottom"]:
                    glyph_margin["bottom"] = spline_dict["bottom"]
                if glyph_margin["left"] > spline_dict["left"]:
                    glyph_margin["left"] = spline_dict["left"]
                if glyph_margin["right"] < spline_dict["right"]:
                    glyph_margin["right"] = spline_dict["right"]

        y_offset = 880
        if not bmp_image is None:
            # maybe is empty glyph or control char.
            FF_TOP=glyph_margin["top"]
            
            BMP_TOP=None
            if not FF_TOP is None:
                BMP_TOP=self.detect_bmp_data_top(bmp_image)
                y_offset = (900 - FF_TOP) - BMP_TOP
            
            #print("FF_TOP=",FF_TOP)
            #print("bmp_top=",BMP_TOP)
            #print("y_offset=",y_offset)

        preprocess_result = self.preprocess(stroke_dict, unicode_int)
        if preprocess_result:
            is_modified = True

        for key in stroke_dict.keys():
            spline_dict = stroke_dict[key]
            #print("key:", key, 'code:', spline_dict['dots'][0])
            # for debug
            #if key==3:
            if True:
                clockwise = self.check_clockwise(spline_dict)
                #print("clockwise:", clockwise)
                normalize_result = self.normalize(stroke_dict, key, unicode_int, bmp_image, y_offset)
                if normalize_result:
                    is_modified = True
 
                if clockwise:
                    trace_result = self.trace_black_block(stroke_dict, key, unicode_int, bmp_image, y_offset)
                    if trace_result:
                        is_modified = True
                else:
                    trace_result = self.trace_white_block(stroke_dict, key, unicode_int, bmp_image, y_offset)
                    if trace_result:
                        is_modified = True

            stroke_dict[key] = spline_dict

        return is_modified, stroke_dict

    def detect_margin(self, spline_dict):
        default_int = -9999

        margin_top=default_int
        margin_bottom=default_int
        margin_left=default_int
        margin_right=default_int
        for dot_dict in spline_dict['dots']:
            x=dot_dict['x']

            if x != default_int:
                if margin_right==default_int:
                    # initail assign
                    margin_right=x
                else:
                    # compare top
                    if x > margin_right:
                        margin_right = x

                if margin_left==default_int:
                    # initail assign
                    margin_left=x
                else:
                    # compare bottom
                    if x < margin_left:
                        margin_left = x

            y=dot_dict['y']
            if y !=default_int:
                if margin_top==default_int:
                    # initail assign
                    margin_top=y
                else:
                    # compare top
                    if y > margin_top:
                        margin_top = y

                if margin_bottom==default_int:
                    # initail assign
                    margin_bottom=y
                else:
                    # compare bottom
                    if y < margin_bottom:
                        margin_bottom = y

        spline_dict["top"]  = margin_top
        spline_dict["bottom"] = margin_bottom
        spline_dict["left"] = margin_left
        spline_dict["right"] = margin_right

    def split_spline(self, stroke_dict, unicode_int):
        redo_split = False
        from . import Rule9_Split_Spline

        #print("before split count:", len(stroke_dict))
        for key in stroke_dict.keys():
            spline_dict = stroke_dict[key]
            #print("key:", key, 'code:', spline_dict['dots'][0])
            # for debug
            #if key==5:
            if True:
                clockwise = self.check_clockwise(spline_dict)
                #print("clockwise:", clockwise)
                if clockwise:
                    # format code.
                    # start to travel nodes for [RULE #9]
                    # format curve coner as l conver

                    ru9=Rule9_Split_Spline.Rule()
                    ru9.assign_config(self.config)

                    idx=-1
                    redo_travel,idx,new_format_dict_array=ru9.apply(spline_dict, idx)
                    ru9 = None

                    if redo_travel:
                        if new_format_dict_array != None:
                            if len(new_format_dict_array) > 0:
                                new_key_index = len(stroke_dict)+1
                                stroke_dict[new_key_index]={}
                                stroke_dict[new_key_index]['dots']=new_format_dict_array
                        redo_split = True
                        break

            stroke_dict[key] = spline_dict

        #print("after split count:", len(stroke_dict))

        return redo_split

    def preprocess(self, stroke_dict, unicode_int):
        is_modified = False
        MAX_SPLIT_CONNT = 100

        idx=-1
        redo_split=False   # Disable
        redo_split=True    # Enable
        while redo_split:
            idx+=1
            redo_split=self.split_spline(stroke_dict, unicode_int)
            if redo_split:
                is_modified = True
            if idx >= MAX_SPLIT_CONNT:
                redo_split = False

        return is_modified


    def normalize(self, stroke_dict, key, unicode_int, bmp_image, y_offset):
        is_modified = False

        from . import Rule4_Curve_Coner
        ru4=Rule4_Curve_Coner.Rule()
        ru4.assign_config(self.config)
        ru4.assign_unicode(unicode_int)

        from . import Rule10_Clean_Noise
        ru10=Rule10_Clean_Noise.Rule()
        ru10.assign_config(self.config)
        ru10.assign_unicode(unicode_int)
        
        from . import Rule14_Merge_Line
        ru14=Rule14_Merge_Line.Rule()
        ru14.assign_config(self.config)
        ru14.assign_unicode(unicode_int)

        from . import Rule6_Almost_Line_Curve
        ru6=Rule6_Almost_Line_Curve.Rule()
        ru6.assign_config(self.config)
        ru6.assign_unicode(unicode_int)

        spline_dict = stroke_dict[key]

        # ==================================================
        # format code block
        # ==================================================

        if self.config.PROCESS_MODE in ["GOTHIC"]:
            # format code.
            # start to travel nodes for [RULE #6]
            # format curve coner as l conver
            #print("start Rule # 6...")
            idx=-1
            redo_travel=False   # Disable
            redo_travel=True    # Enable
            while redo_travel:
                redo_travel,idx=ru6.apply(spline_dict, idx)
                if redo_travel:
                    is_modified = True
            ru6 = None

        # start to travel nodes for [RULE #10]
        # format curve coner as l conver
        #print("start Rule # 10...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        while redo_travel:
            redo_travel,idx=ru10.apply(spline_dict, idx)
            if redo_travel:
                is_modified = True
        ru10 = None

        # start to travel nodes for [RULE #14]
        # 有 first point 的關係，有時會有一小段的直線。
        #print("start Rule # 14...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        while redo_travel:
            redo_travel,idx=ru14.apply(spline_dict, idx)
            if redo_travel:
                is_modified = True
        ru14 = None

        # start to travel nodes for [RULE #4]
        # format curve coner as l conver
        #print("start Rule # 4...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        while redo_travel:
            redo_travel,idx=ru4.apply(spline_dict, idx)
            if redo_travel:
                is_modified = True
        ru4 = None

        return is_modified

    # run both in clockwise and counter clockwise.
    def trace_basic(self, stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule):
        is_modified = False

        DEBUG_CRASH_RULE = False    # online
        #DEBUG_CRASH_RULE = True    # debug

        DISABLE_ALL_RULE = False    # online
        #DISABLE_ALL_RULE = True    # debug specific rule.

        # start process here.
        spline_dict = stroke_dict[key]

        from . import Rule1_Row
        ru1=Rule1_Row.Rule()
        ru1.assign_config(self.config)
        ru1.assign_bmp(bmp_image, y_offset=y_offset)
        ru1.assign_unicode(unicode_int)

        from . import Rule2_Column
        ru2=Rule2_Column.Rule()
        ru2.assign_config(self.config)
        ru2.assign_bmp(bmp_image, y_offset=y_offset)
        ru2.assign_unicode(unicode_int)

        from . import Rule3_Water
        ru3=Rule3_Water.Rule()
        ru3.assign_config(self.config)
        ru3.assign_bmp(bmp_image, y_offset=y_offset)
        ru3.assign_unicode(unicode_int)

        # start to travel nodes for [RULE #2]
        # PS: for casle.31912 繫，的「山」太小，Rule#1 先跑會變成橫的先成立。
        if DEBUG_CRASH_RULE:
            print("start Rule # 2...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#2!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule=ru2.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule)
            if redo_travel:
                is_modified = True
        #print("Rule#2 is_modified:", is_modified)
        #print("Rule#2 redo_count:", redo_count)
        ru2 = None

        # start to travel nodes for [RULE #1]
        # 
        if DEBUG_CRASH_RULE:
            print("start Rule # 1...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#1!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule=ru1.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule)
            if redo_travel:
                is_modified = True
        #print("Rule#1 is_modified:", is_modified)
        #print("Rule#1 redo_count:", redo_count)
        ru1 = None

        # start to travel nodes for [RULE #3]
        # 
        if DEBUG_CRASH_RULE:
            print("start Rule # 3...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#3!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule=ru3.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule)
            if redo_travel:
                is_modified = True
        #print("Rule#3 is_modified:", is_modified)
        #print("Rule#3 redo_count:", redo_count)
        ru3 = None

        return is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule

    # run both in clockwise and counter clockwise.
    def trace_common(self, stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule):
        is_modified = False

        DEBUG_CRASH_RULE = False    # online
        #DEBUG_CRASH_RULE = True    # debug

        DISABLE_ALL_RULE = False    # online
        #DISABLE_ALL_RULE = True    # debug specific rule.

        from . import Rule7_Little_Cap
        ru7=Rule7_Little_Cap.Rule()
        ru7.assign_config(self.config)
        ru7.assign_unicode(unicode_int)

        from . import Rule8_Little_Tail
        ru8=Rule8_Little_Tail.Rule()
        ru8.assign_config(self.config)
        ru8.assign_unicode(unicode_int)

        from . import Rule12_Small_Mouth
        ru12=Rule12_Small_Mouth.Rule()
        ru12.assign_config(self.config)
        ru12.assign_bmp(bmp_image, y_offset=y_offset)
        ru12.assign_unicode(unicode_int)

        from . import Rule13_Small_Mouth_Flip
        ru13=Rule13_Small_Mouth_Flip.Rule()
        ru13.assign_config(self.config)
        ru13.assign_bmp(bmp_image, y_offset=y_offset)
        ru13.assign_unicode(unicode_int)

        from . import Rule16_Curve_Tail
        ru16=Rule16_Curve_Tail.Rule()
        ru16.assign_config(self.config)
        ru16.assign_bmp(bmp_image, y_offset=y_offset)
        ru16.assign_unicode(unicode_int)

        # PS: must apply this rule after all.
        from . import Rule21_Fix_Arrow
        ru21=Rule21_Fix_Arrow.Rule()
        ru21.assign_config(self.config)
        ru21.assign_bmp(bmp_image, y_offset=y_offset)
        ru21.assign_unicode(unicode_int)

        # start process here.
        spline_dict = stroke_dict[key]

        # start to travel nodes for [RULE #16]
        # 已灣，且向後翹的尾巴。
        # PS: must before Rule#1+#2+3!
        # PS: 這個己改用 Rule#2 來解決。
        # PS: 目前不需要使用到  Rule#16.
        if DEBUG_CRASH_RULE:
            print("start Rule # 16...")
        idx=-1
        redo_travel=False   # Disable
        #redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        while redo_travel:
            redo_travel,idx, inside_stroke_dict,skip_coordinate=ru16.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate)
            if redo_travel:
                is_modified = True
        ru16 = None


        # start to travel nodes for [RULE #12]
        # smooth small coner
        # PS: after Rule#1 process , some l will disappear.
        if DEBUG_CRASH_RULE:
            print("start Rule # 12...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#12!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate=ru12.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate)
            if redo_travel:
                is_modified = True
        ru12 = None

        # start to travel nodes for [RULE #13]
        # smooth small coner
        if DEBUG_CRASH_RULE:
            print("start Rule # 13...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#13!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate=ru13.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate)
            if redo_travel:
                is_modified = True
        ru13 = None


        # start to travel nodes for [RULE #7]
        # PS: 應該比 1，2，3 早套用，還是晚套用，這個很難取捨。
        if DEBUG_CRASH_RULE:
            print("start Rule # 7...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==100:
                print("occure bug at rule#7!")
            redo_travel,idx,skip_coordinate=ru7.apply(spline_dict, idx,skip_coordinate)
            if redo_travel:
                is_modified = True
        ru7 = None

        # only diable when halfmoon.
        is_enable_trace_base = True
        if self.config.PROCESS_MODE in ["HALFMOON"]:
            is_enable_trace_base = False

        if is_enable_trace_base:
            # start to travel nodes for [RULE #8]
            # 這是無內縮的版本，由於 rule#1 會強制內縮，造成內凹。
            if DEBUG_CRASH_RULE:
                print("start Rule # 8...")
            idx=-1
            redo_travel=False   # Disable
            redo_travel=True    # Enable
            if DISABLE_ALL_RULE:
                redo_travel=False
                pass
            redo_count=0
            while redo_travel:
                redo_count+=1
                if redo_count==100:
                    print("occure bug at rule#8!")
                redo_travel,idx, inside_stroke_dict,skip_coordinate=ru8.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate)
                if redo_travel:
                    is_modified = True
            ru8 = None

            base_is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule = self.trace_basic(stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)
            if base_is_modified:
                is_modified = True

        if self.config.PROCESS_MODE in ["GOTHIC"]:
            # start to travel nodes for [RULE #21]
            # 
            if DEBUG_CRASH_RULE:
                print("start Rule # 21...")
            idx=-1
            redo_travel=False   # Disable
            redo_travel=True    # Enable
            if DISABLE_ALL_RULE:
                redo_travel=False
                pass
            redo_count=0
            while redo_travel:
                redo_count+=1
                if redo_count==100:
                    print("occure bug at rule#21!")
                redo_travel,idx, inside_stroke_dict,skip_coordinate=ru21.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate)
                if redo_travel:
                    is_modified = True
            ru21 = None


        return is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule


    def trace_white_block(self, stroke_dict, key, unicode_int, bmp_image, y_offset):
        is_modified = False

        DISABLE_ALL_RULE = False    # online
        #DISABLE_ALL_RULE = True    # debug specific rule.

        from . import Rule11_Inside_Curve
        ru11=Rule11_Inside_Curve.Rule()
        ru11.assign_config(self.config)
        ru11.assign_bmp(bmp_image, y_offset=y_offset)
        ru11.assign_unicode(unicode_int)

        from . import Rule99_Coner_Killer
        ru99=Rule99_Coner_Killer.Rule()
        ru99.assign_config(self.config)
        ru99.assign_bmp(bmp_image, y_offset=y_offset)
        ru99.assign_unicode(unicode_int)

        spline_dict = stroke_dict[key]

        # cache bmp status
        inside_stroke_dict={}

        # cache skip coordinate, same transformed position should not do twice.
        skip_coordinate = []

        skip_coordinate_rule = []
        
        # for debug.
        #print("□"*60)
        #print("key:", key, 'code:', spline_dict['dots'][0])
        #if not key == 1:
            #return spline_dict
        is_common_enable = True

        if self.config.PROCESS_MODE in ["B2","B4","XD","HALFMOON"]:
            is_common_enable = False

        if is_common_enable:
            is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule = self.trace_common(stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)

        if self.config.PROCESS_MODE in ["XD","HALFMOON"]:
            base_is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule = self.trace_basic(stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)
            if base_is_modified:
                is_modified = True

        # start to travel nodes for [RULE #11]
        # check outside curve
        #print("start Rule # 11...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if self.config.PROCESS_MODE in ["B2","B4"]:
            redo_travel = False

        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==200:
                print("occure bug at rule#11!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule=ru11.apply(spline_dict, idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule)
            if redo_travel:
                is_modified = True
        ru11 = None


        # start to travel nodes for [RULE #99]
        # kill all small coner.
        #print("start Rule # 99...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        while redo_travel:
            black_mode = False
            redo_travel,idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule =ru99.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate, skip_coordinate_rule, black_mode)
            if redo_travel:
                is_modified = True
        ru99 = None

        return is_modified

    def trace_black_block(self, stroke_dict, key, unicode_int, bmp_image, y_offset):
        is_modified = False

        DEBUG_CRASH_RULE = False    # online
        #DEBUG_CRASH_RULE = True    # debug

        DISABLE_ALL_RULE = False    # online
        #DISABLE_ALL_RULE = True    # debug specific rule.

        from . import Rule5_Outside_Curve
        ru5=Rule5_Outside_Curve.Rule()
        ru5.assign_config(self.config)
        ru5.assign_bmp(bmp_image, y_offset=y_offset)
        ru5.assign_unicode(unicode_int)

        from . import Rule99_Coner_Killer
        ru99=Rule99_Coner_Killer.Rule()
        ru99.assign_config(self.config)
        ru99.assign_bmp(bmp_image, y_offset=y_offset)
        ru99.assign_unicode(unicode_int)

        spline_dict = stroke_dict[key]

        # cache bmp status
        inside_stroke_dict={}

        # cache skip coordinate, same transformed position should not do twice.
        skip_coordinate = []

        skip_coordinate_rule = []

        # for debug.
        #print("□"*60)
        #print("key:", key, 'code:', spline_dict['dots'][0])
        #if not key == 1:
            #return spline_dict

        # ==================================================
        # transform code block
        # ==================================================
        is_common_enable = True

        if self.config.PROCESS_MODE in ["B2","B4","XD","HALFMOON"]:
            is_common_enable = False

        if is_common_enable:
            is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule = self.trace_common(stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)

        if self.config.PROCESS_MODE in ["XD","HALFMOON"]:
            base_is_modified, inside_stroke_dict, skip_coordinate, skip_coordinate_rule = self.trace_basic(stroke_dict, key, unicode_int, bmp_image, y_offset, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)
            if base_is_modified:
                is_modified = True

        # start to travel nodes for [RULE #5]
        # check outside curve
        if DEBUG_CRASH_RULE:
            print("start Rule # 5...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if self.config.PROCESS_MODE in ["B2","B4"]:
            redo_travel = False

        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        
        # cache skip coordinate, same transformed position should not do twice.
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==200:
                print("occure bug at rule#5!")
            redo_travel,idx, inside_stroke_dict,skip_coordinate,skip_coordinate_rule=ru5.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate, skip_coordinate_rule)
            if redo_travel:
                is_modified = True
        ru5 = None


        # 這個在 halfmoon + #5 的情況下，可能會互相套用到。
        # start to travel nodes for [RULE #99]
        # kill all small coner.
        #print("start Rule # 99...")
        idx=-1
        redo_travel=False   # Disable
        redo_travel=True    # Enable
        if DISABLE_ALL_RULE:
            redo_travel=False
            pass
        redo_count=0
        while redo_travel:
            redo_count+=1
            if redo_count==200:
                print("occure bug at rule#9!")

            black_mode = True
            redo_travel,idx, inside_stroke_dict,skip_coordinate, skip_coordinate_rule=ru99.apply(spline_dict, idx, inside_stroke_dict, skip_coordinate, skip_coordinate_rule, black_mode)
            if redo_travel:
                is_modified = True
        ru99 = None

        return is_modified
