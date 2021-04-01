import xcsc_tushare as xc 
from config import xc_token,simulation_server
xc.set_token(xc_token)
pro =xc.pro_api(env='prd',server=simulation_server)
__all__=('pro',)
