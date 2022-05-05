import ccxt
import settings
import time
from pprint import pprint

client = ccxt.bitget()

# API key, secret and password
client.apiKey = settings.API_KEY
client.secret = settings.SECRET_KEY
client.password = settings.PASSWORD

SYMBOL = 'BTCUSDT'  # 코인지정
CANDLE_INTERVAL3 = '3m'
CANDLE_INTERVAL60 = '60m'

RSI_SIZE = 14  # ㅡㅡㅡ 14일 기준
NUM_CANDLE = 150  # ㅡㅡㅡ 150개 캔들 기준

LVG = 20  # 레버리지 배수
BUY_RSI_L = 25  # 롱 매수 기준
BUY_RSI_S = 75  # 숏 매수 기준
SELL_RSI_L = 70  # 롱 매도 기준
SELL_RSI_S = 30  # 숏 매도 기준

SLOSS_L = 0.997  # 롱 스탑로스 기준 0.3%
SLOSS_S = 0.997  # 숏 스탑로스 기준 0.3%

UNIT_AMOUNT = '1'
has_position = False

def get_prices(client, symbol, timeframe, length):
    res = client.fetchOHLCV(symbol, timeframe=timeframe, limit=length)
    prices = []
    for i in range(len(res)):
        prices.append(res[i][4])

    return prices

def RSI(prices, length):
    base_price = None
    positive = []
    negative = []
    rsi = []
    up = 0
    down = 0
    alpha = 1 / length

    positive.append(0)
    negative.append(0)
    rsi.append(0)
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff < 0:
            u = 0
            d = abs(diff)
        else:
            u = diff
            d = 0
        
        up = (1.0 - alpha) * positive[i - 1] + alpha * u
        positive.append(up)
        down = (1.0 - alpha) * negative[i - 1] + alpha * d
        negative.append(down)
        r = 0
        if down != 0:
            r = 100 - (100 / (1 + up / down))
        rsi.append(r)
    
    print("RSI: ", rsi[-1])

    return rsi[-1]


while True:
    try:
        prices3 = get_prices(client, SYMBOL, CANDLE_INTERVAL3, NUM_CANDLE)
        rsi3 = RSI(prices3, RSI_SIZE)

        prices60 = get_prices(client, SYMBOL, CANDLE_INTERVAL60, NUM_CANDLE)
        rsi60 = RSI(prices60, RSI_SIZE)

        # RSI가 기준보다 낮고 포지션 없을 때 구입
        if rsi60 < rsi3 < BUY_RSI_L and not has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                longLeverage=LVG,
                marginMode='crossed',
                type='market',
                side='open_long',
                amount=UNIT_AMOUNT,
                params={
                    'type': '1',
                }
            )
            has_position = True
            pprint(res)

        # RSI가 기준보다 높고 포지션 없을 때 구입
        if rsi60 < rsi3 < BUY_RSI_S and not has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                shortLeverage=LVG,
                marginMode='crossed',
                type='market',
                side='open_short',
                amount=UNIT_AMOUNT,
                params={
                    'type': '1',
                }
            )
            has_position = True
            pprint(res)
        
        # RSI가 기준보다 높고 포지션이 있을 때 판매
        if rsi60 > SELL_RSI_L and has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                type='market',
                side='close_long',
                amount=UNIT_AMOUNT,
                params={
                    'type': '3',
                }
            )
            has_position = False
            pprint(res)

        # RSI가 기준보다 낮고 포지션이 있을 때 판매
        if rsi60 > SELL_RSI_S and has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                type='market',
                side='close_short',
                amount=UNIT_AMOUNT,
                params={
                    'type': '3',
                }
            )
            has_position = False
            pprint(res)

        # LONG 손절조건 매수평균보다 낮고 포지션이 있을 때 판매
        if ((price / priceAvg) < SLOSS_L) and has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                type='market',
                side='close_long',
                amount=UNIT_AMOUNT,
                params={
                    'type': '3',
                }
            )
            has_position = False
            pprint(res)

        # SHORT 손절조건 매수평균보다 낮고 포지션이 있을 때 판매
        if ((price / priceAvg) < SLOSS_S) and has_position:
            res = client.createOrder(
                symbol=SYMBOL,
                marginCoin='USDT',
                type='market',
                side='close_short',
                amount=UNIT_AMOUNT,
                params={
                    'type': '3',
                }
            )
            has_position = False
            pprint(res)
        
    except Exception as e:
        print(e)

    time.sleep(10)






