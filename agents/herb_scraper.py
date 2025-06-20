import pandas as pd
import json
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("herb_targets.log"),  # 日志保存到文件
        logging.StreamHandler()  # 日志输出到控制台
    ]
)

# 设置 Selenium WebDriver
driver = webdriver.Chrome()  # 确保 ChromeDriver 已正确安装

# 结果文件路径
RESULTS_FILE = "herb_targets.json"

def load_existing_results():
    """加载已保存的结果文件"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_results(results):
    """保存结果到文件"""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def set_page_size_to_50():
    """设置分页大小为 50 条/页"""
    try:
        # 找到分页大小选择器
        page_size_selector = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-tabs-tabpane-active')]//div[contains(@class, 'ant-select-selection-selected-value')]"))
        )
        page_size_selector.click()  # 点击选择器
        time.sleep(1)  # 等待下拉菜单弹出

        # 选择 50 条/页
        option_50 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '50 / page')]"))
        )
        option_50.click()
        time.sleep(3)  # 等待页面刷新
        logging.info("已将分页大小设置为 50 条/页")
    except Exception as e:
        logging.error(f"设置分页大小失败: {e}")

def extract_target_info(herb_id, herb_name):
    """提取中药的靶点信息"""
    # 构造中药详细信息页面 URL
    detail_url = f"http://herb.ac.cn/Detail/?v={herb_id}&label=Herb"
    driver.get(detail_url)
    time.sleep(3)  # 等待页面加载

    try:
        # 查找 Related Gene Targets 部分
        related_targets = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Related Gene Targets')]"))
        )
        logging.info(f"找到中药 {herb_name} 的 Related Gene Targets 部分")

        # 设置分页大小为 50 条/页
        set_page_size_to_50()

        # 存储所有靶点信息
        targets = []

        while True:
            # 查找目标信息表格
            targets_table = related_targets.find_element(By.XPATH, "./following-sibling::div//table")
            rows = targets_table.find_elements(By.TAG_NAME, "tr")

            # 提取当前页的 Target id 和 Target name
            for row in rows[1:]:  # 跳过表头
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    target_id = cells[0].text.strip()
                    target_name = cells[1].text.strip()
                    targets.append({"Target id": target_id, "Target name": target_name})
                    # 实时显示靶点信息
                    print(f"中药: {herb_name}, Target id: {target_id}, Target name: {target_name}")

            # 检查是否有下一页
            try:
                next_button = driver.find_element(By.XPATH, "//div[contains(@class, 'ant-tabs-tabpane-active')]//li[@title='Next Page']")
                if "ant-pagination-disabled" in next_button.get_attribute("class"):
                    break  # 如果没有下一页，退出循环
                next_button.click()
                time.sleep(3)  # 等待下一页加载
            except Exception as e:
                logging.error(f"无法找到下一页按钮: {e}")
                break

        return targets
    except Exception as e:
        logging.error(f"中药 {herb_name} 的页面未找到 Related Gene Targets 部分: {e}")
        return []

def main():
    # 读取 CSV 文件
    csv_file = r"E:\1-在研工作\2025-DeepTCM 2.0\herb\herbs.csv"  # 替换为你的 CSV 文件路径
    try:
        df = pd.read_csv(csv_file, encoding='gbk')  # 尝试使用 GBK 编码
    except UnicodeDecodeError:
        logging.warning("检测到编码问题，尝试使用 UTF-8 编码")
        df = pd.read_csv(csv_file, encoding='utf-8')

    # 加载已保存的结果
    results = load_existing_results()
    logging.info(f"已加载 {len(results)} 个中药的靶点信息")

    # 遍历每一行，获取 Herb_ 和 Herb_cn_name
    for index, row in df.iterrows():
        herb_id = row["Herb_"]
        herb_name = row["Herb_cn_name"]

        # 如果已经处理过该中药，则跳过
        if herb_name in results:
            logging.info(f"中药 {herb_name} 已处理，跳过")
            continue

        logging.info(f"正在处理中药: {herb_name} (ID: {herb_id})")

        # 提取目标信息
        targets = extract_target_info(herb_id, herb_name)
        results[herb_name] = targets

        # 实时保存结果
        save_results(results)
        logging.info(f"中药 {herb_name} 的靶点信息已保存")

    # 关闭浏览器
    driver.quit()
    logging.info("所有中药处理完成，数据已保存为 herb_targets.json")

if __name__ == "__main__":
    main()