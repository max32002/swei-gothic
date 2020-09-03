#!/usr/bin/env python3
#encoding=utf-8

class TtfConfig():
    VERSION = "2.094"
    PROCESS_MODE = "GOTHIC"
    #PROCESS_MODE = "HALFMOON"
    #PROCESS_MODE = "D"
    #PROCESS_MODE = "B2"
    #PROCESS_MODE = "B4"
    #PROCESS_MODE = "XD"
    #PROCESS_MODE = "RAINBOW"
    #PROCESS_MODE = "NUT8"
    #PROCESS_MODE = "TOOTHPASTE"

    STYLE_INDEX = 5
    STYLE_ARRAY = ["Black","Bold","Medium","Regular","DemiLight","Light","Thin"]
    STYLE=STYLE_ARRAY[STYLE_INDEX]

    DEFAULT_COORDINATE_VALUE = -9999

    # for Regular
    STROKE_MAX = 102

    # 有些筆劃很細，有些很粗，設太細似乎又會誤判。
    # 雖然字變重，但因為筆畫複雜時，還是有細的線條。
    STROKE_MIN = 30

    # for X,Y axis equal compare.
    # each 100 px, +- 7 px.
    # PS: 大於等於8，其實滿可怕的。
    EQUAL_ACCURACY_MIN = 3
    EQUAL_ACCURACY_PERCENT = 0.07

    # for Regular
    ROUND_OFFSET = 33

    # don't access the distance within 5
    NEXT_DISTANCE_MIN = 5

    # for Regular
    OUTSIDE_ROUND_OFFSET = 55
    INSIDE_ROUND_OFFSET = 19

    NEED_LOAD_BMP_IMAGE = True

    if PROCESS_MODE in ["B2"]:
        NEED_LOAD_BMP_IMAGE = False
        INSIDE_ROUND_OFFSET = 30

        if STYLE=="Black":
            INSIDE_ROUND_OFFSET = 45
        if STYLE=="Bold":
            INSIDE_ROUND_OFFSET = 40
        if STYLE=="Medium":
            INSIDE_ROUND_OFFSET = 35

    if PROCESS_MODE in ["B4"]:
        NEED_LOAD_BMP_IMAGE = False
        INSIDE_ROUND_OFFSET = 25

        if STYLE=="Black":
            INSIDE_ROUND_OFFSET = 40
        if STYLE=="Bold":
            INSIDE_ROUND_OFFSET = 35
        if STYLE=="Medium":
            INSIDE_ROUND_OFFSET = 30

    # for Regular
    if PROCESS_MODE in ["TOOTHPASTE"]:
        OUTSIDE_ROUND_OFFSET = 65
        INSIDE_ROUND_OFFSET = 25

    # some inside block not able to fill 2 curve coner, use small one.
    INSIDE_SMALL_ROUND_OFFSET=15

    # unicode in field
    # 1 to 3
    UNICODE_FIELD = 2

    BMP_PATH = '/Users/chunyuyao/Documents/noto/bmp'


    def apply_weight_setting(self):
        self.STYLE=self.STYLE_ARRAY[self.STYLE_INDEX]

        # for uni53BB, 去, 155
        if self.STYLE=="Black":
            self.STROKE_MAX = 165
        if self.STYLE=="Bold":
            self.STROKE_MAX = 139
        if self.STYLE=="Medium":
            self.STROKE_MAX = 115
        if self.STYLE=="DemiLight":
            self.STROKE_MAX = 96
        if self.STYLE=="Light":
            self.STROKE_MAX = 80
        if self.STYLE=="Thin":
            self.STROKE_MAX = 59

        if self.STYLE=="Black":
            self.STROKE_MIN = 34
        if self.STYLE=="Bold":
            self.STROKE_MIN = 34
        if self.STYLE=="Medium":
            self.STROKE_MIN = 30
        if self.STYLE=="DemiLight":
            self.STROKE_MIN = 27
        if self.STYLE=="Light":
            self.STROKE_MIN = 26
        if self.STYLE=="Thin":
            self.STROKE_MIN = 24

        self.STROKE_ACCURACY_PERCENT = 10
        self.STROKE_WIDTH_MAX = int((self.STROKE_MAX * (100+self.STROKE_ACCURACY_PERCENT))/100)
        self.STROKE_WIDTH_MIN = int((self.STROKE_MIN * (100-self.STROKE_ACCURACY_PERCENT))/100)
        self.STROKE_WIDTH_AVERAGE = int((self.STROKE_MIN+self.STROKE_MAX)/2)
        #print("STROKE_WIDTH_MAX:", STROKE_WIDTH_MAX)
        #print("STROKE_MIN:", STROKE_WIDTH_MIN)


        if self.STYLE=="Black":
            self.ROUND_OFFSET = 48
        if self.STYLE=="Bold":
            self.ROUND_OFFSET = 41
        if self.STYLE=="Medium":
            self.ROUND_OFFSET = 37
        if self.STYLE=="DemiLight":
            self.ROUND_OFFSET = 30
        if self.STYLE=="Light":
            self.ROUND_OFFSET = 27
        if self.STYLE=="Thin":
            self.ROUND_OFFSET = 24

        if self.STYLE=="Black":
            self.OUTSIDE_ROUND_OFFSET = 65
        if self.STYLE=="Bold":
            self.OUTSIDE_ROUND_OFFSET = 60
        if self.STYLE=="Medium":
            self.OUTSIDE_ROUND_OFFSET = 60
        if self.STYLE=="DemiLight":
            self.OUTSIDE_ROUND_OFFSET = 50
        if self.STYLE=="Light":
            self.OUTSIDE_ROUND_OFFSET = 40
        if self.STYLE=="Thin":
            self.OUTSIDE_ROUND_OFFSET = 30

        # bigger curve.
        if self.PROCESS_MODE in ["TOOTHPASTE"]:
            if self.STYLE=="Black":
                self.OUTSIDE_ROUND_OFFSET = 75
            if self.STYLE=="Bold":
                self.OUTSIDE_ROUND_OFFSET = 70
            if self.STYLE=="Medium":
                self.OUTSIDE_ROUND_OFFSET = 65
            if self.STYLE=="DemiLight":
                self.OUTSIDE_ROUND_OFFSET = 60
            if self.STYLE=="Light":
                self.OUTSIDE_ROUND_OFFSET = 50
            if self.STYLE=="Thin":
                self.OUTSIDE_ROUND_OFFSET = 35

        # 只需要大彎.
        if self.PROCESS_MODE in ["D","XD","HALFMOON","NUT8","TOOTHPASTE"]:
            self.ROUND_OFFSET=self.OUTSIDE_ROUND_OFFSET

    def __init__(self, weight_code):
        import datetime

        self.STYLE_INDEX = int(weight_code)
        self.apply_weight_setting()
        print("Transform Mode:", self.PROCESS_MODE)
        print("Transform Style:", self.STYLE)
        print("Transform Version:", self.VERSION)
        print("Transform Time:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def hello(self):
        print("world!")