import urllib
import datetime
import streamlit as st
import pendulum as pdlm
from io import StringIO
from contextlib import contextmanager, redirect_stdout
import taixuanshifa

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
        
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/taixuanshifa/master/' + path
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return ""

def get_file_content_as_string1(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/' + path
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return ""

st.set_page_config(layout="wide",page_title="堅太玄 - 太玄筮法排盤")
pan_tab, guji, links = st.tabs([' 排盤 ', ' 古籍 ',' 連結 ' ])

# 使用香港時間
tz = 'Asia/Hong_Kong'

# 初始化 session state
if 'selected_date' not in st.session_state:
    now = pdlm.now(tz=tz)
    st.session_state.selected_date = now.date()
    st.session_state.selected_time = now.time()
    st.session_state.current_y = now.year
    st.session_state.current_m = now.month
    st.session_state.current_d = now.day
    st.session_state.current_h = now.hour
    st.session_state.current_min = now.minute

with st.sidebar:
    st.header("選擇時間")
    pp_date = st.date_input("日期", value=st.session_state.selected_date, min_value=datetime.date(1500, 1, 1), max_value=datetime.date.today(), key="selected_date")
    pp_time = st.time_input("時間", value=st.session_state.selected_time, key="selected_time")
    
    if st.button("應用指定時間並排盤"):
        p = str(st.session_state.selected_date).split("-")
        pp = str(st.session_state.selected_time).split(":")
        st.session_state.current_y = int(p[0])
        st.session_state.current_m = int(p[1])
        st.session_state.current_d = int(p[2])
        st.session_state.current_h = int(pp[0])
        st.session_state.current_min = int(pp[1])

with links:
    st.header('連結')
    st.markdown(get_file_content_as_string1("update.md"), unsafe_allow_html=True)
    
with pan_tab:
    st.header('堅太玄')
    # 使用當前 session state 的時間排盤
    pan_result = taixuanshifa.Taixuan(
        st.session_state.current_y,
        st.session_state.current_m,
        st.session_state.current_d,
        st.session_state.current_h
    ).pan()
    output = st.empty()
    with st_capture(output.code):
        print(pan_result)
