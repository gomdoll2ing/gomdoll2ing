import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st

from pykrx import stock
from pykrx import bond

import quantstats as qs
from quantstats.reports import html


############################################################################################################################################


# Side bar
# 사이드바에 select box를 활용하여 종을 선택한 다음 그에 해당하는 행만 추출하여 데이터프레임을 만들고자합니다.
st.sidebar.title('Stock Analysis📊')

## 날짜/시간 Input
import datetime
today = st.sidebar.date_input("날짜를 선택하세요.", datetime.datetime.now())
#the_time = st.sidebar.time_input("시간을 입력하세요.", datetime.time())

tickers = stock.get_market_ticker_list(str(today).replace("-",""), market="ALL")
stock_name = []

for ticker in tickers:
    stock_name.append(stock.get_market_ticker_name(ticker))
    
df = pd.DataFrame({"stock_code":tickers,"stock_name":stock_name})
    
#st.table(df)

############################################################################################################################################
# 1. Select Box # 1개 선택
# select_species 변수에 사용자가 선택한 값이 지정됩니다
#select_stock = st.sidebar.selectbox(
#    '종목을 선택하세요',
#    stock_name
#    #['setosa','versicolor','virginica']
#)

#df = stock.get_market_ohlcv("19900101", str(today).replace("-",""), select_stock)
# 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다

# 선택한 종의 맨 처음 5행을 보여줍니다 
#st.table(df)

# 3. Radio / Slider
# 라디오에 선택한 내용을 radio select변수에 담습니다
radio_select =st.sidebar.radio(
    "원하는 전략을 선택하세요",
    ["전략미사용",'절대모멘텀','고배당전략(제작중)'])
    #horizontal=True)
#radio_select = "절대모멘텀"
############################################################################################################################################

