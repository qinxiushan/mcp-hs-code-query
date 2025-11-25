"""
API 接口测试脚本
"""
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:5000"


def test_health():
    """测试健康检查接口"""
    print("=" * 60)
    print("测试: 健康检查")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()


def test_single_query():
    """测试单个商品查询"""
    print("=" * 60)
    print("测试: 单个商品查询")
    print("=" * 60)
    
    products = ["苹果", "笔记本电脑", "T恤", "不存在的商品xyz123"]
    
    for product in products:
        print(f"\n查询商品: {product}")
        print("-" * 60)
        
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"product_name": product}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print(f"✓ 查询成功")
            print(f"  HS编码: {data.get('hs_code')}")
            print(f"  商品名称: {data.get('product_name')}")
            print(f"  法定单位: {data.get('first_unit')}")
        else:
            print(f"✗ 查询失败: {result.get('error')}")
    
    print()


def test_batch_query():
    """测试批量查询"""
    print("=" * 60)
    print("测试: 批量查询")
    print("=" * 60)
    
    products = ["苹果", "香蕉", "橙子", "笔记本电脑", "手机"]
    
    response = requests.post(
        f"{BASE_URL}/api/batch_query",
        json={"product_names": products}
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    print(f"总数: {result.get('total')}")
    print(f"成功: {result.get('successful')}")
    print(f"失败: {result.get('failed')}")
    print()
    
    for idx, item in enumerate(result.get('results', []), 1):
        query_name = item.get('query_product_name', '未知')
        if item.get('search_success'):
            print(f"{idx}. {query_name} ✓")
            print(f"   HS编码: {item.get('hs_code')}")
            print(f"   商品名称: {item.get('product_name')}")
        else:
            print(f"{idx}. {query_name} ✗")
            print(f"   错误: {item.get('error_message')}")
    
    print()


def test_query_by_code():
    """测试根据HS编码查询"""
    print("=" * 60)
    print("测试: 根据HS编码查询")
    print("=" * 60)
    
    hs_codes = ["08081000.00", "85249190.10", "61091000.00"]
    
    for hs_code in hs_codes:
        print(f"\n查询HS编码: {hs_code}")
        print("-" * 60)
        
        response = requests.post(
            f"{BASE_URL}/api/query_by_code",
            json={"hs_code": hs_code}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print(f"✓ 查询成功")
            print(f"  商品名称: {data.get('product_name')}")
            print(f"  商品描述: {data.get('description')}")
        else:
            print(f"✗ 查询失败: {result.get('error')}")
    
    print()


def test_error_cases():
    """测试错误情况"""
    print("=" * 60)
    print("测试: 错误处理")
    print("=" * 60)
    
    # 测试空请求
    print("\n1. 空商品名称")
    response = requests.post(f"{BASE_URL}/api/query", json={"product_name": ""})
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 测试缺少参数
    print("\n2. 缺少参数")
    response = requests.post(f"{BASE_URL}/api/query", json={})
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 测试批量查询超限
    print("\n3. 批量查询超限")
    response = requests.post(
        f"{BASE_URL}/api/batch_query",
        json={"product_names": [f"商品{i}" for i in range(51)]}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("HS 编码查询 API 测试")
    print("=" * 60)
    print()
    
    try:
        # 依次运行测试
        test_health()
        test_single_query()
        test_batch_query()
        test_query_by_code()
        test_error_cases()
        
        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 API 服务")
        print("请先运行: python api_server.py")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
