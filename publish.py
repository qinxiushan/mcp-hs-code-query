#!/usr/bin/env python
"""
自动化发布脚本 - 发布 MCP HS Code Query Server 到 PyPI

使用方法:
    python publish.py --test     # 发布到 TestPyPI
    python publish.py --prod     # 发布到 PyPI
    python publish.py --check    # 只检查不发布
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"\n🚀 执行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False


def clean_build_dirs():
    """清理构建目录"""
    print("\n🧹 清理旧的构建文件...")
    dirs_to_remove = ['dist', 'build', 'mcp_hs_code_query.egg-info']
    
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  删除: {dir_name}")
            shutil.rmtree(dir_path)
        else:
            print(f"  跳过: {dir_name} (不存在)")


def check_dependencies():
    """检查必要的依赖"""
    print("\n🔍 检查构建依赖...")
    required = ['build', 'twine']
    missing = []
    
    for package in required:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package],
            capture_output=True
        )
        if result.returncode != 0:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少必要依赖: {', '.join(missing)}")
        print(f"\n安装命令:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("✅ 所有依赖已安装")
    return True


def build_package():
    """构建包"""
    print("\n📦 构建分发包...")
    return run_command([sys.executable, '-m', 'build'])


def check_package():
    """检查包的质量"""
    print("\n🔍 检查包质量...")
    return run_command([sys.executable, '-m', 'twine', 'check', 'dist/*'])


def upload_to_testpypi():
    """上传到 TestPyPI"""
    print("\n📤 上传到 TestPyPI...")
    return run_command([
        sys.executable, '-m', 'twine', 'upload',
        '--repository', 'testpypi',
        'dist/*'
    ])


def upload_to_pypi():
    """上传到 PyPI"""
    print("\n📤 上传到 PyPI...")
    
    # 确认
    confirm = input("\n⚠️  确定要发布到正式 PyPI？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ 取消发布")
        return False
    
    return run_command([
        sys.executable, '-m', 'twine', 'upload',
        'dist/*'
    ])


def test_local_install():
    """测试本地安装"""
    print("\n🧪 测试本地安装...")
    
    # 找到 wheel 文件
    dist_dir = Path('dist')
    wheel_files = list(dist_dir.glob('*.whl'))
    
    if not wheel_files:
        print("❌ 未找到 wheel 文件")
        return False
    
    wheel_file = wheel_files[0]
    print(f"  使用文件: {wheel_file}")
    
    # 测试 uvx 运行
    print("\n  测试 uvx 运行...")
    result = subprocess.run(
        ['uvx', '--from', str(wheel_file), 'mcp-hs-code-query', '--help'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✅ uvx 测试成功")
        return True
    else:
        print("❌ uvx 测试失败")
        print(result.stderr)
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='发布 MCP HS Code Query Server')
    parser.add_argument('--test', action='store_true', help='发布到 TestPyPI')
    parser.add_argument('--prod', action='store_true', help='发布到 PyPI')
    parser.add_argument('--check', action='store_true', help='只检查不发布')
    parser.add_argument('--skip-clean', action='store_true', help='跳过清理步骤')
    
    args = parser.parse_args()
    
    print("="*60)
    print("MCP HS Code Query Server - 发布工具")
    print("="*60)
    
    # 步骤1: 检查依赖
    if not check_dependencies():
        return 1
    
    # 步骤2: 清理
    if not args.skip_clean:
        clean_build_dirs()
    
    # 步骤3: 构建
    if not build_package():
        print("\n❌ 构建失败")
        return 1
    
    # 步骤4: 检查
    if not check_package():
        print("\n❌ 包检查失败")
        return 1
    
    # 步骤5: 测试本地安装
    print("\n是否测试本地安装？(y/n): ", end='')
    if input().strip().lower() == 'y':
        test_local_install()
    
    # 步骤6: 上传
    if args.check:
        print("\n✅ 检查完成，跳过上传")
        return 0
    
    if args.test:
        if upload_to_testpypi():
            print("\n✅ 成功发布到 TestPyPI!")
            print("\n测试安装:")
            print("  pip install --index-url https://test.pypi.org/simple/ mcp-hs-code-query")
            return 0
        else:
            print("\n❌ 发布到 TestPyPI 失败")
            return 1
    
    if args.prod:
        if upload_to_pypi():
            print("\n✅ 成功发布到 PyPI!")
            print("\n安装命令:")
            print("  pip install mcp-hs-code-query")
            print("\nuvx 使用:")
            print("  uvx mcp-hs-code-query")
            return 0
        else:
            print("\n❌ 发布到 PyPI 失败")
            return 1
    
    # 没有指定上传目标
    print("\n请指定上传目标:")
    print("  --test  : 发布到 TestPyPI")
    print("  --prod  : 发布到 PyPI")
    print("  --check : 只检查不发布")
    return 0


if __name__ == '__main__':
    sys.exit(main())
