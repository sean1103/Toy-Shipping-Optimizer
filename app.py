


import gradio as gr
import pandas as pd
import math
from itertools import combinations
from numbers_parser import Document

# 資料全域變數
opt_target_allocate = []
product_list = []
original_file_path = None

# 處理 .numbers 檔案
current_file = None  # 全域變數，存最新上傳的檔案物件

def process_file(file):
    global opt_target_allocate, product_list, current_file
    current_file = file  # 儲存當前上傳檔案，給獲利查詢用

    doc = Document(file.name)
    sheets = doc.sheets
    filtered_weight_list = []
    all_products = []

    for sheet in sheets:
        for table in sheet.tables:
            data = table.rows(values_only=True)
            df = pd.DataFrame(data, columns=data[0])
            df.columns = df.columns.str.strip()

            if '集運時間' in df.columns and '重量(KG)' in df.columns and '玩具名稱' in df.columns:
                filtered = df[
                    df["集運時間"].isna() &
                    df["重量(KG)"].notna() &
                    df["玩具名稱"].notna()
                ]

                weights = filtered["重量(KG)"].tolist()
                products = filtered["玩具名稱"].tolist()
                filtered_weight_list.extend(weights)
                all_products.extend(products)

    opt_target_allocate = [round(float(w), 2) for w in filtered_weight_list]
    product_list = all_products
    
    # ✅ 將 [商品, 重量] 組合後做升冪排序
    sorted_pairs = sorted(zip(product_list, opt_target_allocate), key=lambda x: x[1])
    product_list, opt_target_allocate = zip(*sorted_pairs) if sorted_pairs else ([], [])


    # 用 [商品名稱 : 重量] , ... 格式輸出
    product_weight_str_list = [f"[{p} : {w}]" for p, w in zip(product_list, opt_target_allocate)]
    total_weight = round(sum(opt_target_allocate), 2)
    
    
    
    return f"上傳成功，共 {len(opt_target_allocate)} 筆，總重量: {total_weight} KG\n商品列表:\n" + ', '.join(product_weight_str_list)


def get_money(y, m):
    global current_file
    if current_file is None:
        return "請先上傳 .numbers 檔案"

    doc = Document(current_file.name)
    sheets = doc.sheets
    money_list = []
    product_list_profit = []

    for sheet in sheets:
        for table in sheet.tables:
            data = table.rows(values_only=True)
            df = pd.DataFrame(data, columns=data[0])
            df.columns = df.columns.str.strip()

            if '獲利日' in df.columns and '玩具名稱' in df.columns and '獲利' in df.columns:
                df['獲利日'] = pd.to_datetime(df['獲利日'], errors='coerce')

                if y == 0:
                    # 全部年份所有月份
                    filtered = df[df['獲利'].notna()]
                elif m == 0:
                    # 指定年份全部月份
                    filtered = df[(df['獲利日'].dt.year == y) & (df['獲利'].notna())]
                else:
                    # 指定年月
                    filtered = df[(df['獲利日'].dt.year == y) & (df['獲利日'].dt.month == m) & (df['獲利'].notna())]

                money_list.extend(filtered['獲利'].tolist())

                if y != 0 and m != 0:
                    product_list_profit.extend(filtered['玩具名稱'].tolist())

    total_profit = sum(money_list)

    if y == 0 or m == 0:
        # 不顯示明細
        return f"獲利總計: {total_profit} 元"
    else:
        # 顯示明細（[商品 : 獲利] 逗號分隔）
        detail_list = [f"[{p} : {m}]" for p, m in zip(product_list_profit, money_list)]
        return f"{y}年{m}月總獲利: {total_profit} 元\n\n獲利項目:\n" + ', '.join(detail_list)


# 查詢重量
def query_weights(input_names):
    names = [x.strip() for x in input_names.split(',')]
    output = []
    total = 0
    for name in names:
        if name in product_list:
            idx = product_list.index(name)
            weight = opt_target_allocate[idx]
            output.append(f"{name} : {weight} KG")
            total += float(weight)
        else:
            output.append(f"{name} : 未找到")
    output.append(f"總重量: {total:.2f} KG")
    return '\n'.join(output)

# 單筆最佳打包組合
def compute_cost(weight):
    kg = math.ceil(weight)
    cost = kg * 64
    if weight < 10:
        cost += 80
    return cost

def best_nearest_ceiling_combination(weight_list):
    weight_list = list(map(float, weight_list))
    n = len(weight_list)

    best_combo = []
    min_diff = float('inf')
    best_cost = float('inf')

    for r in range(1, n + 1):
        for combo in combinations(weight_list, r):
            weight = sum(combo)
            if 10 <= weight <= 13:
                diff = math.ceil(weight) - weight
                cost = compute_cost(weight)
                if (diff < min_diff) or (diff == min_diff and cost < best_cost):
                    min_diff = diff
                    best_cost = cost
                    best_combo = combo

    selected_index_list = []
    used = [False] * n
    for val in best_combo:
        for i in range(n):
            if not used[i] and weight_list[i] == val:
                selected_index_list.append(i)
                used[i] = True
                break

    product_name = [product_list[i] for i in selected_index_list]

    return best_combo, product_name, sum(best_combo), best_cost, math.ceil(sum(best_combo))

def once():
    combo, names, weight, cost, kg = best_nearest_ceiling_combination(opt_target_allocate)
    lines = []
    if weight < 10:
        lines.append("⚠️ 未達 10 公斤，建議考慮合併更多商品。\n")
        for name, w in zip(product_list, opt_target_allocate):
            lines.append(f"{name}: {w} KG")
        lines.append(f"\n總重量: {sum(opt_target_allocate):.2f} KG")
    else:
        lines.extend([
            "建議單筆組合:",
            f"商品: {names}",
            f"重量組合: {combo}",
            f"總重量: {weight:.2f} KG", 
            f"計費公斤(無條件進位): {kg} KG",
            f"運費: {cost} 元"
        ])
    return '\n'.join(lines)


# 介面設計
with gr.Blocks() as demo:
    gr.Markdown("UNION玩具集運分析工具")

    with gr.Tab("1. 上傳檔案"):
        file_input = gr.File(label="上傳 .numbers 檔案")
        upload_output = gr.Textbox(label="處理結果")
        file_input.change(fn=process_file, inputs=file_input, outputs=upload_output)

    with gr.Tab("2. 查詢玩具重量"):
        name_input = gr.Textbox(label="輸入玩具名稱（以逗號分隔）")
        weight_output = gr.Textbox(label="對應重量與總和")
        name_input.submit(fn=query_weights, inputs=name_input, outputs=weight_output)

    with gr.Tab("3. 單筆建議"):
        single_result = gr.Textbox(label="最佳單筆打包建議")
        btn_once = gr.Button("計算建議")
        btn_once.click(fn=once, outputs=single_result)

    with gr.Tab("4. 獲利查詢"):
        year = gr.Number(label="年份", precision=0)
        month = gr.Number(label="月份", precision=0)
        profit_output = gr.Textbox(label="獲利資訊")
        query_btn = gr.Button("查詢")
        query_btn.click(fn=get_money, inputs=[year, month], outputs=profit_output)

demo.launch()





