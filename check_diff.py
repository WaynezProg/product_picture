import pandas as pd

# 讀取兩個檔案
df1 = pd.read_csv("output.csv", dtype=str)
df2 = pd.read_csv("recheck_output.csv", dtype=str)

# 填補NaN為空字串，方便比較
df1 = df1.fillna("")
df2 = df2.fillna("")

# 檢查欄位是否一致
if list(df1.columns) != list(df2.columns):
    print("兩個檔案的欄位名稱不一致！")
    print("output.csv欄位：", df1.columns.tolist())
    print("recheck_output.csv欄位：", df2.columns.tolist())
else:
    # 以條碼為key合併
    key = "條碼"
    merged = df1.merge(df2, on=key, how="outer", suffixes=('_output', '_recheck'), indicator=True)

    # 找出只在其中一個檔案出現的條碼
    only_in_output = merged[merged['_merge'] == 'left_only'][key].tolist()
    only_in_recheck = merged[merged['_merge'] == 'right_only'][key].tolist()

    if only_in_output:
        print("只在output.csv出現的條碼：", only_in_output)
    if only_in_recheck:
        print("只在recheck_output.csv出現的條碼：", only_in_recheck)

    # 找出兩個檔案都有但內容不一樣的條碼
    diff_rows = []
    both = merged[merged['_merge'] == 'both']
    for idx, row in both.iterrows():
        diff = {}
        for col in df1.columns:
            if col == key:
                continue
            col1 = f"{col}_output"
            col2 = f"{col}_recheck"
            val1 = str(row[col1]) if pd.notnull(row[col1]) else ""
            val2 = str(row[col2]) if pd.notnull(row[col2]) else ""
            if val1 != val2:
                diff[col] = (val1, val2)
        if diff:
            diff_rows.append({
                key: row[key],
                "差異欄位": diff
            })

    if not only_in_output and not only_in_recheck and not diff_rows:
        print("output.csv和recheck_output.csv完全一致！")
    else:
        if diff_rows:
            print("以下條碼在兩個檔案中內容不一致：")
            for item in diff_rows:
                print(f"條碼：{item[key]}")
                for col, (v1, v2) in item["差異欄位"].items():
                    print(f"  欄位「{col}」 output.csv:「{v1}」 recheck_output.csv:「{v2}」")
                print("-" * 30)
