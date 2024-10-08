import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import json
from streamlit_javascript import st_javascript

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import time

# Set the page configuration
st.set_page_config(page_title="Unified Game and Script Extractor", layout="centered", initial_sidebar_state="collapsed")

# Create a navigation menu
with st.sidebar:
    selected = option_menu("Main Menu", ["Game", "Map Maker", "Map Store", "YouTube Script Extractor"],
                           icons=["controller", "pencil", "archive", "youtube"], menu_icon="menu-app", default_index=0)

# Initialize an empty dictionary to store maps if not exist
if "maps" not in st.session_state:
    st.session_state.maps = []

# Function to handle saving the map from the session state
def save_map(map_data):
    st.session_state.maps.append(json.loads(map_data))
    st.success("맵이 저장되었습니다!")

# Game Page
if selected == "Game":
    # The updated HTML code for the game with responsive design and all necessary control buttons
    html_code = """
    <!DOCTYPE html> 
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        #gameContainer {
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px; /* Fixed height */
            width: 100%;
            overflow: hidden; /* Prevent the container itself from scrolling */
            background-color: #f0f0f0; /* Background for fullscreen mode */
        }
        #gameCanvas {
            border: 1px solid black;
            width: 100%;  /* Make sure canvas adapts to its container's width */
            height: 100%; /* Match the height of gameContainer */
            max-width: 800px; /* Set a max-width to avoid exceeding container */
        }
        .control-pad {
            position: absolute;
            background-color: rgba(0, 0, 0, 0.2); /* Light transparent background */
            border-radius: 50%;
            z-index: 10;
        }
        #leftControl {
            left: 20px;
            bottom: 20px;
            width: 150px;
            height: 150px;
        }
        #rightControl {
            right: 20px;
            bottom: 20px;
            width: 75px;
            height: 75px;
        }
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden; /* Prevent page-level scrolling */
            height: 100%; /* Ensure the page takes full height */
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <div id="leftControl" class="control-pad"></div>
        <div id="rightControl" class="control-pad"></div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 자동으로 캔버스 크기를 컨테이너에 맞게 조정
        function resizeCanvas() {
            const container = document.getElementById('gameContainer');
            canvas.width = container.clientWidth; // 컨테이너의 너비에 맞게 설정
            canvas.height = container.clientHeight; // 컨테이너의 높이에 맞게 설정
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const player = {
            x: 50, y: 200, width: 30, height: 30,
            speed: 2.5, jumpForce: 10, gravity: 0.5,
            jumping: false, velocityY: 0
        };

        const door = { x: 0, y: 0, width: 40, height: 60 };

        let platforms = [];
        let enemies = [];
        let coins = [];
        let currentLevel = 0;
        let levelStartTime = 0;
        let totalTime = 0;
        let totalCoins = 0;
        const levelTime = 15000; // 15 seconds per level

        const keys = {};
        
        // 키보드 이벤트 리스너 추가
        document.addEventListener('keydown', (e) => keys[e.code] = true);
        document.addEventListener('keyup', (e) => keys[e.code] = false);

        function getRandomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        function generateMap() {
            platforms = [{ x: 0, y: canvas.height - 50, width: canvas.width, height: 50, isGround: true }];
            enemies = [];
            coins = [];
            
            const numPlatforms = getRandomInt(3, 6);
            for (let i = 0; i < numPlatforms; i++) {
                platforms.push({
                    x: getRandomInt(100, canvas.width - 200),
                    y: getRandomInt(100, canvas.height - 150),
                    width: getRandomInt(100, 200),
                    height: 20,
                    isGround: false
                });
            }

            let doorPlaced = false;
            while (!doorPlaced) {
                const randomPlatform = platforms[getRandomInt(1, platforms.length - 1)];
                door.x = randomPlatform.x + randomPlatform.width / 2 - door.width / 2;
                door.y = randomPlatform.y - door.height;
                
                if (door.x > 0 && door.x + door.width < canvas.width) {
                    doorPlaced = true;
                }
            }

            const numEnemies = getRandomInt(1, 2);
            for (let i = 0; i < numEnemies; i++) {
                const randomPlatform = platforms[getRandomInt(0, platforms.length - 1)];
                enemies.push({
                    x: randomPlatform.x + getRandomInt(0, randomPlatform.width - 30),
                    y: randomPlatform.y - 30,
                    width: 30,
                    height: 30,
                    speed: getRandomInt(0.5, 1.5) * (1 + currentLevel * 0.05) * (Math.random() > 0.5 ? 1 : -1), 
                    platform: randomPlatform
                });
            }

            const numCoins = getRandomInt(3, 5); // Generate 3 to 5 coins per level
            for (let i = 0; i < numCoins; i++) {
                const randomPlatform = platforms[getRandomInt(0, platforms.length - 1)];
                coins.push({
                    x: randomPlatform.x + getRandomInt(0, randomPlatform.width - 20),
                    y: randomPlatform.y - 20,
                    width: 15,
                    height: 15
                });
            }

            player.x = 50;
            player.y = 300;
            levelStartTime = Date.now();
        }

        function update() {
            const currentTime = Date.now();
            const elapsedTime = currentTime - levelStartTime;
            const timeLeft = Math.max(0, levelTime - elapsedTime);

            if (keys['ArrowLeft']) player.x -= player.speed;
            if (keys['ArrowRight']) player.x += player.speed;

            if (keys['Space'] && !player.jumping) {
                player.jumping = true;
                player.velocityY = -player.jumpForce;
            }

            player.velocityY += player.gravity;
            player.y += player.velocityY;

            for (let platform of platforms) {
                if (!platform.isGround && timeLeft < 5000) {
                    platform.y += 0.5;
                }
                if (player.x < platform.x + platform.width &&
                    player.x + player.width > platform.x &&
                    player.y + player.height > platform.y &&
                    player.y < platform.y + platform.height) {
                    player.y = platform.y - player.height;
                    player.jumping = false;
                    player.velocityY = 0;
                }
            }

            if (!door.isGround && timeLeft < 5000) {
                door.y += 0.5;
            }

            for (let enemy of enemies) {
                enemy.x += enemy.speed;
                if (enemy.x <= enemy.platform.x || enemy.x + enemy.width >= enemy.platform.x + enemy.platform.width) {
                    enemy.speed *= -1;
                }

                if (timeLeft < 5000) {
                    enemy.y += 0.5;
                }

                if (player.x < enemy.x + enemy.width &&
                    player.x + player.width > enemy.x &&
                    player.y < enemy.y + enemy.height &&
                    player.y + player.height > enemy.y) {
                    if (totalCoins >= 10) {
                        totalCoins -= 10; // Use 10 coins to revive
                        player.x = 50;
                        player.y = 300;
                    } else {
                        totalCoins = 0;
                        currentLevel = 0;
                        generateMap();
                    }
                    return;
                }
            }

            // 동전 수집 처리
            coins = coins.filter(coin => {
                if (player.x < coin.x + coin.width &&
                    player.x + player.width > coin.x &&
                    player.y < coin.y + coin.height &&
                    player.y + player.height > coin.y) {
                    totalCoins++;
                    return false; // Remove collected coin
                }
                return true;
            });

            if (player.x < 0) player.x = 0;
            if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
            if (player.y + player.height > canvas.height) {
                player.y = canvas.height - player.height;
                player.jumping = false;
                player.velocityY = 0;
            }

            if (player.x < door.x + door.width &&
                player.x + player.width > door.x &&
                player.y < door.y + door.height &&
                keys['ArrowUp']) {
                currentLevel++;
                totalTime += elapsedTime;
                generateMap();
            }

            if (timeLeft === 0) {
                alert('시간 초과! 게임 오버');
                currentLevel = 0;
                totalCoins = 0;
                totalTime = 0;
                generateMap();
            }
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'red';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            ctx.fillStyle = 'green';
            for (let platform of platforms) {
                ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
            }

            ctx.fillStyle = 'blue';
            ctx.fillRect(door.x, door.y, door.width, door.height);

            ctx.fillStyle = 'purple';
            for (let enemy of enemies) {
                ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
            }

            // 동전 렌더링
            ctx.fillStyle = 'gold';
            for (let coin of coins) {
                ctx.beginPath();
                ctx.arc(coin.x + coin.width / 2, coin.y + coin.height / 2, coin.width / 2, 0, Math.PI * 2);
                ctx.fill();
            }

            ctx.fillStyle = 'black';
            ctx.font = '16px Arial';
            const currentTime = Date.now();
            const elapsedTime = currentTime - levelStartTime;
            const timeLeft = Math.max(0, levelTime - elapsedTime);
            ctx.fillText(`레벨: ${currentLevel + 1}`, 10, 25);
            ctx.fillText(`남은 시간: ${Math.ceil(timeLeft / 1000)}초`, 10, 50);
            
            ctx.textAlign = 'right';
            ctx.fillText(`총 시간: ${Math.ceil((totalTime + elapsedTime) / 1000)}초`, canvas.width - 10, 25);
            ctx.fillText(`동전: ${totalCoins}`, canvas.width - 10, 50);
            ctx.textAlign = 'left';
        }

        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        generateMap();
        gameLoop();

        // 터치 이벤트 추가
        const leftControl = document.getElementById('leftControl');
        const rightControl = document.getElementById('rightControl');

        let startX = 0;
        let startY = 0;

        leftControl.addEventListener('touchstart', (event) => {
            event.preventDefault();
            const touch = event.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
        });

        leftControl.addEventListener('touchmove', (event) => {
            event.preventDefault();
            const touch = event.touches[0];
            const currentX = touch.clientX;
            const currentY = touch.clientY;

            if (currentX < startX - 15) {
                keys['ArrowLeft'] = true;
                keys['ArrowRight'] = false;
            } else if (currentX > startX + 15) {
                keys['ArrowRight'] = true;
                keys['ArrowLeft'] = false;
            } else {
                keys['ArrowLeft'] = false;
                keys['ArrowRight'] = false;
            }

            if (startY - currentY > 20) {
                keys['ArrowUp'] = true;
            } else {
                keys['ArrowUp'] = false;
            }
        });

        leftControl.addEventListener('touchend', (event) => {
            event.preventDefault();
            keys['ArrowLeft'] = false;
            keys['ArrowRight'] = false;
            keys['ArrowUp'] = false;
        });

        rightControl.addEventListener('touchstart', (event) => {
            event.preventDefault();
            keys['Space'] = true;
        });

        rightControl.addEventListener('touchend', (event) => {
            event.preventDefault();
            keys['Space'] = false;
        });

        function enterFullscreen() {
            const gameContainer = document.getElementById('gameContainer');
            if (gameContainer.requestFullscreen) {
                gameContainer.requestFullscreen();
            } else if (gameContainer.webkitRequestFullscreen) {
                gameContainer.webkitRequestFullscreen();
            } else if (gameContainer.msRequestFullscreen) {
                gameContainer.msRequestFullscreen();
            }
        }

        window.addEventListener('load', () => {
            if (window.innerWidth <= 768) {
                enterFullscreen();
            }
        });
    </script>
</body>
</html>
    """
    components.html(html_code, height=430, scrolling=False)

