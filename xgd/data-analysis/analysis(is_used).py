import pandas as pd
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import japanize_matplotlib

df = pd.read_csv('xgd/is_used.csv')

# urlカラムからドメインを取得
# .apply(func): 列の各要素にfuncを適用
# lambda: 関数をかける(lambda x: x*2)
# urlparse: URLを分解してscheme(https), netloc(domain), pathを取り出せる
df["domain"] = df["url"].apply(lambda x: urlparse(str(x)).netloc)
print(df[["url", "domain"]].head())

# 各ドメインがそれぞれいくつあるか
domain_counts = df["domain"].value_counts()
print(domain_counts.head(50))

# 何種類ドメインが存在するか
print(df["domain"].nunique())

# 何回出現したドメインがいくつあるか
print(domain_counts.value_counts())

# ドメインごとの割合
domain_ratio = df["domain"].value_counts(normalize=True)*100
print(domain_ratio.head(10))

# 棒グラフ
plt.figure(figsize=(6, 12))
# kind="bash": 横向きの棒グラフ
domain_counts.head(50).plot(kind="barh")
plt.xlabel("Count")
plt.title("各ドメインが何個存在するか")
# gca(): 現在のaxes(描画領域)を取得
# invert_yazis(): y軸を反転して、一番多いものをtopにくるようにする
plt.gca().invert_yaxis()
plt.show()