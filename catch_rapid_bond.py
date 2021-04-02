
import xcsc_tushare as xc
from queue import Queue
import datetime
import numpy as np
import re

# ==============================================================================
# 定义变量

# version 2
'''
1 X分钟内涨幅≥A  【起始涨幅＞A1 则买入后X1分钟卖出 ||||  起始涨幅＜A1 则买入后X2分钟卖出]，

2 Y分钟内 B≤涨幅＜A，[ 起始跌幅＞B1，则买入后X3分钟卖出,|||| 起始跌幅＜B1，则买入后X4分钟卖出]

3 Z分钟内跌幅≥C ,[ 起始涨幅＞C1 则买入后X5分钟卖出，||||  起始涨幅＜C1 则买入后X6分钟卖出]，

4 W分钟内 D≤跌幅＜C，[ 起始跌幅＞D1，则买入后X7分钟卖出 ||||| 跌幅＜D2，则买入后X78分钟卖出]


变量 X Y Z W 分钟
时间区间涨幅 A，B，C，D
其实涨幅与时间 A1，X1,X2
B1 X3,X4
C1 X5,X6
D1 X7 X8
'''


'''
x1分钟内涨幅大于x11 且 起始涨幅大于sp1 则买入后m1分钟卖出，如果起始涨幅小于sp2，则买入后m2分钟卖出

y1分钟内跌幅大于y11 且 起始跌幅大于sp3 则买入后n1分钟卖出，如果起始涨幅小于sp4，则买入n2X分钟卖出
'''


'''
不同的字母代表不同的值，当然可以设置为一样的
T1分钟内涨幅≥A1 且 起始涨幅＞B1 则买入后S1分钟卖出，
T2分钟内涨幅≥A2 且 起始涨幅＜B2 则买入后S2分钟卖出，
T3分钟内跌幅≥A3 且 起始涨幅＞B3 则买入后S3分钟卖出，
T4分钟内跌幅≥A4 且 起始涨幅＜B4 则买入后S4分钟卖出，

T5分钟内 C5≤涨幅＜A5，且 起始涨幅＞D5，则买入后S5分钟卖出
T6分钟内 C6≤涨幅＜A6，且 起始涨幅＜D6，则买入后S6分钟卖出
T7分钟内 C7≤跌幅＜A7，且 起始涨幅＞D7，则买入后S7分钟卖出
T8分钟内 C8≤跌幅＜A8，且 起始涨幅＜D8，则买入后S8分钟卖出
'''


class BaseStrategy():
    def __init__(self,
                 strategy_number=None,
                 monitor_time=None,
                 monitor_raise_min=None,
                 monitor_raise_max=None,
                 start_raise=None,
                 sell_time=None,
                 ):
                     
        self.monitor_time = monitor_time
        self.monitor_raise_min = monitor_raise_min
        self.monitor_raise_max = monitor_raise_max
        self.start_raise = start_raise
        self.sell_time = sell_time
        self.strategy_number = strategy_number

    def valid(self):
        return True if self.monitor_time else False

    def match_time(self, current):
        return True if current >= self.monitor_time else False

    def get_sell_time(self):
        return self.sell_time

    def start_raise_condition(self, v_value):
        if self.strategy_number % 2 == 0:
            return True if v_value < self.start_raise else False
        else:
            return True if v_value > self.start_raise else False

    def meet(self, current, interval_raise_val, start_raise_val):
        if self.valid() and self.match_time(current) and self.interval_raise(interval_raise_val) and self.start_raise_condition(start_raise_val):
            return True
        else:
            return None


class StrategyCondition1(BaseStrategy):

    def interval_raise(self, v_value):
        if self.strategy_number <3: # 策略1，2
            return True if v_value >= self.self.monitor_raise_max else False
        else: # 策略3，4
            return True if v_value <= self.self.monitor_raise_max else False

class StrategyCondition2(BaseStrategy):

    def interval_raise(self, v_value):
        if self.strategy_number <7: # 策略5，6
            return True if self.monitor_raise_min <= v_value < self.self.monitor_raise_max else False
        else: # 策略 7,8
            return True if self.monitor_raise_min > v_value >= self.self.monitor_raise_max else False
            

