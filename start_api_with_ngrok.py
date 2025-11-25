"""
使用 ngrok 启动 API 服务并进行内网穿透
"""
import subprocess
import time
import sys
import os
import requests
import json
from threading import Thread

# 配置
API_PORT = 8000
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN', '')  # 可选:从环境变量读取


def start_api_server():
    """启动 API 服务"""
    print("=" * 60)
    print("正在启动 API 服务...")
    print("=" * 60)
    
    # 启动 Flask 服务
    subprocess.Popen(
        [sys.executable, 'api_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务启动
    print("等待 API 服务启动...")
    for i in range(10):
        try:
            response = requests.get(f'http://localhost:{API_PORT}/health', timeout=1)
            if response.status_code == 200:
                print(f"✓ API 服务已在端口 {API_PORT} 启动")
                return True
        except:
            time.sleep(1)
    
    print("✗ API 服务启动超时")
    return False


def start_ngrok():
    """启动 ngrok"""
    print("\n" + "=" * 60)
    print("正在启动 ngrok 内网穿透...")
    print("=" * 60)
    
    # 如果设置了认证令牌，先配置
    if NGROK_AUTH_TOKEN:
        print("配置 ngrok 认证令牌...")
        subprocess.run(['ngrok', 'config', 'add-authtoken', NGROK_AUTH_TOKEN])
    
    # 启动 ngrok
    print(f"启动 ngrok，映射端口 {API_PORT}...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(API_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待 ngrok 启动
    time.sleep(3)
    
    # 获取公网 URL
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        tunnels = response.json()
        
        if tunnels and 'tunnels' in tunnels and len(tunnels['tunnels']) > 0:
            public_url = tunnels['tunnels'][0]['public_url']
            print("\n" + "=" * 60)
            print("✓ ngrok 隧道已建立！")
            print("=" * 60)
            print(f"公网访问地址: {public_url}")
            print("=" * 60)
            print("\n可用接口:")
            print(f"  GET  {public_url}/health")
            print(f"  POST {public_url}/api/query")
            print(f"  POST {public_url}/api/batch_query")
            print(f"  POST {public_url}/api/query_by_code")
            print("\nngrok 控制面板: http://localhost:4040")
            print("=" * 60)
            
            # 显示测试命令
            print("\n测试命令示例:")
            print(f'curl -X POST {public_url}/api/query -H "Content-Type: application/json" -d "{{\\"product_name\\":\\"苹果\\"}}"')
            print("=" * 60)
            
            return ngrok_process, public_url
        else:
            print("✗ 无法获取 ngrok 公网地址")
            return ngrok_process, None
    except Exception as e:
        print(f"✗ 获取 ngrok 信息失败: {str(e)}")
        print("提示: 请确保已安装 ngrok，下载地址: https://ngrok.com/download")
        return ngrok_process, None


def test_public_api(public_url):
    """测试公网 API"""
    if not public_url:
        return
    
    print("\n" + "=" * 60)
    print("测试公网 API...")
    print("=" * 60)
    
    try:
        # 测试健康检查
        print("\n1. 测试健康检查接口...")
        response = requests.get(f'{public_url}/health', timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 测试商品查询
        print("\n2. 测试商品查询接口...")
        response = requests.post(
            f'{public_url}/api/query',
            json={'product_name': '苹果'},
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"   ✓ 查询成功")
            print(f"   HS编码: {result['data']['hs_code']}")
            print(f"   商品名称: {result['data']['product_name']}")
        else:
            print(f"   ✗ 查询失败: {result.get('error')}")
        
        print("\n✓ 公网 API 测试通过！")
        
    except Exception as e:
        print(f"\n✗ 公网 API 测试失败: {str(e)}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("HS 编码查询 API - ngrok 内网穿透启动器")
    print("=" * 60)
    
    # 检查 ngrok 是否安装
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
    except:
        print("\n✗ 未检测到 ngrok，请先安装:")
        print("   1. 访问 https://ngrok.com/download")
        print("   2. 下载并安装 ngrok")
        print("   3. （可选）注册账号并获取认证令牌")
        print("   4. （可选）运行: ngrok config add-authtoken YOUR_TOKEN")
        return
    
    # 启动 API 服务
    if not start_api_server():
        print("\n✗ API 服务启动失败，退出")
        return
    
    # 启动 ngrok
    ngrok_process, public_url = start_ngrok()
    
    if not public_url:
        print("\n⚠ ngrok 启动可能未成功，请检查:")
        print("   - ngrok 是否正确安装")
        print("   - 是否有其他程序占用端口 4040")
        print("   - 网络连接是否正常")
        return
    
    # 测试公网 API
    test_public_api(public_url)
    
    # 保持运行
    print("\n" + "=" * 60)
    print("服务正在运行...")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        ngrok_process.wait()
    except KeyboardInterrupt:
        print("\n\n正在关闭服务...")
        ngrok_process.terminate()
        print("服务已停止")


if __name__ == '__main__':
    main()