# Map Maker Page
elif selected == "Map Maker":
    st.subheader("Map Maker")
    map_maker_html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            #mapCanvas {
                border: 1px solid black;
                width: 100%;
                max-width: 800px;
                height: 400px;
                background-color: #f8f8f8;
            }
            #controls {
                margin-top: 10px;
            }
            .button {
                padding: 5px 10px;
                margin: 5px;
                background-color: #007BFF;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 4px;
            }
            .button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <canvas id="mapCanvas"></canvas>
        <div id="controls">
            <button class="button" onclick="setTool('platform')">땅 추가</button>
            <button class="button" onclick="setTool('enemy')">몬스터 추가</button>
            <button class="button" onclick="setTool('door')">문 추가</button>
            <button class="button" onclick="saveMap()">맵 저장</button>
        </div>

        <script>
            const canvas = document.getElementById('mapCanvas');
            const ctx = canvas.getContext('2d');
            const objects = [];
            let currentTool = null;

            canvas.width = canvas.clientWidth;
            canvas.height = canvas.clientHeight;

            function setTool(tool) {
                currentTool = tool;
            }

            canvas.addEventListener('click', (e) => {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                if (currentTool === 'platform') {
                    objects.push({ type: 'platform', x: x, y: y, width: 100, height: 20 });
                } else if (currentTool === 'enemy') {
                    objects.push({ type: 'enemy', x: x, y: y, width: 30, height: 30 });
                } else if (currentTool === 'door') {
                    objects.push({ type: 'door', x: x, y: y, width: 40, height: 60 });
                }
                draw();
            });

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                objects.forEach(obj => {
                    if (obj.type === 'platform') {
                        ctx.fillStyle = 'green';
                        ctx.fillRect(obj.x, obj.y, obj.width, obj.height);
                    } else if (obj.type === 'enemy') {
                        ctx.fillStyle = 'purple';
                        ctx.fillRect(obj.x, obj.y, obj.width, obj.height);
                    } else if (obj.type === 'door') {
                        ctx.fillStyle = 'blue';
                        ctx.fillRect(obj.x, obj.y, obj.width, obj.height);
                    }
                });
            }

            function saveMap() {
                if (objects.length === 0) {
                    alert("맵에 요소가 없습니다.");
                    return;
                }

                const mapData = JSON.stringify(objects);
                
                // Instead of postMessage, use return statement to send data to Streamlit directly
                window.streamlitWebResult = mapData;
                window.parent.postMessage({ type: 'save_map', data: mapData }, '*'); // 데이터 전송
            }
        </script>
    </body>
    </html>
    """
    components.html(map_maker_html, height=600, scrolling=False)

    # Add a button to trigger the map saving process
    if st.button("맵 저장하기"):
        # Use st_javascript to capture the result of map data when the save button is clicked
        result = st_javascript("""
            return window.streamlitWebResult;
        """)
        print(result)
        # Check if we received any map data and save it
        if result:
            save_map(result)

# Map Store Page
elif selected == "Map Store":
    st.subheader("저장된 맵 목록")
    if not st.session_state.maps:
        st.write("저장된 맵이 없습니다.")
    else:
        for idx, map_data in enumerate(st.session_state.maps):
            st.write(f"맵 {idx + 1}: {json.dumps(map_data, ensure_ascii=False)}")
            if st.button(f"이 맵 삭제하기", key=f"delete_map_{idx}"):
                st.session_state.maps.pop(idx)
                st.success(f"맵 {idx + 1}이 삭제되었습니다.")
                st.experimental_rerun()

# YouTube Script Extractor Page
if selected == "YouTube Script Extractor":
    # Function to extract script using youtube_transcript_api
    def get_script(url, language="ko"):
        error_txt = "사용자가 많습니다. 추출 버튼을 다시 한번 눌러주세요."
        for cnt in range(5):
            time.sleep(3)
            try:
                # Extract video ID from the URL
                video_id = url.split("v=")[-1].split("&")[0]

                # Attempt to get the transcript
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                if language in [t.language_code for t in transcript_list]:
                    transcript = transcript_list.find_transcript([language]).fetch()
                else:
                    # Fall back to default language if the requested language is unavailable
                    transcript = transcript_list.find_transcript(['en']).fetch()

                # Join the script text
                script_text = " ".join([entry['text'] for entry in transcript])
                return script_text

            except TranscriptsDisabled:
                error_txt += " 이 동영상에는 자막이 비활성화되어 있습니다."
                break
            except NoTranscriptFound:
                error_txt += " 이 동영상에 해당하는 언어의 자막이 없습니다."
                break
            except VideoUnavailable:
                error_txt += " 이 동영상을 찾을 수 없습니다."
                break
            except Exception as e:
                error_txt += f" 시도 {cnt + 1} 실패: {str(e)}"
                time.sleep(1)
                continue
        
        return f"Error: {error_txt}"

    # Initialize session state to store scripts
    if "scripts" not in st.session_state:
        st.session_state["scripts"] = []

    # Streamlit app
    st.title("YouTube Script Extractor")
    st.write("Enter a YouTube URL, and extract the video script!")

    # User inputs
    url = st.text_input("YouTube URL", "")
    language = st.selectbox("Select Language", ["ko", "en"])  # You can add more languages if needed

    if st.button("Extract Script"):
        iframe_html = """
            </br>
            </br>
            <iframe src="https://ads-partners.coupang.com/widgets.html?id=791090&template=carousel&trackingCode=AF1181191&subId=&width=700&height=100&tsource=" width="700" height="100" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics></iframe>
            """
            
        st.markdown(iframe_html, unsafe_allow_html=True)

        original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
        st.markdown(original_title, unsafe_allow_html=True)

        warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p></br>'
        st.markdown(warning, unsafe_allow_html=True)

        if url:
            with st.spinner("Extracting script... Please wait."):
                script = get_script(url, language)
                if "Error:" in script:
                    st.error(script)
                else:
                    st.success("Script extracted successfully!")
                    
                    # Extract the first sentence to use as a title
                    script_title = script.split('.')[0] if '.' in script else script[:50]
                    st.session_state["scripts"].append({"title": script_title, "content": script})
                    
                    # Display the extracted script below the button
                    st.subheader("Extracted Script")
                    st.text_area("Script Content", script, height=300, key="main_script_display")

    # Sidebar for displaying the list of extracted scripts
    st.sidebar.header("Extracted Scripts List")
    if st.session_state["scripts"]:
        selected_script_title = st.sidebar.selectbox(
            "Select a script to view",
            options=[s["title"] for s in st.session_state["scripts"]],
            key="script_select"
        )

        # Find the selected script content
        selected_script_content = next(
            s["content"] for s in st.session_state["scripts"] if s["title"] == selected_script_title
        )

        st.sidebar.subheader("Selected Script")
        st.sidebar.text_area("Script Content", selected_script_content, height=300, key="sidebar_script_display")

        iframe_html = """
            </br>
            </br>
            <iframe src="https://coupa.ng/cgeFzM" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics></iframe>
            """
            
        st.sidebar.markdown(iframe_html, unsafe_allow_html=True)

        original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
        st.sidebar.markdown(original_title, unsafe_allow_html=True)

        warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p></br>'
        st.sidebar.markdown(warning, unsafe_allow_html=True)
    else:
        st.sidebar.write("No scripts extracted yet.")






    # import numpy as np
    # import pandas as pd 
    # import matplotlib.pyplot as plt
    # import streamlit as st

    # from pykrx import stock
    # from pykrx import bond

    # import quantstats as qs
    # from quantstats.reports import html
    # import seaborn as sns  

    # plt.rcParams['font.family'] = 'NanumGothic' #: 한글 깨짐시 font 변경


    # ############################################################################################################################################


    # # Side bar
    # # 사이드바에 select box를 활용하여 종을 선택한 다음 그에 해당하는 행만 추출하여 데이터프레임을 만들고자합니다.
    # st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
    # st.write("자신의 전략을 직접 만들어보세요 (좌측 상단 Filter를 열어주세요)")
    # st.write("")
    # st.sidebar.title('Stock Analysis📊')

    # ## 날짜/시간 Input
    # import datetime
    # past = st.sidebar.date_input("날짜를 선택하세요 (Start)", datetime.datetime.now()-datetime.timedelta(days=365*30))
    # today = st.sidebar.date_input("날짜를 선택하세요 (End)", datetime.datetime.now()-datetime.timedelta(days=1))

    # # 날짜 간의 차이 계산
    # date_difference = today - past

    # # 차이를 일(day)로 변환하여 int로 표현
    # difference_in_days = date_difference.days

    # #st.write("날짜 차이 (일):", difference_in_days)
    # #the_time = st.sidebar.time_input("시간을 입력하세요.", datetime.time())

    # radio_stock =st.sidebar.radio(
    #     "주식 & ETF",
    #     ["주식",'ETF']
    #     )

    # if radio_stock=='주식':
    #     tickers = stock.get_market_ticker_list(str(today).replace("-",""), market="ALL")
    #     stock_name = []
        
    #     for ticker in tickers:
    #         stock_name.append(stock.get_market_ticker_name(ticker))
            
    #     df = pd.DataFrame({"stock_code":tickers,"stock_name":stock_name})
            
    #     #st.table(df)
        
    #     ############################################################################################################################################
    #     # 1. Select Box # 1개 선택
    #     # select_species 변수에 사용자가 선택한 값이 지정됩니다
    #     #select_stock = st.sidebar.selectbox(
    #     #    '종목을 선택하세요',
    #     #    stock_name
    #     #    #['setosa','versicolor','virginica']
    #     #)
        
    #     #df = stock.get_market_ohlcv("19900101", str(today).replace("-",""), select_stock)
    #     # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
        
    #     # 선택한 종의 맨 처음 5행을 보여줍니다 
    #     #st.table(df)
        
    #     # 3. Radio / Slider
    #     # 라디오에 선택한 내용을 radio select변수에 담습니다
    #     radio_select =st.sidebar.radio(
    #         "원하는 전략을 선택하세요",
    #         ["전략미사용",'이동평균선_전략','고배당_전략'])
    #         #horizontal=True)
    #     #radio_select = "절대모멘텀"
    #     ############################################################################################################################################
        
    #     if radio_select == "이동평균선_전략":
    #         if date_difference < datetime.timedelta(days=40):
    #             original_title = '<p style="font-family:Courier; color:Red; font-size: 30px;">날짜 기간이 너무 짧습니다</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
    #         # 2. multi select
    #         # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    #         # return : list
    #         select_multi_species = st.sidebar.multiselect(
    #             '주식 종목을 선택하세요 (복수선택가능)',
    #             stock_name
    #             #['setosa','versicolor','virginica']
            
    #         )
            
    #         code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
            
    #         # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #         #tmp_df = df[df['species'].isin(select_multi_species)]
    #         # 선택한 종들의 결과표를 나타냅니다.  
    #         #
            
    #         ############################################################################################################################################
    #         # 3. Slider
    #         # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    #         radio_ma =st.sidebar.radio(
    #             "(Stock) 선택한 이동평균선보다 종가가 높으면 매수, 낮으면 매도 하는 전략",
    #             [1,2,3])
            
    #         if radio_ma == 1:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #         elif radio_ma==2:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range2 = st.sidebar.slider(
    #                 "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #         else:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range2 = st.sidebar.slider(
    #                 "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range3 = st.sidebar.slider(
    #                 "전략3 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
            
    #         # 필터 적용버튼 생성 
    #         start_button = st.sidebar.button(
    #             "START 📊 "#"버튼에 표시될 내용"
    #         )
            
    #         # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    #         # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    #         if start_button:
    #             #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
    #             if len(select_multi_species) != 0:
    #                 df_cump = pd.DataFrame()
    #                 df_cor = pd.DataFrame()
    #                 for code in code_list:
    #                     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
    #                     df_tmp["등락률"]=df_tmp["등락률"]/100
    #                     df_tmp = df_tmp.reset_index()
    #                     df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                        
    #                     if df_cump.shape[0] == 0:
    #                         df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                         df_tmp["ma1"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
    #                         if radio_ma > 1:
    #                             df_tmp["ma2"] = df_tmp["종가"].shift(1).rolling(slider_range2).mean()
    #                             if radio_ma > 2:
    #                                 df_tmp["ma3"] = df_tmp["종가"].shift(1).rolling(slider_range3).mean()
                                    
    #                         df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma1"],1,0)
    #                         if radio_ma > 1:
    #                             df_tmp["flag2"] = np.where(df_tmp["종가"] > df_tmp["ma2"],1,0)
    #                             df_tmp["flag"] *= df_tmp["flag2"]
    #                             if radio_ma > 2:
    #                                 df_tmp["flag3"] = np.where(df_tmp["종가"] > df_tmp["ma3"],1,0)
    #                                 df_tmp["flag"] *= df_tmp["flag3"]
                                    
    #                         df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                     else:
    #                         df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
    #                         df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
    #                         df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
                    
    #                 df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
    #                 df_cump = df_cump.set_index("날짜").mean(1)
    #                 #df_cump = (df_cump+1).cumprod()-1
                    
                    
                    
    #                 #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
    #                 #st.write(fig)
                    
    #                 # 퀀트스탯 메트릭 생성
                    
    #                 # Streamlit 애플리케이션 생성
                    
    #                 st.write("")
    #                 st.write("당신의 포트폴리오는")
    #                 st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
    #                 st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
    #                 st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
    #                 st.write("")
    #                 if len(code_list) >= 2:
    #                     # df_cor = list()
    #                     # new_column_names = []
    #                     # for code in code_list:
    #                     #     new_column_names.append(stock.get_market_ticker_name(code))
    #                     #     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
    #                     #     df_tmp["등락률"]=df_tmp["등락률"]/100
    #                     #     df_tmp = df_tmp.reset_index()
    #                     #     df_tmp = df_tmp.rename(columns={"등락률":stock.get_market_ticker_name(code)})
    #                     #     df_cor.append(df_tmp.iloc[:,-1].tolist())
                        
                        
    #                     # # 데이터프레임 변환 및 시각화
    #                     # df_cor = pd.DataFrame(df_cor).transpose()
    #                     #df_cor = df_cor.apply(lambda x:round(x,2))
                        
    #                     # 컬럼 이름 변경
    #                     df_cor = df_cor.iloc[:,1:]
    #                     new_column_names = [stock.get_market_ticker_name(col) for col in df_cor.columns]
    #                     df_cor.columns = new_column_names
    #                     cor = df_cor.corr()
    #                     # 색상 및 투명도 설정
    #                     def color_score(val):
    #                         if val >= 0.5:
    #                             color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
    #                         else:
    #                             color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
    #                         return color
    #                     st.write("")
    #                     st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
    #                     st.table(cor.style.applymap(color_score))
                        
    #                 st.write("")
    #                 # 퀀트스탯 메트릭 정보 출력
    #                 st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
    #                 st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                    
    #                 st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
    #                 st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                    
    #                 st.write("연도별 수익률을 확인해보세요")
    #                 st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
    #                 st.write(qs.plots.yearly_returns(df_cump, show=False))
                    
    #                 st.write("월 수익률 히스토그램을 확인해보세요")
    #                 st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
    #                 st.write(qs.plots.histogram(df_cump, show=False))
    #                 st.write("")
                    
    #                 iframe_html1 = """
    #                 <div style='display: flex;'>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                 </div>
    #                 """
                    
    #                 st.markdown(iframe_html1, unsafe_allow_html=True)
                    
    #                 st.write("")
    #                 original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #                 st.markdown(original_title, unsafe_allow_html=True)
    #                 st.write("")
    #                 warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
    #                 st.markdown(warning, unsafe_allow_html=True)
                    
    #                 #st.line_chart(df_cump)
                
    #             #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
    #             #st.table(tmp_df)
    #             # 성공문구 + 풍선이 날리는 특수효과 
    #             st.sidebar.success("Filter Applied!")
    #             iframe_html = """
    #             <div style='display: flex;'>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%;'>
    #                     <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #             </div>
    #             """
                
    #             st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
                
    #             original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
    #             #st.toast('portfolio 수익률을 확인해보세요', icon='😍')
    #             #st.balloons()
    #     elif radio_select == "전략미사용":
    #         # 2. multi select
    #         # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    #         # return : list
    #         select_multi_species = st.sidebar.multiselect(
    #             '주식 종목을 선택하세요 (복수선택가능)',
    #             stock_name
    #             #['setosa','versicolor','virginica']
            
    #         )
            
    #         code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
            
    #         # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #         #tmp_df = df[df['species'].isin(select_multi_species)]
    #         # 선택한 종들의 결과표를 나타냅니다.  
    #         #
            
    #         ############################################################################################################################################
    #         # 3. Slider
    #         # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    #         start_button = st.sidebar.button(
    #             "START 📊 "#"버튼에 표시될 내용"
    #         )
    #         # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    #         # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    #         if start_button:
    #             #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
    #             if len(select_multi_species) != 0:
    #                 df_cump = pd.DataFrame()
    #                 df_cor = pd.DataFrame()
    #                 for code in code_list:
    #                     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
    #                     df_tmp["등락률"]=df_tmp["등락률"]/100
    #                     df_tmp = df_tmp.reset_index()
    #                     df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                        
    #                     if df_cump.shape[0] == 0:
    #                         df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                         #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
    #                         #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                     else:
    #                         df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
    #                         #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
    #                         #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
                    
    #                 df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
    #                 df_cump = df_cump.set_index("날짜").mean(1)
    #                 #df_cump = (df_cump+1).cumprod()-1
                    
                    
                    
    #                 #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
    #                 #st.write(fig)
                    
    #                 # 퀀트스탯 메트릭 생성
                    
    #                 # Streamlit 애플리케이션 생성
    #                 #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
    #                 st.write("")
    #                 st.write("당신의 포트폴리오는")
    #                 st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
    #                 st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
    #                 st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
    #                 st.write("")
    #                 if len(code_list) >= 2:
                        
                        
    #                     # 데이터프레임 변환 및 시각화
    #                     df_cor = df_cor.iloc[:,1:]
    #                     new_column_names = [stock.get_market_ticker_name(col) for col in df_cor.columns]
    #                     df_cor.columns = new_column_names
    #                     cor = df_cor.corr()
                        
    #                     # 색상 및 투명도 설정
    #                     def color_score(val):
    #                         if val >= 0.5:
    #                             color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
    #                         else:
    #                             color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
    #                         return color
    #                     st.write("")
    #                     st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
    #                     st.table(cor.style.applymap(color_score))
                        
    #                 st.write("")
    #                 # 퀀트스탯 메트릭 정보 출력
    #                 st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
    #                 st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                    
    #                 st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
    #                 st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                    
    #                 st.write("연도별 수익률을 확인해보세요")
    #                 st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
    #                 st.write(qs.plots.yearly_returns(df_cump, show=False))
                    
    #                 st.write("월 수익률 히스토그램을 확인해보세요")
    #                 st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
    #                 st.write(qs.plots.histogram(df_cump, show=False))
    #                 st.write("")
                    
    #                 iframe_html1 = """
    #                 <div style='display: flex;'>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                 </div>
    #                 """
                    
    #                 st.markdown(iframe_html1, unsafe_allow_html=True)
    #                 st.write("")
    #                 original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #                 st.markdown(original_title, unsafe_allow_html=True)
    #                 st.write("")
    #                 warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
    #                 st.markdown(warning, unsafe_allow_html=True)
                    
    #                 #st.line_chart(df_cump)
                
    #             #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
    #             #st.table(tmp_df)
    #             # 성공문구 + 풍선이 날리는 특수효과 
    #             st.sidebar.success("Filter Applied!")
                
    #             iframe_html = """
    #             <div style='display: flex;'>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%;'>
    #                     <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #             </div>
    #             """
                
    #             st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
                
    #             original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
    #             #st.toast('portfolio 수익률을 확인해보세요')# , icon='😍'
    #             #st.balloons()
    #     else:
    #         df = stock.get_market_fundamental_by_ticker(date='20230822', market="ALL")
    #         df = df.sort_values("DIV", ascending=False).head(20)
    #         df.index = [stock.get_market_ticker_name(s) for s in df.index]
    #         df=df.rename(columns={"DIV":"배당수익률","DPS":"주당배당금"})
            
    #         dps = '<p style="font-family:Courier; color:Blue; font-size: 20px;">배당수익률 상위 10개 종목 매수 전략</p>'
    #         st.markdown(dps, unsafe_allow_html=True)
            
    #         html_blog='한국 배당주 투자 참고 게시물 [link](https://blog.naver.com/koreanfinancetime/223119607639)'
    #         st.markdown(html_blog,unsafe_allow_html=True)
            
    #         # Score 컬럼 값에 따라 색상 지정
    #         def color_score(val):
    #             color = 'background-color: green' if val >= 10 else 'background-color: red'
    #             return color
            
    #         df = df.style.applymap(color_score, subset=pd.IndexSlice[:, ['배당수익률']])
            
    #         st.table(df)
    #         st.write("")
    #         st.write("")
            
    #         iframe_html = """
    #         <div style='display: flex;'>
    #             <div style='flex: 33.33%; padding-right: 10px;'>
    #                 <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #             </div>
    #             <div style='flex: 33.33%; padding-right: 10px;'>
    #                 <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #             </div>
    #             <div style='flex: 33.33%;'>
    #                 <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #             </div>
    #             <div style='flex: 33.33%;'>
    #                 <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #             </div>
    #         </div>
    #         """
            
    #         st.markdown(iframe_html, unsafe_allow_html=True)
            
    #         original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #         st.markdown(original_title, unsafe_allow_html=True)
            
    #         warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
    #         st.markdown(warning, unsafe_allow_html=True)
            
    # else:
    #     tickers = stock.get_etf_ticker_list(str(today).replace("-",""))
    #     stock_name = []
        
    #     for ticker in tickers:
    #         stock_name.append(stock.get_etf_ticker_name(ticker))
            
    #     df = pd.DataFrame({"stock_code":tickers,"stock_name":stock_name})
            
    #     #st.table(df)
        
    #     ############################################################################################################################################
    #     # 1. Select Box # 1개 선택
    #     # select_species 변수에 사용자가 선택한 값이 지정됩니다
    #     #select_stock = st.sidebar.selectbox(
    #     #    '종목을 선택하세요',
    #     #    stock_name
    #     #    #['setosa','versicolor','virginica']
    #     #)
        
    #     #df = stock.get_market_ohlcv("19900101", str(today).replace("-",""), select_stock)
    #     # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
        
    #     # 선택한 종의 맨 처음 5행을 보여줍니다 
    #     #st.table(df)
        
    #     # 3. Radio / Slider
    #     # 라디오에 선택한 내용을 radio select변수에 담습니다
    #     radio_select =st.sidebar.radio(
    #         "원하는 ETF 전략을 선택하세요",
    #         ["전략미사용",'이동평균선_전략',"고배당_전략"]
    #         )
    #         #horizontal=True)
    #     #radio_select = "절대모멘텀"
    #     ############################################################################################################################################
        
    #     if radio_select == "이동평균선_전략":
    #         if date_difference < datetime.timedelta(days=40):
    #             original_title = '<p style="font-family:Courier; color:Red; font-size: 30px;">날짜 기간이 너무 짧습니다</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
    #         # 2. multi select
    #         # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    #         # return : list
    #         select_multi_species = st.sidebar.multiselect(
    #             '종목을 선택하세요 (복수선택가능)',
    #             stock_name
    #             #['setosa','versicolor','virginica']
            
    #         )
            
    #         code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
            
    #         # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #         #tmp_df = df[df['species'].isin(select_multi_species)]
    #         # 선택한 종들의 결과표를 나타냅니다.  
    #         #
            
    #         ############################################################################################################################################
    #         # 3. Slider
    #         # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    #         radio_ma =st.sidebar.radio(
    #             "(ETF) 선택한 이동평균선보다 종가가 높으면 매수, 낮으면 매도 하는 전략",
    #             [1,2,3])
            
    #         if radio_ma == 1:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #         elif radio_ma==2:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range2 = st.sidebar.slider(
    #                 "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #         else:
    #             slider_range1 = st.sidebar.slider(
    #                 "전략1 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range2 = st.sidebar.slider(
    #                 "전략2 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
    #             slider_range3 = st.sidebar.slider(
    #                 "전략3 : 해당 이평선 위에 있을 때 매수, 아래에 있을 때 매도",
    #                  1, #시작 값 
    #                  200, #끝 값  
    #                  value=60
    #                 #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #             )
            
    #         # 필터 적용버튼 생성 
    #         start_button = st.sidebar.button(
    #             "START 📊 "#"버튼에 표시될 내용"
    #         )
            
    #         # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    #         # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    #         if start_button:
    #             #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
    #             if len(select_multi_species) != 0:
    #                 df_cump = pd.DataFrame()
    #                 df_cor = pd.DataFrame()
    #                 for code in code_list:
    #                     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
    #                     df_tmp["등락률"] = df_tmp["종가"].pct_change().dropna()
    #                     #df_tmp["등락률"]=df_tmp["등락률"]/100
    #                     df_tmp = df_tmp.reset_index()
    #                     df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                        
    #                     if df_cump.shape[0] == 0:
    #                         df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                         df_tmp["ma1"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
    #                         if radio_ma > 1:
    #                             df_tmp["ma2"] = df_tmp["종가"].shift(1).rolling(slider_range2).mean()
    #                             if radio_ma > 2:
    #                                 df_tmp["ma3"] = df_tmp["종가"].shift(1).rolling(slider_range3).mean()
                                    
    #                         df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma1"],1,0)
    #                         if radio_ma > 1:
    #                             df_tmp["flag2"] = np.where(df_tmp["종가"] > df_tmp["ma2"],1,0)
    #                             df_tmp["flag"] *= df_tmp["flag2"]
    #                             if radio_ma > 2:
    #                                 df_tmp["flag3"] = np.where(df_tmp["종가"] > df_tmp["ma3"],1,0)
    #                                 df_tmp["flag"] *= df_tmp["flag3"]
                                    
    #                         df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                     else:
    #                         df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
    #                         df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range1).mean()
    #                         df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
                    
    #                 df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
    #                 df_cump = df_cump.set_index("날짜").mean(1)
    #                 #df_cump = (df_cump+1).cumprod()-1
                    
                    
                    
    #                 #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
    #                 #st.write(fig)
                    
    #                 # 퀀트스탯 메트릭 생성
                    
    #                 # Streamlit 애플리케이션 생성
    #                 #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
    #                 st.write("")
    #                 st.write("당신의 포트폴리오는")
    #                 st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
    #                 st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
    #                 st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
    #                 st.write("")
    #                 if len(code_list) >= 2:
                        
                        
    #                     # 데이터프레임 변환 및 시각화
    #                     df_cor = df_cor.iloc[:,1:]
    #                     new_column_names = [stock.get_etf_ticker_name(col) for col in df_cor.columns]
    #                     df_cor.columns = new_column_names
    #                     cor = df_cor.corr()
                        
    #                     # 색상 및 투명도 설정
    #                     def color_score(val):
    #                         if val >= 0.5:
    #                             color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
    #                         else:
    #                             color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
    #                         return color
    #                     st.write("")
    #                     st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
    #                     st.table(cor.style.applymap(color_score))
                        
    #                 st.write("")
    #                 # 퀀트스탯 메트릭 정보 출력
    #                 st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
    #                 st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                    
    #                 st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
    #                 st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                    
    #                 st.write("연도별 수익률을 확인해보세요")
    #                 st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
    #                 st.write(qs.plots.yearly_returns(df_cump, show=False))
                    
    #                 st.write("월 수익률 히스토그램을 확인해보세요")
    #                 st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
    #                 st.write(qs.plots.histogram(df_cump, show=False))
    #                 st.write("")
                    
    #                 iframe_html1 = """
    #                 <div style='display: flex;'>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                 </div>
    #                 """
                    
    #                 st.markdown(iframe_html1, unsafe_allow_html=True)
    #                 st.write("")
    #                 original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #                 st.markdown(original_title, unsafe_allow_html=True)
    #                 st.write("")
    #                 warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
    #                 st.markdown(warning, unsafe_allow_html=True)
                    
    #                 #st.line_chart(df_cump)
                
    #             #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
    #             #st.table(tmp_df)
    #             # 성공문구 + 풍선이 날리는 특수효과 
    #             st.sidebar.success("Filter Applied!")
    #             iframe_html = """
    #             <div style='display: flex;'>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%;'>
    #                     <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #             </div>
    #             """
                
    #             st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
                
    #             original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
                
                
    #             #st.toast('portfolio 수익률을 확인해보세요', icon='😍')
    #             #st.balloons()
    #     elif radio_select == "전략미사용":
    #         # 2. multi select
    #         # 여러개 선택할 수 있을 때는 multiselect를 이용하실 수 있습니다 
    #         # return : list
    #         select_multi_species = st.sidebar.multiselect(
    #             '종목을 선택하세요. (복수선택가능)',
    #             stock_name
    #             #['setosa','versicolor','virginica']
            
    #         )
            
    #         slider_range_prop = list()
    #         prop_sum = 100
    #         for s in select_multi_species:
    #              slider_range_prop.append(st.sidebar.slider(
    #                     s+" 종목의 포트폴리오 비중을 선택하세요",
    #                      1, #시작 값 
    #                      min(98,prop_sum-sum(slider_range_prop)), #끝 값  
    #                      value=1
    #                     #(2.5, 7.5) # 기본값, 앞 뒤로 2개 설정 /  하나만 하는 경우 value=2.5 이런 식으로 설정가능
    #                 ))
                
    #         st.sidebar.write("포트폴리오 비중 합 : "+str(sum(slider_range_prop))+"%")
    #         st.sidebar.write("포트폴리오 비중 합이 100%가 되어야 Button이 활성화됩니다")
            
    #         slider_range_prop = list(np.array(slider_range_prop)/100)
    #         code_list = df[df["stock_name"].isin(select_multi_species)]["stock_code"]
            
    #         # 원래 dataframe으로 부터 꽃의 종류가 선택한 종류들만 필터링 되어서 나오게 일시적인 dataframe을 생성합니다
    #         #tmp_df = df[df['species'].isin(select_multi_species)]
    #         # 선택한 종들의 결과표를 나타냅니다.  
    #         #
            
    #         ############################################################################################################################################
    #         # 3. Slider
    #         # 선택한 컬럼의 값의 범위를 지정할 수 있는 slider를 만듭니다. 
    #         start_button = False
    #         # 필터 적용버튼 생성 
    #         if sum(slider_range_prop) == 1:
    #             start_button = st.sidebar.button(
    #                 "START 📊 "#"버튼에 표시될 내용"
    #             )
            
    #         # button이 눌리는 경우 start_button의 값이 true로 바뀌게 된다.
    #         # 이를 이용해서 if문으로 버튼이 눌렸을 때를 구현 
    #         if start_button:
    #             #slider input으로 받은 값에 해당하는 값을 기준으로 데이터를 필터링합니다.
    #             if len(select_multi_species) != 0:
    #                 df_cump = pd.DataFrame()
    #                 df_cor = pd.DataFrame()
    #                 prop_cnt = 0
    #                 for code in code_list:
    #                     df_tmp = stock.get_market_ohlcv(str(past).replace("-",""),str(today).replace("-",""), code).dropna()
    #                     df_tmp["등락률"] = df_tmp["종가"].pct_change().dropna()
    #                     #df_tmp["등락률"]=df_tmp["등락률"]/100
    #                     df_tmp = df_tmp.reset_index()
    #                     df_tmp["날짜"] = df_tmp["날짜"].apply(lambda x:str(x)[:10])
                        
    #                     if df_cump.shape[0] == 0:
    #                         df_tmp["등락률"] = df_tmp["등락률"]*slider_range_prop[prop_cnt]
    #                         df_cor = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                         #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
    #                         #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = df_tmp[["날짜","등락률"]].rename(columns={"등락률":code})
    #                     else:
    #                         df_tmp["등락률"] = df_tmp["등락률"]*slider_range_prop[prop_cnt]
    #                         df_cor = pd.merge(df_cor,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
    #                         #df_tmp["ma"] = df_tmp["종가"].shift(1).rolling(slider_range).mean()
    #                         #df_tmp["flag"] = np.where(df_tmp["종가"] > df_tmp["ma"],1,0)
    #                         #df_tmp["flag_shift"] = df_tmp["flag"].shift(1)
    #                         df_tmp = df_tmp.dropna()
    #                         #df_tmp["등락률"] = df_tmp["등락률"]*df_tmp["flag_shift"]
    #                         df_cump = pd.merge(df_cump,df_tmp[["날짜","등락률"]].rename(columns={"등락률":code}),on="날짜",how="left").dropna()
    #                     prop_cnt += 1
                        
    #                 df_cump['날짜'] = pd.to_datetime(df_cump['날짜'])
    #                 df_cump = df_cump.set_index("날짜").sum(1)
    #                 #df_cump = (df_cump+1).cumprod()-1
                    
                    
                    
    #                 #fig = qs.plots.snapshot(stock, title='AAPL Performance', show=False)
    #                 #st.write(fig)
                    
    #                 # 퀀트스탯 메트릭 생성
                    
    #                 # Streamlit 애플리케이션 생성
    #                 #st.title("DIY Strategy Evaluation")  # 웹 페이지 제목
    #                 st.write("")
    #                 st.write("당신의 포트폴리오는")
    #                 st.write("연율화 수익률 " + str(round(qs.stats.cagr(df_cump)*100,2))+'% 로')
    #                 st.write("10년 기준 " + str(round(((qs.stats.cagr(df_cump)+1)**10-1)*100,2))+'% 수익률 예상됩니다')
    #                 st.write("최대 낙폭률은 " + str(round(qs.stats.max_drawdown(df_cump)*100,2))+"% 입니다")
    #                 st.write("")
    #                 if len(code_list) >= 2:
                        
    #                     # 데이터프레임 변환 및 시각화
    #                     df_cor = df_cor.iloc[:,1:]
    #                     new_column_names = [stock.get_etf_ticker_name(col) for col in df_cor.columns]
    #                     df_cor.columns = new_column_names
    #                     cor = df_cor.corr()
                        
    #                     # 색상 및 투명도 설정
    #                     def color_score(val):
    #                         if val >= 0.5:
    #                             color = 'background-color: rgba(0, 0, 255, 0.5)'  # 파란색, 투명도 0.5
    #                         else:
    #                             color = 'background-color: rgba(255, 0, 0, 0.5)'  # 빨간색, 투명도 0.5
    #                         return color
    #                     st.write("")
    #                     st.write("음의 선형 상관관계를 보일수록 보완이 되는 관계가 될 가능성이 높습니다")
    #                     st.table(cor.style.applymap(color_score))
                        
    #                 st.write("")
    #                 # 퀀트스탯 메트릭 정보 출력
    #                 st.write("누적 수익률과 Maximum DrawDown을 확인해보세요")
    #                 st.write(qs.plots.snapshot(df_cump, title='Portfolio Return', show=False))
                    
    #                 st.write("월별 수익률을 확인해보세요(계절/월별 특성 확인)")
    #                 st.write(qs.plots.monthly_heatmap(df_cump, show=False))
                    
    #                 st.write("연도별 수익률을 확인해보세요")
    #                 st.write("(연도별로 비슷할 수록 강건한 포트폴리오가 됩니다)")
    #                 st.write(qs.plots.yearly_returns(df_cump, show=False))
                    
    #                 st.write("월 수익률 히스토그램을 확인해보세요")
    #                 st.write("(평균이 0보다 크고 분포가 양수에 치우칠 수록 좋습니다)")
    #                 st.write(qs.plots.histogram(df_cump, show=False))
    #                 st.write("")
                    
    #                 iframe_html1 = """
    #                 <div style='display: flex;'>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8An7" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%; padding-right: 10px;'>
    #                         <iframe src="https://coupa.ng/cd8Ap8" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8AqO" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                     <div style='flex: 33.33%;'>
    #                         <iframe src="https://coupa.ng/cd8Art" width="120" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                     </div>
    #                 </div>
    #                 """
                    
    #                 st.markdown(iframe_html1, unsafe_allow_html=True)
    #                 st.write("")
    #                 original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #                 st.markdown(original_title, unsafe_allow_html=True)
    #                 st.write("")
    #                 warning = '<p style="font-family:Courier; color:Gray; font-size: 12px;">위 정보는 투자에 대한 이해를 돕기 위해 제공하는 것으로 투자 권유를 목적으로 하지 않습니다. 제공되는 정보는 오류 또는 지연이 발생할 수 있으며 제작자는 제공된 정보에 의한 투자 결과에 대해 법적인 책임을 지지 않습니다.</p>'
    #                 st.markdown(warning, unsafe_allow_html=True)
                    
    #                 #st.line_chart(df_cump)
                
    #             #tmp_df= tmp_df[ (tmp_df[radio_select] >= slider_range[0]) & (tmp_df[radio_select] <= slider_range[1])]
    #             #st.table(tmp_df)
    #             # 성공문구 + 풍선이 날리는 특수효과 
    #             st.sidebar.success("Filter Applied!")
    #             iframe_html = """
    #             <div style='display: flex;'>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kRY" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%; padding-right: 10px;'>
    #                     <iframe src="https://coupa.ng/cd8kY9" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #                 <div style='flex: 33.33%;'>
    #                     <iframe src="https://coupa.ng/cd8k1U" width="90" height="240" frameborder="0" scrolling="no" referrerpolicy="unsafe-url"></iframe>
    #                 </div>
    #             </div>
    #             """
                
    #             st.sidebar.markdown(iframe_html, unsafe_allow_html=True)
                
    #             original_title = '<p style="font-family:Courier; color:Orange; font-size: 12px;">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>'
    #             st.sidebar.markdown(original_title, unsafe_allow_html=True)
                
    #             #st.toast('portfolio 수익률을 확인해보세요')# , icon='😍'
    #             #st.balloons()
    #     else:
    #         div_df = stock.get_index_fundamental(date='20230822')
    #         div_df = div_df.sort_values("배당수익률", ascending=False).head(20)

            
    #         etf_dps = '<p style="font-family:Courier; color:Blue; font-size: 20px;">배당수익률 상위 종목 매수 전략</p>'
    #         st.markdown(etf_dps, unsafe_allow_html=True)
            
    #         html_blog='한국 배당주 투자 참고 게시물 [link](https://blog.naver.com/koreanfinancetime/223119607639)'
    #         st.markdown(html_blog,unsafe_allow_html=True)
            
    #         # Score 컬럼 값에 따라 색상 지정
    #         def color_score(val):
    #             color = 'background-color: green' if val >= 3 else 'background-color: red'
    #             return color
            
    #         div_df = div_df.style.applymap(color_score, subset=pd.IndexSlice[:, ['배당수익률']])

            
    #         # Styler 객체를 HTML로 변환하여 출력
    #         st.write(div_df.to_html(escape=False), unsafe_allow_html=True)
            
    #         #st.table(div_df)
    #         st.write("")
    #         st.write("")
            
            
    # ############################################################################################################################################
