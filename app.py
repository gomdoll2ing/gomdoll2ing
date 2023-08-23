import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st

from pykrx import stock
from pykrx import bond

import quantstats as qs
from quantstats.reports import html
import seaborn as sns  

plt.rcParams['font.family'] = 'NanumGothic' #: 한글 깨짐시 font 변경


############################################################################################################################################


# Side bar
# 사이드바에 select box를 활용하여 종을 선택한 다음 그에 해당하는 행만 추출하여 데이터프레임을 만들고자합니다.
st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
st.write("자신의 전략을 직접 만들어보세요 (좌측 상단 Filter를 열어주세요)")
st.write("")
st.sidebar.title('Stock Analysis📊')

## 날짜/시간 Input
import datetime
past = st.sidebar.date_input("날짜를 선택하세요 (Start)", datetime.datetime.now()-datetime.timedelta(days=365*30))
today = st.sidebar.date_input("날짜를 선택하세요 (End)", datetime.datetime.now())

# 날짜 간의 차이 계산
date_difference = today - past

# 차이를 일(day)로 변환하여 int로 표현
difference_in_days = date_difference.days

#st.write("날짜 차이 (일):", difference_in_days)
#the_time = st.sidebar.time_input("시간을 입력하세요.", datetime.time())

radio_stock =st.sidebar.radio(
    "주식 & ETF",
    ["주식",'ETF']
    )

