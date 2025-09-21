from urllib.parse import urlparse
import pandas as pd

df = pd.read_csv("xgd/result_4.csv")

# データの総数
print('総数:\n', df.shape)

# index
print('Index:\n', df.index)

# column
print('Column:\n', df.columns)

# データ型
print('各列のデータ型:\n', df.dtypes)

# 使用率
df_used = df[df["is_used"] == True]
print(f'使用率: {len(df.shape)/len(df_used)*100}%')

# # ---使われているものだけをCSVに保存
# df_used.to_csv('xgd/is_used.csv', index=True, encoding='utf-8-sig')
# print(f'{len(df_used)}件保存しました。')

# # ---x.gd/unsafeを除いて保存する
# df_remove_xgd = df[df["url"].apply(lambda x: urlparse(str(x)).netloc) != "x.gd"]
# df_remove_xgd.to_csv('xgd/remove_xgd.csv', index=True, encoding='utf-8-sig')
# print(f'{len(df_remove_xgd)}件保存しました。')
