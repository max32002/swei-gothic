# 獅尾圓體 Swei Gothic

獅尾圓體基於[思源黑體](https://github.com/adobe-fonts/source-han-sans)的拔腳和加圓改造，更加簡明現代化的字體。支援简体中文、繁體中文、韓文與日文。

「獅尾腿圓體」和「獅尾圓體」差別在有沒有拔腳，「拔腳」就是會有較少的筆畫，例如移除「口」字的左右下角會多出的短線條。有拔腳的字會較圓，但是會造成有些字因直接去掉腿後左右不平衡、左右不對襯的「懸空」問題。改使用「腿」系列字體就不會有這個問題。

和思源黑體一樣，支援7種的字重：
![字重比較](https://github.com/max32002/swei-gothic/raw/master/preview/compare_style.png)

## 與其他字體的比較
「獅尾圓體」、「源泉圓體」、「jf open 粉圓」的比較：

![字體比較](https://github.com/max32002/swei-gothic/raw/master/preview/compare_swei_gothic.png)

* 在「刂」的筆畫，粉圓和獅尾比較相似台灣(教育部國字標準字體)教育部推薦字體筆順。
* 在「肉」、「糸」、「女」、「辶」、「食」的筆畫，獅尾比較相似台灣教育部推薦字體筆順，適合教育用途。
* 在「草」部的筆畫，獅尾是分開的二個部份。
* 字體裡的「草字頭部首」中間該不該連起來，「肉字旁部首」該不該變成「月」，要不要把手寫習慣代入印刷字體？整體看來，會不會影響視覺的延伸性？會不會影響印刷的可行性與閱讀的便利性？這個答案我也不清楚，如果你是台灣教育部標準字符的愛好者，獅尾字體應該是一個不錯的選擇。
* 和「源泉圓體TW」的差異之一，是Regular 的字重有調整了部份的常用字，因為拔腳之後，不平衡的問題。
![字體比較](https://github.com/max32002/swei-gothic/raw/master/preview/fix_balance.png)

### 字體後面的 SC,JP,TC是什意思？
* SC是 Simplified Chinese 简体中文，代表大陸習慣字形。
* TC是 Traditional Chinese 繁体中文，代表港台習慣的字形。
* JP是 Japanese 日文，代表日本習慣字形。
* 相同一個字，在不地區的書寫方式可能會略有不同。

### 「CJK TC」和「CJK SC」的比較：
![TC和SC比較](https://github.com/max32002/swei-gothic/raw/master/preview/compare_tc_sc.png)
* 在「肉」、「糸」、「女」、「辶」、「食」的筆畫不同，CJK SC 「肉字旁部首」變成「月」。 
* 在「草」部的筆畫，CJK SC 中間連起來。
* 「體」字的骨上方方向相反。
* 「角」字下面穿頭。
* 雨、身、戶、舟、北、㕣、酋字寫法不同。

### 「CJK TC」和「CJK JP」的比較：
![TC和JP比較](https://github.com/max32002/swei-gothic/raw/master/preview/compare_tc_jp.png)
* 在「肉」、「糸」、「女」、「辶」、「食」的筆畫不同，CJK JP 「肉字旁部首」變成「月」。 
* 在「草」部的筆畫，CJK JP 中間連起來。
* 雨、言、青、兌、賣、直、真、曾、戶、北、㕣、酋字寫法不同。其他[常見與日系字型的差異](https://max-everyday.com/2020/06/taiwanpearl/#diff)。

## 更新日誌
[點擊此處](https://github.com/max32002/swei-gothic/blob/master/change_log.md) 查看更新記錄。

## 下載字型

請點選GitHub此畫面右上綠色「Clone or download」按鈕，並選擇「Download ZIP」，或點進想下載的ttf字型檔案，再點「Download」的按鈕進行下載。

## 網頁字型(Web Font)服務

網頁字型用於網頁上的字型顯示，訪客不需預先安裝字型檔，一樣能夠看到特殊的字型效果。不只是電腦，在智慧型手機和平板裝置的瀏覽器上也可正常顯示。實現該功能的原理是在瀏覽時才下載字型檔。

可以服用下面的css:
```
@font-face {
  font-family: SweiGothicCJKtc-Regular;
  src: url(https://cdn.jsdelivr.net/gh/max32002/swei-gothic@2.129/WebFont/CJK%20TC/SweiGothicCJKtc-Regular.woff2) format("woff2")
  , url(https://cdn.jsdelivr.net/gh/max32002/swei-gothic@2.129/WebFont/CJK%20TC/SweiGothicCJKtc-Regular.woff) format("woff");
}
```

## 已知問題

* 這不是一個專業的字型檔案。
* 很多字還是可以看到思源黑體的的直角。
* 因為拔腳，會造成部分文字「懸空」。
* 希望有贊助者，或其他勇者繼續改良和調整很多怪怪的小細節。
* 由於小編對字體編碼方式完全不清楚，相較於原版的思源黑體，可能有掉一些符號或不常用的字。

## 附註

* 演算黑科技將字體變圓，請參考 /python/ 目錄下的腳本檔案。透過調整程式碼，也許也可以產生出新的有趣字型。目前的程式應該還有很多錯誤或需要再加強的地方。請先把要處理的字型，透過 FontForge 開啟，並另存 FontForge 的專案為資料夾格式(.sfdir)，最後就可以透過Max的 Python 程式去處理產生出來的檔案。

## 著作權與授權

* 本字型是基於 SIL Open Font License 1.1 改造Adobe和Google所開發、發表的「[思源黑體](https://github.com/adobe-fonts/source-han-sans)」字型。
* 本字型亦基於 SIL Open Font License 1.1 授權條款免費公開，關於授權合約的內容、免責事項等細節，請詳讀 License 文件。
    * 可自由商用 不需付費、知會或標明作者，即可自由使用此字型，亦可做商業應用。
    * 可自由傳布 可自由分享檔案、將檔案安裝於任何軟硬體中。
    * 可自由改作為其他字型 將字型檔案修改重製為其他字型檔案，改作後的字型檔案須同樣依 Open Font License 釋出。
    
    
## 相關網頁

花園家族：
* B2花園 B2 Hana
https://max-everyday.com/2020/08/b2-hana-font/
* 花園肉丸 Hana Meatball
https://max-everyday.com/2020/08/hana-meatball/

獅尾黑體家族：
* 獅尾火腿黑體 Swei Match Leg
https://max-everyday.com/2020/11/swei-match-leg/
* 獅尾火柴黑體 Swei Match Sans
https://max-everyday.com/2020/11/swei-match-sans/
* 獅尾骨腿黑體 Swei Bone Leg
https://max-everyday.com/2020/11/swei-bone-leg/
* 獅尾骨頭黑體 Swei Bone Sans
https://max-everyday.com/2020/11/swei-bone-sans/
* 獅尾斧腿黑體 Swei Ax Leg
https://max-everyday.com/2020/11/swei-ax-leg/
* 獅尾斧頭黑體 Swei Ax Sans
https://max-everyday.com/2020/11/swei-ax-sans/
* 獅尾喇腿黑體 Swei Bell Leg
https://max-everyday.com/2020/11/swei-bell-leg/
* 獅尾喇叭黑體 Swei Bell Sans
https://max-everyday.com/2020/11/swei-bell-sans/
* 獅尾惡腿黑體 Swei Devil Leg
https://max-everyday.com/2020/11/swei-devil-leg/
* 獅尾惡魔黑體 Swei Devil Sans
https://max-everyday.com/2020/11/swei-devil-sans/
* 獅尾麥腿黑體 Swei Marker Leg
https://max-everyday.com/2020/10/swei-marker-leg/
* 獅尾麥克黑體 Swei Marker Sans
https://max-everyday.com/2020/10/swei-marker-sans/
* 獅尾詠腿黑體 Swei Fist Leg
https://max-everyday.com/2020/10/swei-fist-leg/
* 獅尾詠春黑體 Swei Fist Sans
https://max-everyday.com/2020/10/swei-fist-sans/
* 獅尾鋸腿黑體 Swei Alias Leg
https://max-everyday.com/2020/10/swei-alias-leg/
* 獅尾鋸齒黑體 Swei Alias Sans
https://max-everyday.com/2020/10/swei-alias-sans/
* 獅尾尖腿黑體 Swei Spike Leg
https://max-everyday.com/2020/10/swei-spike-leg/
* 獅尾尖刺黑體 Swei Spike Sans
https://max-everyday.com/2020/10/swei-spike-sans/
* 獅尾快腿黑體 Swei Shear Leg
https://max-everyday.com/2020/09/swei-shear-leg/
* 獅尾快剪黑體 Swei Shear Sans
https://max-everyday.com/2020/09/swei-shear-sans/
* 獅尾福腿黑體 Swei Gospel Leg
https://max-everyday.com/2020/09/swei-gospel-leg/
* 獅尾福音黑體 Swei Gospel Sans
https://max-everyday.com/2020/09/swei-gospel-sans/
* 獅尾D滷腿黑體 Swei Del Luna Leg
https://max-everyday.com/2020/09/swei-del-luna-leg/
* 獅尾德魯納黑體 Swei Del Luna Sans
https://max-everyday.com/2020/09/swei-del-luna-sans/
* 獅尾彎腿黑體 Swei Curve Leg
https://max-everyday.com/2020/09/swei-curve-leg/
* 獅尾彎黑體 Swei Curve Sans
https://max-everyday.com/2020/09/swei-curve-sans/
* 獅尾霓腿黑體 Swei Bow Leg
https://max-everyday.com/2020/09/swei-bow-leg/
* 獅尾霓黑體 Swei Bow Sans
https://max-everyday.com/2020/09/swei-bow-sans/
* 獅尾蝙蝠圓體 Swei Bat Sans
https://max-everyday.com/2020/09/swei-bat-sans/
* 獅尾牙膏圓體 Swei Toothpaste
https://max-everyday.com/2020/09/swei-toothpaste/
* 獅尾三腿黑體 Swei 3T Leg
https://max-everyday.com/2020/09/swei-3t-leg/
* 獅尾三角黑體 Swei 3T Sans
https://max-everyday.com/2020/08/swei-3t-sans/
* 獅尾螺帽腿黑體 Swei Nut Leg
https://max-everyday.com/2020/08/swei-nut-leg/
* 獅尾螺帽黑體 Swei Nut Sans
https://max-everyday.com/2020/08/swei-nut-sans/
* 獅尾B2腿黑體 Swei B2 Leg
https://max-everyday.com/2020/07/swei-b2-leg/
* 獅尾B2黑體 Swei B2 Sans
https://max-everyday.com/2020/07/swei-b2-sans/
* 獅尾腿圓 Swei Gothic Leg
https://max-everyday.com/2020/08/swei-gothic-leg/
* 獅尾彩虹腿 Swei Rainbow Leg
https://max-everyday.com/2020/08/swei-rainbow-leg/
* 獅尾XD珍珠 Swei XD Pearl
https://max-everyday.com/2020/07/swei-xd-pearl/
* 獅尾D露西 Swei D Lucy
https://max-everyday.com/2020/07/swei-d-lucy/
* 獅尾半月字體 Swei Gothic
https://max-everyday.com/2020/04/swei-half-moon/
* 台灣圓體 TaiwanPearl
https://max-everyday.com/2020/06/taiwanpearl/
* 獅尾圓體 Swei Gothic
https://max-everyday.com/2020/04/swei-gothic/
* 獅尾黑體 Swei Sans
https://max-everyday.com/2020/03/swei-sans/

獅尾宋體家族：
* 獅尾B2加糖宋體 Swei B2 Sugar
https://max-everyday.com/2020/11/swei-b2-sugar/
* 獅尾加糖宋體 Swei Sugar
https://max-everyday.com/2020/11/swei-sugar/
* 獅尾B2宋朝 Swei B2 Serif
https://max-everyday.com/2020/07/swei-b2-serif/
* 獅尾肉丸 Swei Meatball
https://max-everyday.com/2020/06/swei-meatball/
* 獅尾四季春字體 Swei Spring
https://max-everyday.com/2020/04/swei-spring/

其他字體：
* 何某手寫體 Nani Font
https://max-everyday.com/2020/09/nanifont/
* 內海字體  Naikai Font
https://max-everyday.com/2020/03/naikaifont/
* 莫大毛筆字體 Bakudai Font
https://max-everyday.com/2020/03/bakudaifont/
* 正風毛筆字體 Masa Font
https://max-everyday.com/2020/05/masafont/
* 假粉圓體 Fake Pearl 
https://max-everyday.com/2020/03/open-huninn-font/
* 俊羽圓體 Yu Pearl 
https://max-everyday.com/2020/03/yupearl/

其他網站：
* 清松手寫體 JasonHandWriting
https://jasonfonts.max-everyday.com/
* Max學習字體相關的筆記
https://codereview.max-everyday.com/font-readme/

## 贊助Max

很高興可以替中華民國美學盡一分心力、讓台灣擁有更好的文字風景，希望能提供另一種美學讓大家選擇，如果你覺得這篇文章寫的很好，想打賞Max，贊助方式如下：
https://max-everyday.com/about/#donate