if radio_stock=='주식':
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
        ["전략미사용",'이동평균선_전략','고배당_전략'])
        #horizontal=True)
    #radio_select = "절대모멘텀"
    ############################################################################################################################################
    
    if radio_select == "이동평균선_전략":
        if date_difference < datetime.timedelta(days=40):
            original_title = '<p style="font-family:Courier; color:Red; font-size: 30px;">날짜 기간이 너무 짧습니다</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
        # 2. multi select
        # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
        # return : list
        select_multi_species = st.sidebar.multiselect(
            '[이동평균선_전략] 종목을 선택하세요 (복수선택가능)',
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
            "(Stock) 선택한 이동평균선보다 종가가 높으면 매수, 낮으면 매도 하는 전략",
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
                df_cor = pd.DataFrame()
                for code in code_list:
                    df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                    df_tmp["등락률"]=df_tmp["등락률"]/100
                    df_tmp = df_tmp.reset_index()
                    df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                    
                    if df_cump.shape[0] == 0:
                        df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
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
                        df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
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
                
                st.write("")
                st.write("당신의 포트폴리오는")
                st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
                st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
                st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
                st.write("")
                if len(code_list) >= 2:
                    # df_cor = list()
                    # new_column_names = []
                    # for code in code_list:
                    #     new_column_names.append(stock.get_market_ticker_name(code))
                    #     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                    #     df_tmp["등락률"]=df_tmp["등락률"]/100
                    #     df_tmp = df_tmp.reset_index()
                    #     df_tmp = df_tmp.rename(columns={"등락률":stock.get_market_ticker_name(code)})
                    #     df_cor.append(df_tmp.iloc[:,-1].tolist())
                    
                    
                    # # 데이터프레임 변환 및 시각화
                    # df_cor = pd.DataFrame(df_cor).transpose()
                    #df_cor = df_cor.apply(lambda x:round(x,2))
                    
                    # 컬럼 이름 변경
                    df_cor = df_cor.iloc[:,1:]
                    new_column_names = [stock.get_market_ticker_name(col) for col in df_cor.columns]
                    df_cor.columns = new_column_names
                    cor = df_cor.corr()
                    # 색상 및 투명도 설정
                    def color_score(val):
                        if val >= 0.5:
                            color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
                        else:
                            color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
                        return color
                    st.write("")
                    st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
                    st.table(cor.style.applymap(color_score))
                    
                st.write("")
                # 퀀트스탯 메트릭 정보 출력
                st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
                st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                
                st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
                st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                
                st.write("연도별 수익률을 확인해보세요")
                st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
                st.write(qs.plots.yearly_returns(df_cump, show=False))
                
                st.write("월 수익률 히스토그램을 확인해보세요")
                st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
                st.write(qs.plots.histogram(df_cump, show=False))
                st.write("")
                
                iframe_html1 = """
                <div style='display: flex;'>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                </div>
                """
                
                st.markdown(iframe_html1, unsafe_allow_html=True)
                
                st.write("")
                original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.write("")
                warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
                st.markdown(warning, unsafe_allow_html=True)
                
                #st.line_chart(df_cump)
            
            #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
            #st.table(tmp_df)
            # 성공문구 + 풍선이 날리는 특수효과 
            st.sidebar.success("Filter Applied!")
            iframe_html = """
            <div style='display: flex;'>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%;'>
                    <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
            </div>
            """
            
            st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
            
            original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
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
        start_button = st.sidebar.button(
            "START 📊 "#"버튼에 표시될 내용"
        )
        # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
        # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
        if start_button:
            #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
            if len(select_multi_species) != 0:
                df_cump = pd.DataFrame()
                df_cor = pd.DataFrame()
                for code in code_list:
                    df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                    df_tmp["등락률"]=df_tmp["등락률"]/100
                    df_tmp = df_tmp.reset_index()
                    df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                    
                    if df_cump.shape[0] == 0:
                        df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
                        #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
                        #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
                        #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
                        df_tmp = df_tmp.dropna()
                        #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
                        df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
                    else:
                        df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
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
                #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
                st.write("")
                st.write("당신의 포트폴리오는")
                st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
                st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
                st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
                st.write("")
                if len(code_list) >= 2:
                    df_cor = list()
                    new_column_names = []
                    for code in code_list:
                        new_column_names.append(stock.get_market_ticker_name(code))
                        df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                        df_tmp["등락률"]=df_tmp["등락률"]/100
                        df_tmp = df_tmp.reset_index()
                        df_tmp = df_tmp.rename(columns={"등락률":stock.get_market_ticker_name(code)})
                        df_cor.append(df_tmp.iloc[:,-1].tolist())
                    
                    # 데이터프레임 변환 및 시각화
                    df_cor = df_cor.iloc[:,1:]
                    new_column_names = [stock.get_market_ticker_name(col) for col in df_cor.columns]
                    df_cor.columns = new_column_names
                    cor = df_cor.corr()
                    
                    # 색상 및 투명도 설정
                    def color_score(val):
                        if val >= 0.5:
                            color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
                        else:
                            color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
                        return color
                    st.write("")
                    st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
                    st.table(cor.style.applymap(color_score))
                    
                st.write("")
                # 퀀트스탯 메트릭 정보 출력
                st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
                st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                
                st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
                st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                
                st.write("연도별 수익률을 확인해보세요")
                st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
                st.write(qs.plots.yearly_returns(df_cump, show=False))
                
                st.write("월 수익률 히스토그램을 확인해보세요")
                st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
                st.write(qs.plots.histogram(df_cump, show=False))
                st.write("")
                
                iframe_html1 = """
                <div style='display: flex;'>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                </div>
                """
                
                st.markdown(iframe_html1, unsafe_allow_html=True)
                st.write("")
                original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.write("")
                warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
                st.markdown(warning, unsafe_allow_html=True)
                
                #st.line_chart(df_cump)
            
            #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
            #st.table(tmp_df)
            # 성공문구 + 풍선이 날리는 특수효과 
            st.sidebar.success("Filter Applied!")
            
            iframe_html = """
            <div style='display: flex;'>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%;'>
                    <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
            </div>
            """
            
            st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
            
            original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
            #st.toast('portfolio 수익률을 확인해보세요')# , icon='😍'
            #st.balloons()
    else:
        df = stock.get_market_fundamental_by_ticker(date='20230822', market="ALL")
        df = df.sort_values("DIV", ascending=False).head(20)
        df.index = [stock.get_market_ticker_name(s) for s in df.index]
        df=df.rename(columns={"DIV":"배당수익률","DPS":"주당배당금"})
        
        dps = '<p style="font-family:Courier; color:Blue; font-size: 20px;">배당수익률 상위 10개 종목 매수 전략</p>'
        st.markdown(dps, unsafe_allow_html=True)
        
        html_blog='한국 배당주 투자 참고 게시물 [link](https://blog.naver.com/koreanfinancetime/223119607639)'
        st.markdown(html_blog,unsafe_allow_html=True)
        
        # Score 컬럼 값에 따라 색상 지정
        def color_score(val):
            color = 'background-color: green' if val >= 10 else 'background-color: red'
            return color
        
        df = df.style.applymap(color_score, subset=pd.IndexSlice[:, ['배당수익률']])
        
        st.table(df)
        st.write("")
        st.write("")
        
        iframe_html = """
        <div style='display: flex;'>
            <div style='flex: 33.33%; padding-right: 10px;'>
                <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%; padding-right: 10px;'>
                <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%;'>
                <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%;'>
                <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
        </div>
        """
        
        st.markdown(iframe_html, unsafe_allow_html=True)
        
        original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
        st.markdown(original_title, unsafe_allow_html=True)
        
        warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
        st.markdown(warning, unsafe_allow_html=True)
        
else:
    tickers = stock.get_etf_ticker_list(str(today).replace("-",""))
    stock_name = []
    
    for ticker in tickers:
        stock_name.append(stock.get_etf_ticker_name(ticker))
        
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
        "원하는 ETF 전략을 선택하세요",
        ["전략미사용",'이동평균선_전략',"고배당_전략"]
        )
        #horizontal=True)
    #radio_select = "절대모멘텀"
    ############################################################################################################################################
    
    if radio_select == "이동평균선_전략":
        if date_difference < datetime.timedelta(days=40):
            original_title = '<p style="font-family:Courier; color:Red; font-size: 30px;">날짜 기간이 너무 짧습니다</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
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
            "(ETF) 선택한 이동평균선보다 종가가 높으면 매수, 낮으면 매도 하는 전략",
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
                df_cor = pd.DataFrame()
                for code in code_list:
                    df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                    df_tmp["등락률"] = df_tmp["종가"].pct_change().dropna()
                    #df_tmp["등락률"]=df_tmp["등락률"]/100
                    df_tmp = df_tmp.reset_index()
                    df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                    
                    if df_cump.shape[0] == 0:
                        df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
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
                        df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
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
                #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
                st.write("")
                st.write("당신의 포트폴리오는")
                st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
                st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
                st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
                st.write("")
                if len(code_list) >= 2:
                    df_cor = list()
                    new_column_names = []
                    for code in code_list:
                        new_column_names.append(stock.get_etf_ticker_name(code))
                        df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                        df_tmp["등락률"]=df_tmp["등락률"]/100
                        df_tmp = df_tmp.reset_index()
                        df_tmp = df_tmp.rename(columns={"등락률":stock.get_etf_ticker_name(code)})
                        df_cor.append(df_tmp.iloc[:,-1].tolist())
                    
                    
                    # 데이터프레임 변환 및 시각화
                    df_cor = df_cor.iloc[:,1:]
                    new_column_names = [stock.get_market_ticker_name(col) for col in df_cor.columns]
                    df_cor.columns = new_column_names
                    cor = df_cor.corr()
                    
                    # 색상 및 투명도 설정
                    def color_score(val):
                        if val >= 0.5:
                            color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
                        else:
                            color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
                        return color
                    st.write("")
                    st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
                    st.table(cor.style.applymap(color_score))
                    
                st.write("")
                # 퀀트스탯 메트릭 정보 출력
                st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
                st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                
                st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
                st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                
                st.write("연도별 수익률을 확인해보세요")
                st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
                st.write(qs.plots.yearly_returns(df_cump, show=False))
                
                st.write("월 수익률 히스토그램을 확인해보세요")
                st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
                st.write(qs.plots.histogram(df_cump, show=False))
                st.write("")
                
                iframe_html1 = """
                <div style='display: flex;'>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                </div>
                """
                
                st.markdown(iframe_html1, unsafe_allow_html=True)
                st.write("")
                original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.write("")
                warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
                st.markdown(warning, unsafe_allow_html=True)
                
                #st.line_chart(df_cump)
            
            #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
            #st.table(tmp_df)
            # 성공문구 + 풍선이 날리는 특수효과 
            st.sidebar.success("Filter Applied!")
            iframe_html = """
            <div style='display: flex;'>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%;'>
                    <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
            </div>
            """
            
            st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
            
            original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
            
            
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
                    df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                    df_tmp["등락률"] = df_tmp["종가"].pct_change().dropna()
                    #df_tmp["등락률"]=df_tmp["등락률"]/100
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
                #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
                st.write("")
                st.write("당신의 포트폴리오는")
                st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
                st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
                st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
                st.write("")
                if len(code_list) >= 2:
                    df_cor = list()
                    new_column_names = []
                    for code in code_list:
                        new_column_names.append(stock.get_etf_ticker_name(code))
                        df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
                        df_tmp["등락률"]=df_tmp["등락률"]/100
                        df_tmp = df_tmp.reset_index()
                        df_tmp = df_tmp.rename(columns={"등락률":stock.get_etf_ticker_name(code)})
                        df_cor.append(df_tmp.iloc[:,-1].tolist())
                    
                    
                    # 데이터프레임 변환 및 시각화
                    df_cor = pd.DataFrame(df_cor).transpose()
                    df_cor = df_cor.apply(lambda x:round(x,2))
                    
                    # 컬럼 이름 변경
                    df_cor.columns = new_column_names
                    
                    cor = df_cor.corr()
                    # 색상 및 투명도 설정
                    def color_score(val):
                        if val >= 0.5:
                            color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
                        else:
                            color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
                        return color
                    st.write("")
                    st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
                    st.table(cor.style.applymap(color_score))
                    
                st.write("")
                # 퀀트스탯 메트릭 정보 출력
                st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
                st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                
                st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
                st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                
                st.write("연도별 수익률을 확인해보세요")
                st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
                st.write(qs.plots.yearly_returns(df_cump, show=False))
                
                st.write("월 수익률 히스토그램을 확인해보세요")
                st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
                st.write(qs.plots.histogram(df_cump, show=False))
                st.write("")
                
                iframe_html1 = """
                <div style='display: flex;'>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%; padding-right: 10px;'>
                        <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                    <div style='flex: 33.33%;'>
                        <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                    </div>
                </div>
                """
                
                st.markdown(iframe_html1, unsafe_allow_html=True)
                st.write("")
                original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
                st.markdown(original_title, unsafe_allow_html=True)
                st.write("")
                warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
                st.markdown(warning, unsafe_allow_html=True)
                
                #st.line_chart(df_cump)
            
            #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
            #st.table(tmp_df)
            # 성공문구 + 풍선이 날리는 특수효과 
            st.sidebar.success("Filter Applied!")
            iframe_html = """
            <div style='display: flex;'>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%; padding-right: 10px;'>
                    <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
                <div style='flex: 33.33%;'>
                    <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
                </div>
            </div>
            """
            
            st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
            
            original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
            st.sidebar.markdown(original_title, unsafe_allow_html=True)
            
            #st.toast('portfolio 수익률을 확인해보세요')# , icon='😍'
            #st.balloons()
    else:
        div_df = stock.get_index_fundamental(date='20230822')
        div_df = div_df.sort_values("배당수익률", ascending=False).head(20)

        
        etf_dps = '<p style="font-family:Courier; color:Blue; font-size: 20px;">배당수익률 상위 종목 매수 전략</p>'
        st.markdown(etf_dps, unsafe_allow_html=True)
        
        html_blog='한국 배당주 투자 참고 게시물 [link](https://blog.naver.com/koreanfinancetime/223119607639)'
        st.markdown(html_blog,unsafe_allow_html=True)
        
        # Score 컬럼 값에 따라 색상 지정
        def color_score(val):
            color = 'background-color: green' if val >= 3 else 'background-color: red'
            return color
        
        div_df = div_df.style.applymap(color_score, subset=pd.IndexSlice[:, ['배당수익률']])

        
        # Styler 객체를 HTML로 변환하여 출력
        st.write(div_df.to_html(escape=False), unsafe_allow_html=True)
        
        #st.table(div_df)
        st.write("")
        st.write("")
        
        iframe_html = """
        <div style='display: flex;'>
            <div style='flex: 33.33%; padding-right: 10px;'>
                <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%; padding-right: 10px;'>
                <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%;'>
                <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
            <div style='flex: 33.33%;'>
                <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
            </div>
        </div>
        """
        
        st.markdown(iframe_html, unsafe_allow_html=True)
        
        original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
        st.markdown(original_title, unsafe_allow_html=True)
        
        warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
        st.markdown(warning, unsafe_allow_html=True)
        
############################################################################################################################################