if radio_select == "절대모멘텀":
    # 2. multi select
    # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    # return : list
    select_multi_species = st.sidebar.multiselect(
        '종목을 선택하세요 (복수선택가능)',
        stock_name
        #['setosa','versicolor','virginica']
    
    )
    
    code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
    
    # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #tmp_df = df[df['species'].isin(select_multi_species)]
    # 선택한 종들의 결과표를 나타냅니다.  
    #
    
    ############################################################################################################################################
    # 3. Slider
    # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    radio_ma =st.sidebar.radio(
        "전략에 사용할 이평선 갯수를 고르세요",
        [1,2,3])
    
    if radio_ma == 1:
        slider_range1 = st.sidebar.slider(
            "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
    elif radio_ma==2:
        slider_range1 = st.sidebar.slider(
            "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
        slider_range2 = st.sidebar.slider(
            "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
    else:
        slider_range1 = st.sidebar.slider(
            "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
        slider_range2 = st.sidebar.slider(
            "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
        slider_range3 = st.sidebar.slider(
            "전략3 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
             1, #시작 값 
             200, #끝 값  
             value=60
            #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
        )
    
    # 필터 적용버튼 생성 
    start_button = st.sidebar.button(
        "START 📊 "#"버튼에 표시될 내용"
    )
    
    # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    if start_button:
        #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
        if len(select_multi_species) != 0:
            df_cump = pd.DataFrame()
            for code in code_list:
                df_tmp = stock.get_market_ohlcv("20000101",str(today).replace("-",""), code).dropna()
                df_tmp["등락률"]=df_tmp["등락률"]/100
                df_tmp = df_tmp.reset_index()
                df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                
                if df_cump.shape[0] == 0:
                    df_tmp["ma1"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
                    if radio_ma > 1:
                        df_tmp["ma2"] = df_tmp["종가"].shift(1).rolling(slider_range2).mean()
                        if radio_ma > 2:
                            df_tmp["ma3"] = df_tmp["종가"].shift(1).rolling(slider_range3).mean()
                            
                    df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma1"],1,0)
                    if radio_ma > 1:
                        df_tmp["flag2"] = np.where(df_tmp["종가"] > df_tmp["ma2"],1,0)
                        df_tmp["flag"] *= df_tmp["flag2"]
                        if radio_ma > 2:
                            df_tmp["flag3"] = np.where(df_tmp["종가"] > df_tmp["ma3"],1,0)
                            df_tmp["flag"] *= df_tmp["flag3"]
                            
                    df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
                    df_tmp = df_tmp.dropna()
                    df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
                    df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
                else:
                    df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
                    df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
                    df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
                    df_tmp = df_tmp.dropna()
                    df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
                    df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
            
            df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
            df_cump = df_cump.set_index("날짜").mean(1)
            #df_cump = (df_cump+1).cumprod()-1
            
            
            
            #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
            #st.write(fig)
            
            # 퀀트스탯 메트릭 생성
            
            # Streamlit 애플리케이션 생성
            st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
            st.write("")
            st.write("연율화 수익률 : " + str(qs.stats.cagr(df_tmp["등락률"]).round(3)*100)+'%' + "\nMDD : " + str(qs.stats.max_drawdown(df_tmp["등락률"]).round(3)*100)+"%")
            st.write("")
            # 퀀트스탯 메트릭 정보 출력
            st.write("Portfolio Return")
            st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
            
            st.write("Monthly Return")
            st.write(qs.plots.monthly_heatmap(df_cump, show=False))
            
            st.write("Yearly Return")
            st.write(qs.plots.yearly_returns(df_cump, show=False))
            
            st.write("Monthly Return Histogram")
            st.write(qs.plots.histogram(df_cump, show=False))
            
            #st.line_chart(df_cump)
        
        #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
        #st.table(tmp_df)
        # 성공문구 + 풍선이 날리는 특수효과 
        st.sidebar.success("Filter Applied!")
        #st.toast('portfolio 수익률을 확인해보세요', icon='😍')
        #st.balloons()
elif radio_select == "전략미사용":
    # 2. multi select
    # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    # return : list
    select_multi_species = st.sidebar.multiselect(
        '종목을 선택하세요. (복수선택가능)',
        stock_name
        #['setosa','versicolor','virginica']
    
    )
    
    code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
    
    # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #tmp_df = df[df['species'].isin(select_multi_species)]
    # 선택한 종들의 결과표를 나타냅니다.  
    #
    
    ############################################################################################################################################
    # 3. Slider
    # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    
    # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    if True:
        #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
        if len(select_multi_species) != 0:
            df_cump = pd.DataFrame()
            for code in code_list:
                df_tmp = stock.get_market_ohlcv("20000101",str(today).replace("-",""), code).dropna()
                df_tmp["등락률"]=df_tmp["등락률"]/100
                df_tmp = df_tmp.reset_index()
                df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                
                if df_cump.shape[0] == 0:
                    #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
                    #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
                    #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
                    df_tmp = df_tmp.dropna()
                    #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
                    df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
                else:
                    #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
                    #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
                    #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
                    df_tmp = df_tmp.dropna()
                    #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
                    df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
            
            df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
            df_cump = df_cump.set_index("날짜").mean(1)
            #df_cump = (df_cump+1).cumprod()-1
            
            
            
            #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
            #st.write(fig)
            
            # 퀀트스탯 메트릭 생성
            
            # Streamlit 애플리케이션 생성
            st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
            
            # 퀀트스탯 메트릭 정보 출력
            st.write("Portfolio Return")
            st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
            
            st.write("Monthly Return")
            st.write(qs.plots.monthly_heatmap(df_cump, show=False))
            
            st.write("Yearly Return")
            st.write(qs.plots.yearly_returns(df_cump, show=False))
            
            st.write("Monthly Return Histogram")
            st.write(qs.plots.histogram(df_cump, show=False))
            
            #st.line_chart(df_cump)
        
        #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
        #st.table(tmp_df)
        # 성공문구 + 풍선이 날리는 특수효과 
        st.sidebar.success("Filter Applied!")
        #st.toast('portfolio 수익률을 확인해보세요')# , icon='😍'
        #st.balloons()
else:
    st.write("추가 중")
############################################################################################################################################

