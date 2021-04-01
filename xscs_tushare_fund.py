from Base import pro
df=pro.fund_manager(offset=1,limit=2000)
# print(df['edu'].value_counts())
print(df[df['edu']=='博士'])