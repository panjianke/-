from selenium import webdriver  # 用于操作浏览器
from selenium.webdriver.chrome.options import Options  # 用于设置各种浏览器选项
from selenium.webdriver.chrome.service import Service  # 用于管理驱动
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By #元素定位
import time
from openai import OpenAI
import re
import ast

"pip install selenium"
"pip install openai   "

kpi = "你的deepseek的key"
phone = "你的学习通账号"
password ="你的密码"
url = "进入开始答题然后复制的网页
    client = OpenAI(
        api_key=kpi,
        base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": """
                【严格指令】
                 你是一个专业考试助手
                """
            },
            {"role": "user", "content": text},
        ],
        stream=stream_mode,  # 通过参数控制是否流式输出
        temperature=0.1,  # 增加一定随机性促进思考

    )

    return response.choices[0].message.content

#启动浏览器
def open():
    # 创建浏览器选项对象
    chrome_options = Options()

    # 添加无沙箱模式（提高兼容性）
    chrome_options.add_argument('--no-sandbox')

    # 保持浏览器窗口打开（即使代码执行完毕也不自动关闭）
    chrome_options.add_experimental_option('detach', True)

    # 创建并启动浏览器
    driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
    return driver

#开启登入
def login(driver):


    driver.get(
        url)

    driver.maximize_window()  # 最大化

    # 获取输入框
    driver.find_element(By.ID, 'phone').send_keys(phone)

    # 获取密码输入框
    driver.find_element(By.ID, 'pwd').send_keys(password)

    # 点击按钮
    a3 = driver.find_element(By.ID, 'loginBtn')

    a3.click()

    time.sleep(3)

#开始答题
def answer_uestions(map):

    #定义一个单选题数组
    single_choice = map["single_choice"]
    multiple_choice = map["multiple_choice"]
    true_false = map["true_false"]
    short_answer = map["short_answer"]
    sfill_in_blank = map["fill_in_blank"]


    # 拿到题目
    list = driver.find_elements(By.CLASS_NAME, "whiteDiv")

    # 查看选择题
    index1 = 0
    index2 = 0
    index3 = 0
    index4 = 0
    index5 = 0


    for i in list:
        list1 = i.find_elements(By.CLASS_NAME, "padBom50")
        # 拿到每一个id值
        # 拿到带单选每一题的id

        for i in list1:
             id = i.get_attribute("id")
             text = i.get_attribute("typename")

             if text == "单选题":
                 Choose(i,id,single_choice,index1)
                 index1 +=1

             if text == "多选题":
                 multipleChoice(i,id, multiple_choice,index2)
                 index2 += 1
             if text == "判断题":
                 Choose(i,id,true_false ,index3)
                 index3 +=1

             if text == "简答题":
                 Write(id,short_answer,index4)
                 index4 +=1
             if text =="填空题":
                 Write(id,sfill_in_blank,index5)
                 index5 +=1

#单选答题
def  Choose(i,id,arr,index):
    i.find_element(By.XPATH, f'//*[@id="{id}"]/div[2]/div[{arr[index]}]').click()

#简答
def  Write(id,short_answer,index4):

    parent_div = driver.find_element(By.XPATH, f'//*[@id="{id}"]/div[2]')

    # 2. 显式等待 iframe 出现（模糊 ID）
    iframe = WebDriverWait(parent_div, 10).until(
    EC.presence_of_element_located((By.XPATH, './/iframe[contains(@id, "ueditor_")]'))
                 )

     # 3. 切换到 iframe
    driver.switch_to.frame(iframe)

    # 4. 找 body 里的 p 标签
    p_tag = driver.find_element(By.TAG_NAME, 'p')

    # 5. 输入内容
    p_tag.send_keys(short_answer[index4])

    # 6. 可选：切回主文档
    driver.switch_to.default_content()

#多选
def multipleChoice(i,id,multiple_choice ,index):
    for itme in multiple_choice[index]:
        i.find_element(By.XPATH, f'//*[@id="{id}"]/div[2]/div[{itme}]').click()

#获取题目
def Get_the_question():
    arr = ["A","B","C","D"]
    #定义所有的题目

    text = ""
    # 拿到所有的题目（单选 多选 判断）
    list = driver.find_elements(By.CLASS_NAME, "whiteDiv")

    #拿到手游的题目的标题
    for i in list:
        title = i.find_element(By.CLASS_NAME, "type_tit").text #  # 拿到标题


        text = text + title + "\n"
        list_Choice = i.find_elements(By.CLASS_NAME, "padBom50")  # 查看单选的题目
        for i in list_Choice:
            id = i.get_attribute("id")
            topic = i.find_element(By.XPATH, f'//*[@id="{id}"]/h3').text  # 获取题目
            text = text + topic + "\n"
            choose = i.find_elements(By.CLASS_NAME, "clearfix")  # 获取到选择题
            index = 0
            for i in choose:
                choose = i.get_attribute("aria-label")  # 拿到每一个选择题
                a = choose.split()
                result = "".join(a[1:])
                result = arr[index]+result + "\n"
                text = text +  result + "\n"
                index = index + 1
    text = text+ """
    请认真回答问题，请将下面这套试题按如下要求分别整理成数组形式返回：

1. 单选题：选项 A=1, B=2, C=3, D=4，用数组形式返回，例如：[1, 4, 3]
2. 多选题：每题多个选项按 A=1, B=2, C=3, D=4 返回二维数组，例如：[[1, 2, 4], [1, 3]]
3. 判断题：对=1，错=2，用数组形式返回，例如：[2, 1, 2]
4. 简答题：只返回一个字符串数组，每题一句简洁的总结性回答，例如：["Vue开发效率高", "组合式API"]
5. 填空题：按顺序返回字符串数组，例如：["Vue CLI", "Model"]

格式要求如下：
- single_choice = [...]
- multiple_choice = [[...], [...]]
- true_false = [...]
- short_answer = ["...", "..."]
- fill_in_blank = ["...", "..."]"""
    return text

#解析文字
def test(text):
    if text =="":
        print("+++++++++++++++++++++++++++++++++++++++++题目返回失败+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    result = {}

    # 用正则表达式分割每个题型的部分（按 "数字. 题型名称：" 分割）
    sections = re.split(r'\d+\.\s*.*?：', text)[1:]  # [1:] 跳过第一个无关部分

    for section in sections:
        section = section.strip()
        if "=" in section:
            # 分割变量名和值
            var_part, val_part = section.split("=", 1)
            var_name = var_part.strip()
            # 移除注释并清理值部分
            val_str = val_part.split("#", 1)[0].strip()
            try:
                # 安全解析值
                parsed_val = ast.literal_eval(val_str)
                result[var_name] = parsed_val
            except Exception as e:
                print(f"解析失败：{var_name}，错误：{e}")

    return result


# 示例用法
if __name__ == '__main__':
    driver = open()
    print("++++++++++++++++++++正在登入++++++++++++++++++++++++++++")
    login(driver)
    print("+++++++++++++++++正在获取题目++++++++++++++++++++++++++++++")
    text = Get_the_question()
    print(f"+++++++++++++++++++++题目+++++++++++++++++++++")
    print(text)
    print("+++++++++++++++++++++++等待ai回答++++++++++++++++++++++++")
    list = deepseek(text)
    print(list)
    map = test(list)
    print(map)
    answer_uestions(map)



