#变量定义
T1,A1,B1,S1=10,2,1,4
T2,A2,B2,S2=10,3,0,4
T3,A3,B3,S3=10,-2,1,4
T4,A4,B4,S4=10,-3,0,4

T5,C5,A5,B5,S5=10,2,4,2,4
T6,C6,A6,B6,S6=10,3,5,1,4
T7,C7,A7,B7,S7=10,-2,-5,2,4
T8,C8,A8,B8,S8=10,-1,-3,1,4

strategy1=StrategyCondition1(1,T1,None,A1,B1,S1)
strategy2=StrategyCondition1(2,T2,None,A2,B2,S2)
strategy3=StrategyCondition1(3,T3,None,A3,B3,S3)
strategy4=StrategyCondition1(4,T4,None,A4,B4,S4)

strategy5=StrategyCondition2(5,T5,C5,A5,B5,S5)
strategy6=StrategyCondition2(6,T6,C6,A6,B6,S6)
strategy7=StrategyCondition2(7,T7,C7,A7,B7,S7)
strategy8=StrategyCondition2(8,T8,C8,A8,B8,S8)

strategy_list =[
    strategy1,
    strategy2,
    strategy3,
    strategy4,
    strategy5,
    strategy6,
    strategy7,
    strategy8,

]

LIMIT_PRICE_PERCENT = 1.2  # 当前成交价的20% 限制

USE_UP = True
USE_DOWN = True

AFTER_HALT_SELL_TIME = 5  # 复牌后5分钟卖
# 强赎列表，当天强赎的转债代码，如果有多个请用逗号隔开 例子：['123004.SZ','123004.SZ']
forced_redemption_list = ['123000.SH', ]
DEBUG = True
# =================================================================================


xc.set_token(xc_token)
pro = xc.pro_api(env='prd', server=simulation_server)

def get_max_time():
    result_list=[]
    for i in strategy_list:
        result_list.append(i.monitor_time)
    v=max(result_list)
    print(v)
    return v
    
