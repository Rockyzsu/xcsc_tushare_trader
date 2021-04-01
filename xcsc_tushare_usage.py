import xcsc_tushare as xc 
from config import xc_token,simulation_server
import datetime
from sqlalchemy import create_engine

xc.set_token(xc_token)
pro =xc.pro_api(env='prd',server=simulation_server)

# 获取可转债所有代码
class Bond:
    def __init__(self):
        self.engine = self.get_enine()

    @property
    def bond_code_list(self):
        '''
        当天所有转债代码
        '''
        df_today = pro.cb_daily(trade_date=self.today)
        return df_today['ts_code'].value_counts().index.tolist()


    @property
    def today(self):
        return datetime.datetime.now().strftime('%Y%m%d')

    # 所有交易日
    def trading_cal(self,start_date='20180101',end_date=None):
        if end_date is None:
            end_date=self.today
        trading_date = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)
        return trading_date['trade_date'].tolist()

    def insert_daily_info(self,day):
        df=pro.cb_daily(trade_date=day)
        try:
            df.to_sql('xcsc_bond_daily', con=self.engine,if_exists='append',index=False)
        except Exception as e:
            print(e)
    
    def get_enine(self):
        from config import user, password, host, port
        try:
            engine = create_engine(
                'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, 'db_stock'))
        except Exception as e:
            print(e)
            return None
        return engine


    def export(self):
        all_day =self.trading_cal()
        for day in all_day:
            print(day)
            self.insert_daily_info(day)
    def apply_new_bond(self):
        df = pro.cb_issue(start_date='20180101',end_date='20210101')
        # print(len(df))
        # print(df.head())
        # print(df.tail())
        # people_count = df[['onl_winning_rate','onl_name']]
        print(df.info())
        # print(people_count)

    def bond_minte_ticket(self):
        # df = pro.stk_mins(ts_code='128033.SZ',trade_time='2020-11-17',freq='1min')
        # print(df.head())
        import tushare as ts

        df = ts.get_h_data('128033.SZ', start='2020-01-01', end='2020-03-16')
        print(df.head(10))

def bond_change():
    df = pro.bond_amount(ts_code='128050.SZ')
    print(df.head(20))


def main():
    bond = Bond()
    # bond.export()
    # bond.apply_new_bond()
    bond.bond_minte_ticket()

if __name__=='__main__':
    main()