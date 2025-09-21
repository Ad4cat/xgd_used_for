import pandas as pd
from urllib.parse import urlparse
import tldextract
import matplotlib.pyplot as plt
import japanize_matplotlib

df = pd.read_csv('xgd/remove_xgd.csv')

df["domain"] = df["url"].apply(lambda x: urlparse(str(x)).netloc)

# ベースドメインを取り出す関数を定義
def get_base_domain(domain: str) -> str:
    # NaNやNoneの場合はそのまま返す
    if pd.isna(domain):
        return domain

    # tldextractで分解
    ext = tldextract.extract(domain)
    # 例: docs.google.com → ExtractResult(subdomain='docs', domain='google', suffix='com')

    # domainとsuffixが両方あれば「google.com」のように組み立てる
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    else:
        # suffixが無い場合 (例: localhost, 127.0.0.1) は元の値を返す
        return domain
df["base_domain"] = df["domain"].apply(get_base_domain)
base_counts = df["base_domain"].value_counts()
# print(base_counts.head(20))

def get_brand(domain: str) -> str:
    ext = tldextract.extract(domain)
    if ext.domain:
        return ext.domain
    return domain

df["bland"] = df["domain"].apply(get_brand)
brand_counts = df["bland"].value_counts()
# print(brand_counts.head(20))

top_n = 15
top_brands = brand_counts.head(top_n)
others = pd.Series([brand_counts[top_n:].sum()], index=[f"その他({df["domain"].nunique() - top_n}個)"])
plot_data = pd.concat([top_brands, others])

plt.figure(figsize=(12, 12))
plot_data.plot(
    kind = "pie",
    autopct="%1.1f%%",
    startangle=90,
    counterclock=False
)
plt.ylabel("")
plt.title(f"ブランド別 割合(上位{top_n}個とその他)")
plt.show()