class Bond:

    def modify_sh_code(self, x):
        return re.sub('SH', 'SS', x)

    @property
    def bond_code_list(self):
        '''
        当天所有转债代码
        '''
        df_today = pro.cb_daily(trade_date=self.yesterday)
        current_bond_list = df_today['ts_code'].value_counts().index.tolist()
        current_bond_list = list(map(self.modify_sh_code, current_bond_list))
        try:
            for code in forced_redemption_list:
                code = code.upper()
                if code in current_bond_list:
                    current_bond_list.remove(code)

        except Exception as e:
            log.info(e)

        return current_bond_list

    @property
    def yesterday(self):
        return (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y%m%d')


def before_trading_start(context, data):
    if DEBUG:
        log.info('before_trading_start')
    monitor_time = get_max_time()
    g.monitor_time = monitor_time
    log.info('monitor time {}'.format(monitor_time))

    g.count = 0
    g.closed_df_price = {}
    g.holding = 0
    g.ordered_stocks_dict_list = []
    g.start = True
    bond = Bond()
    g.trade_order_list = []  # 委托单
    position_last_close_init(context)

    g.stock_list = bond.bond_code_list  # 标的转债
    g.halt_stock_dict = {}  # 停牌

    # 昨日收盘价 QA：如果昨日停牌了，价格依然存在？
    history = get_history(
        1, '1d', ['close', 'volume'], g.stock_list, fq='pre', include=True)

    history = history.swapaxes("minor_axis", "items")

    for stock in g.stock_list.copy():
        # 昨日停牌的
        closed_df = history[stock]
        if len(closed_df) == 0:
            g.stock_list.remove(stock)
            continue

        g.closed_df_price[stock] = closed_df['close'].iloc[-1]


    log.info('before trading start end')

def after_trading_end(context, data):
    if DEBUG:
        log.info('after_trading_end')

    log.info(g.ordered_stocks_dict_list)


def initialize(context):
    if DEBUG:
        log.info('initialize')

    run_daily(context, sell_on_startup, '9:30')
    run_daily(context, sell_on_startup, '14:56')  # 收盘前

    run_interval(context, execution, seconds=3)  # 扫描


def convert_percent(current_price, last_price):
    '''
    换算百分比
    '''
    return (current_price-last_price)/last_price*1.00 * 100


def trade_pending():
    if len(g.trade_order_list) == 0:
        return

    for order_id in g.trade_order_list.copy():
        order_info = get_order(order_id)
        code = order_info['symbol ']
        if order_info['status'] == 8:
            log.info('订单{order_id} 交易成功 标的 {}'.format(order_id, code))
        else:

            cancel_order(order_id)
            # 移除
            for item in g.ordered_stocks_dict_list.copy():
                if item['code'] == code:
                    g.ordered_stocks_dict_list.remove(item)

        g.trade_order_list.remove(order_id)




def execution(context):
    '''
    his1 = get_history(10, '1m', 'price') # 过去10分钟
    '''

    current = context.blotter.current_dt
    second = current.second

    if second < 5:  # 每分钟只执行有一次
        if DEBUG:
            log.info('{} scaning buy'.format(current))
        minute_count=g.monitor_time
        print(minute_count)
        buy_between_time_df = get_history(minute_count, '1m', ['open', 'close'], g.stock_list, fq='pre', include=True)
        buy_between_time_df = buy_between_time_df.swapaxes("minor_axis", "items")

        buy_list=[]
        for code in g.stock_list:

            if has_buy(code):
                # 没卖出
                continue

            stock_df = buy_between_time_df[code]
            for index,strategy in  enumerate(strategy_list):
                log.info('扫描第{}个策略'.format(index+1))

                monitor_time = strategy.monitor_time

                stock_df_up = stock_df.iloc[-1*monitor_time:]

                # 有可能是NAN
                if np.isnan(stock_df_up['close'].iloc[-1]):
                    continue

                if len(stock_df_up) < monitor_time:
                    # 时间不满足，重新循坏
                    continue

                yesterday_close_price = g.closed_df_price[code]

                if np.isnan(yesterday_close_price):
                    continue

                if np.isnan(stock_df_up['open'].iloc[0]):
                    # 之前为nan 去除
                    new_stock_df = stock_df_up.dropna(axis=0, how='any')
                    open_price = new_stock_df['open'].iloc[0]

                else:
                    open_price = stock_df_up['open'].iloc[0]

                # 起始涨幅
                start_raise = convert_percent(open_price, yesterday_close_price)

                # 区间涨幅
                part_raise = convert_percent(
                    stock_df_up['close'].iloc[-1], yesterday_close_price)



                if strategy.meet(monitor_time,part_raise,start_raise):

                    # 买入
                    # log.info('stock {}满足买入条件： {}分钟内涨幅大于{}, 初始涨幅大于 {}'.format(
                        # code, X_MINUTE_UP, X00_PERCENT_UP, X_START_PERCENT_UP_LARGE))
                    d = {}
                    d['stock'] = code
                    d['selltime'] = strategy.get_sell_time()
                    buy_list.append(d)
                    break # 跳出改策略组


        buy_operation(context, buy_list)  # 批量买卖

    # 卖出监控
    if second > 56:
        if DEBUG:
            log.info('{} scaning selling'.format(current))

        sell_operation(context)


def sell_operation(context):

    for item in g.ordered_stocks_dict_list.copy():
        code = item['code']
        selltime = item['selltime']-1  # 在上一分钟中的56秒进行操作
        current = context.blotter.current_dt

        stock_info_df = get_snapshot(code)
        current_status = stock_info_df[code]['trade_status']

        # 需要到实盘查看实际状态 TODO
        if current_status in ['SUSP', 'HALT']:
            # 停牌状态
            if code not in g.halt_stock_dict:
                # 登记
                g.halt_stock_dict[code] = {
                    'halt_start_time': current, 'status': 'halt'}

        else:
            # 可以交易状态
            if code not in g.halt_stock_dict:
                # 正常交易
                if selltime <= current:
                    # 时间到了，可以卖出
                    order_id = order_target(code, 0)
                    if order_id:
                        sell_marked(code, order_id)
                    else:
                        order_id = order_target(code, 0)
                        if order_id:
                            sell_marked(code, order_id)
                        else:
                            log.error('{}卖出失败，订单ID{}'.format(code, order_id))

            else:
                # 停牌后操作
                halt_start_time = g.halt_stock_dict[code]['halt_start_time']
                stock_current_status = g.halt_stock_dict[code]['status']

                if stock_current_status == 'halt':
                    # 开始复牌
                    g.halt_stock_dict[code].update({'status': 'open'})
                    g.halt_stock_dict[code].update({'open_time': current})

                elif stock_current_status == 'open':
                    open_time = g.halt_stock_dict[code]['open_time']
                    if currnet >= open_time+datetime.timedelta(minutes=AFTER_HALT_SELL_TIME):
                        # 卖出
                        order_id = order_target(code, 0)
                        if order_id:
                            sell_marked(code, order_id)  # TODO
                            del g.halt_stock_dict[code]

                        else:
                            # 卖出失败，重新卖
                            cancel_order(order_id)
                            order_id = order_target(code, 0)
                            if order_id:
                                sell_marked(code, order_id)
                                del g.halt_stock_dict[code]
                            else:
                                log.error(
                                    '{}卖出失败，订单ID{}'.format(code, order_id))


def check_position(context):
    portfolio = context.portfolio


def buy_operation(context, buy_list):

    count = len(buy_list)
    if count == 0:
        return

    portfolio_info = context.portfolio  # 更新频率较慢 bug
    cash = portfolio_info.cash  # 当前现金

    mean_cash = cash/count  # 平均分
    log.info('当前现金{} 均分为{}'.format(cash, mean_cash))
    for item in buy_list:
        code = item['stock']
        after_time = item['selltime']

        df = get_snapshot(code)
        sold_list = df[code]['offer_grp']
        sold_one_price = sold_list[1][0]
        try:
            sold_two_price = sold_list[2][0]
            can_trade = True
        except:
            log.info('{} 停牌无法买入'.format(code))
            can_trade = False  # 停牌

        if can_trade and not has_buy(code):
            limit_price = sold_one_price * LIMIT_PRICE_PERCENT  # 限定在1.2
            log.info('准备买入{}, 金额{} ， 限价{}'.format(
                code, mean_cash, limit_price))

            order_id = order_value(code, mean_cash, limit_price=limit_price)

            sell_time = context.blotter.current_dt + \
                datetime.timedelta(minutes=after_time)

            if order_id:
                buy_marked(code, sell_time, order_id)

            else:

                order_id = order_value(
                    code, mean_cash, limit_price=limit_price)

                if order_id:
                    buy_marked(code, sell_time.order_id)
                else:
                    log.error('{}下单重试报错'.format(code))


def has_buy(code):
    '''
    在已入的列表里，是否卖出
    '''
    temp_list = []
    for item in g.ordered_stocks_dict_list:
        temp_list.append(item['code'])

    return True if code in temp_list else False

# 每分钟执行一次


def handle_data(context, data):
    pass


def buy_marked(code, sell_time, order_id):
    g.ordered_stocks_dict_list.append({'code': code, 'selltime': sell_time})
    g.trade_order_list.append(
        {'code': code, 'order_id': order_id, 'status': 'buy'})
    log.info(('已下单委托买：', code))


def sell_marked(code, order_id):

    for item in g.ordered_stocks_dict_list.copy():
        if code == item['code']:
            g.ordered_stocks_dict_list.remove(item)  # 在已购买list清除

    log.info(('开盘卖出 已下单卖出：', code))
    g.trade_order_list.append(
        {'code': code, 'order_id': order_id, 'status': 'sell'})

    # 在持仓列表里面移除 TODO 判断 id的状态，是否全部卖出
    # g.position_last_list.remove(code) 不使用这个移除


def sell_on_startup(context):
    # 开盘即卖
    # TODO 判断是否停牌
    # 持仓的
    position_last_close_init(context)  # 分钟级别的更新
    for code in g.position_last_list.copy():
        # 直接卖
        # TODO 价格限制
        order_id = order_target(code, 0)
        if order_id:
            # TODO 需要在实盘中确认
            sell_marked(code, order_id)
        else:
            order_id = order_target(code, 0)
            if order_id:
                sell_marked(code)
            else:
                log.error('{}卖出失败'.format(code))


def read_stock_list_from_file():
    '''
    deprecated
    '''
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # today='2021-03-25'
    full_path = home + '{}.txt'.format(today)
    with open(full_path, 'r') as fp:
        content = fp.read()
        code_list = eval(content.strip())
        return code_list


def position_last_close_init(context):
    log.info('获取持仓信息')
    g.position_last_list = [
        position.sid
        for position in context.portfolio.positions.values()
        if position.amount != 0
    ]
