"""
快速数据下载脚本 - 下载NYC餐厅和出租车数据
Quick Data Download Script for Where to DINE Project
"""

import requests
import pandas as pd
import json
from pathlib import Path

print("=" * 60)
print("Where to DINE - 数据下载工具")
print("=" * 60)

# 创建数据目录
Path("data/raw").mkdir(parents=True, exist_ok=True)


# ============ 1. 下载餐厅数据（使用NYC开放数据） ============
print("\n📍 步骤 1: 下载NYC餐厅数据...")
print("来源: NYC餐厅检查数据")

try:
    # NYC餐厅检查数据API
    api_url = "https://data.cityofnewyork.us/resource/43nn-pn8j.json"

    # 下载前5000条数据（示例）
    params = {
        "$limit": 5000,
        "$where": "latitude IS NOT NULL AND longitude IS NOT NULL",
        "$$app_token": "DEMO"  # 使用演示token
    }

    print("正在下载... (可能需要1-2分钟)")
    response = requests.get(api_url, params=params, timeout=120)

    if response.status_code == 200:
        data = response.json()

        # 转换为DataFrame
        df = pd.DataFrame(data)

        # 选择需要的列并重命名
        restaurants = df[[
            'dba',           # 餐厅名称
            'cuisine_description',  # 菜系
            'latitude',
            'longitude',
            'boro'           # 行政区
        ]].copy()

        restaurants.columns = ['name', 'cuisine', 'latitude', 'longitude', 'borough']
        restaurants['category'] = 'restaurant'

        # 转换坐标为数字
        restaurants['latitude'] = pd.to_numeric(restaurants['latitude'], errors='coerce')
        restaurants['longitude'] = pd.to_numeric(restaurants['longitude'], errors='coerce')

        # 删除无效坐标
        restaurants = restaurants.dropna(subset=['latitude', 'longitude'])

        # 只保留NYC范围内的餐厅
        restaurants = restaurants[
            (restaurants['latitude'] >= 40.4774) &
            (restaurants['latitude'] <= 40.9176) &
            (restaurants['longitude'] >= -74.2591) &
            (restaurants['longitude'] <= -73.7004)
        ]

        # 保存
        output_file = "data/raw/restaurants_nyc.csv"
        restaurants.to_csv(output_file, index=False)

        print(f"✅ 成功！下载了 {len(restaurants)} 个餐厅")
        print(f"   保存到: {output_file}")
        print(f"   文件大小: {Path(output_file).stat().st_size / 1024:.1f} KB")

    else:
        print(f"❌ 下载失败，HTTP状态码: {response.status_code}")
        print("   请稍后重试或手动下载")

except Exception as e:
    print(f"❌ 下载餐厅数据时出错: {e}")
    print("   您可以稍后手动下载或使用其他方法")


# ============ 2. 出租车数据说明 ============
print("\n\n🚕 步骤 2: 出租车数据下载说明")
print("-" * 60)
print("由于出租车数据文件很大（100-200 MB/月），")
print("需要您手动下载。以下是下载方法：")
print()
print("方法A - 使用wget命令（推荐）:")
print("  wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet")
print("  mv yellow_tripdata_2023-09.parquet data/raw/taxi_trips_2023_09.parquet")
print()
print("方法B - 浏览器下载:")
print("  1. 访问: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page")
print("  2. 选择 Yellow Taxi Trip Records")
print("  3. 下载 2023年9月数据 (yellow_tripdata_2023-09.parquet)")
print("  4. 移动到 data/raw/ 目录")
print()
print("方法C - 使用测试数据:")
print("  创建小型测试数据集（见下方代码）")


# ============ 3. 创建测试用出租车数据 ============
print("\n\n📝 步骤 3: 创建测试数据（用于快速测试）")
print("-" * 60)

try:
    import numpy as np
    from datetime import datetime, timedelta

    print("正在生成1000条测试出租车数据...")

    # 生成测试数据
    np.random.seed(42)

    # 纽约市热门餐饮区域中心点
    hotspot_centers = [
        (40.7589, -73.9851, "Times Square"),
        (40.7282, -73.9942, "Greenwich Village"),
        (40.7614, -73.9776, "Midtown"),
        (40.7223, -73.9875, "Lower East Side"),
        (40.7489, -73.9680, "Murray Hill"),
    ]

    records = []
    base_date = datetime(2023, 9, 15)

    for i in range(1000):
        # 随机选择一个热点区域
        center_lat, center_lon, area_name = hotspot_centers[np.random.randint(0, len(hotspot_centers))]

        # 在中心点周围随机偏移
        lat = center_lat + np.random.normal(0, 0.005)
        lon = center_lon + np.random.normal(0, 0.005)

        # 随机时间（午餐或晚餐时段）
        hour = np.random.choice([12, 13, 18, 19, 20])
        minute = np.random.randint(0, 60)
        day_offset = np.random.randint(0, 30)

        dt = base_date + timedelta(days=day_offset, hours=hour, minutes=minute)

        records.append({
            'dropoff_datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'dropoff_latitude': lat,
            'dropoff_longitude': lon
        })

    # 保存测试数据
    test_df = pd.DataFrame(records)
    test_file = "data/raw/taxi_trips_test.csv"
    test_df.to_csv(test_file, index=False)

    print(f"✅ 测试数据创建成功！")
    print(f"   保存到: {test_file}")
    print(f"   包含 {len(test_df)} 条记录")
    print(f"   覆盖区域: {', '.join([c[2] for c in hotspot_centers])}")

except Exception as e:
    print(f"❌ 创建测试数据时出错: {e}")


# ============ 总结 ============
print("\n\n" + "=" * 60)
print("📋 下载总结")
print("=" * 60)
print()
print("已完成:")
print("  ✅ 餐厅数据: data/raw/restaurants_nyc.csv")
print("  ✅ 测试用出租车数据: data/raw/taxi_trips_test.csv")
print()
print("待完成:")
print("  ⏳ 真实出租车数据: 需手动下载（见上方说明）")
print()
print("下一步:")
print("  1. 检查 data/raw/ 目录确认文件存在")
print("  2. 运行数据处理脚本: cd backend/data_processing")
print("  3. 执行: python 01_cluster_restaurants.py")
print()
print("=" * 60)
print("下载完成！")
print("=" * 60)
