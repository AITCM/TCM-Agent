import json 

herb_names = ["柴胡", "天花粉", "当归", "红花", "甘草", "大黄", "桃仁"]

# 读取herb_targets.json文件
with open("herb_targets.json", "r", encoding="utf-8") as f:
    herb_targets = json.load(f)

# 遍历herb_names列表，打印每个名称对应的herb_targets
network_plot = {}
for herb_name in herb_names:
    network_plot[herb_name] = herb_targets[herb_name][:20]

print(network_plot)

# 将network_plot写入network_plot.json文件
with open("network_plot.json", "w", encoding="utf-8") as f:
    json.dump(network_plot, f, ensure_ascii=False)
