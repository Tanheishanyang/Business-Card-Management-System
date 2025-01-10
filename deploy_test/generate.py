# populate_info.py

import sqlite3
from faker import Faker
import random

# 配置参数
DATABASE = 'database.db'  # 你的数据库文件路径
NUM_RECORDS = 10000        # 需要插入的记录数量

# 初始化 Faker
fake = Faker('zh_CN')  # 使用中文本地化数据

# 定义一些常见的职位
TITLES = [
    '软件工程师', '数据分析师', '产品经理', '设计师', '市场专员',
    '销售经理', '人力资源经理', '财务分析师', '客服代表', '运营经理',
    '项目经理', '系统管理员', '网络工程师', '测试工程师', 'UI/UX 设计师'
]

def generate_unique_phone(existing_phones):
    """生成唯一的电话号码"""
    while True:
        phone = fake.phone_number()
        # 简单过滤，确保电话号码长度合理（例如 11 位中国手机号）
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) == 11 and phone not in existing_phones:
            return phone

def main():
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 获取现有的电话号码，以确保新生成的电话号码唯一
    cursor.execute('SELECT phone FROM info')
    existing_phones = set(row[0] for row in cursor.fetchall())

    # 准备要插入的数据
    records = []
    for _ in range(NUM_RECORDS):
        name = fake.name()
        phone = generate_unique_phone(existing_phones)
        existing_phones.add(phone)
        title = random.choice(TITLES)
        address = fake.address().replace('\n', ', ')
        image = None  # 不需要上传图片，可以设置为 NULL

        records.append((name, phone, title, address, image))

    # 插入数据
    try:
        cursor.executemany('''
            INSERT INTO info (name, phone, title, address, image)
            VALUES (?, ?, ?, ?, ?)
        ''', records)
        conn.commit()
        print(f"成功插入了 {NUM_RECORDS} 条记录到 'info' 表中。")
    except sqlite3.IntegrityError as e:
        print("插入数据时发生完整性错误：", e)
    except Exception as e:
        print("插入数据时发生错误：", e)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
