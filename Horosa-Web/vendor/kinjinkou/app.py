# -*- coding: utf-8 -*-
"""
堅金口 - 金口訣排盤 Streamlit App
參考 kinliuren.streamlit.app (https://github.com/kentang2017/kinliuren)
"""

import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from kinjinkou import JinkoujueApi
from jieqi import gangzhi, jq, lunar_date_d, lunar_year_to_chinese, lunar_day_to_chinese


@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield


st.set_page_config(
    layout="wide",
    page_title="堅金口 - 金口訣排盤",
    page_icon="🧮"
)

pan, readme_tab = st.tabs([' 🧮排盤 ', ' 📖說明 '])

with st.sidebar:
    st.header("日期與時間選擇")

    default_datetime = pdlm.now(tz='Asia/Hong_Kong')

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        y = st.number_input(
            "年", min_value=1900, max_value=2100,
            value=default_datetime.year, step=1,
            help="輸入年份 (1900-2100)"
        )
    with col2:
        m = st.number_input(
            "月", min_value=1, max_value=12,
            value=default_datetime.month, step=1,
            help="輸入月份 (1-12)"
        )
    with col3:
        d = st.number_input(
            "日", min_value=1, max_value=31,
            value=default_datetime.day, step=1,
            help="輸入日期 (1-31)"
        )

    col4, col5 = st.columns(2)
    with col4:
        h = st.number_input(
            "時", min_value=0, max_value=23,
            value=default_datetime.hour, step=1,
            help="輸入小時 (0-23)"
        )
    with col5:
        mi = st.number_input(
            "分", min_value=0, max_value=59,
            value=default_datetime.minute, step=1,
            help="輸入分鐘 (0-59)"
        )

    st.subheader("地分選擇")
    dizhi_list = list("子丑寅卯辰巳午未申酉戌亥")
    difen = st.selectbox("地分（十二地支）", dizhi_list, index=0)

    st.subheader("快速選擇")
    if st.button("現在"):
        now = pdlm.now(tz='Asia/Hong_Kong')
        y = now.year
        m = now.month
        d = now.day
        h = now.hour
        mi = now.minute

    try:
        pdlm.datetime(y, m, d, h, mi, tz='Asia/Hong_Kong')
        st.write(f"已選擇: {y}年{m}月{d}日 {h:02d}:{mi:02d}")
    except ValueError:
        st.error("請輸入有效的日期和時間！")

    st.caption("時區: Asia/Hong_Kong")

with pan:
    st.header('堅金口 - 金口排盤')

    try:
        # 計算干支
        qgz = gangzhi(y, m, d, h, mi)
        # 計算節氣
        jieqi_name = jq(y, m, d, h, mi)
        # 計算農曆
        lunar = lunar_date_d(y, m, d)

        # 使用 JinkoujueApi 排盤
        dt = pdlm.datetime(y, m, d, h, mi, tz='Asia/Hong_Kong')
        api = JinkoujueApi()
        api.paipan(dt, difen=difen)

        # 顯示日期與干支資訊
        info_text = ""
        info_text += "日期︰{}年{}月{}日{}時{}分\n".format(y, m, d, h, mi)
        info_text += "農曆︰{}年{}{}日\n".format(lunar_year_to_chinese(lunar["年"]), lunar["農曆月"], lunar_day_to_chinese(lunar["日"]))
        info_text += "節氣︰{}\n".format(jieqi_name)
        #info_text += "干支︰{}年 {}月 {}日 {}時 {}分\n".format(
        #    qgz[0], qgz[1], qgz[2], qgz[3], qgz[4])
        #info_text += "地分︰{}\n".format(difen)

        output1 = st.empty()
        with st_capture(output1.code):
            print(info_text)
            
        output2 = st.empty()
        with st_capture(output2.code):
            pan_result = api.print_pan()
            # 不顯示天盤、地盤、神盤
            pan_result = '\n'.join(
                line for line in pan_result.splitlines()
                if not line.startswith(('地盘：', '天盘：', '神盘：'))
            )
            print(pan_result)

        # 原始資料
        expander = st.expander("原始資料")
        expander.write(str(api.P.Res))

    except Exception as e:
        st.error(f"排盤計算出錯：{str(e)}")

with readme_tab:
    st.header('說明')
    st.markdown("""
### 堅金口 - 金口訣排盤

金口訣（大六壬金口訣）是中國古代三式之一的六壬術的簡化版本，又稱「孫臏預測學」。

#### 使用方法
1. 在左側選擇日期與時間
2. 選擇地分（十二地支之一）
3. 系統自動計算干支並進行排盤

#### 功能說明
- **起年月日時干支**：根據輸入的公曆日期時間，自動計算年柱、月柱、日柱、時柱、分柱的天干地支
- **節氣計算**：自動判斷當前所處節氣
- **農曆轉換**：自動顯示對應的農曆日期
- **金口訣排盤**：根據干支和地分進行完整的金口訣起課計算

#### 排盤結果包括
- 月將
- 四課：人元、貴神、將神、地分
- 五行、陰陽、旺衰、用神分析
- 納音五行
- 四大空亡

#### 參考
- [kinliuren](https://github.com/kentang2017/kinliuren) - Python 大六壬排盤
""")
