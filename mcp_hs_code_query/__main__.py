"""MCP HS Code Query Server - 命令行入口"""

import sys
from .server import mcp


def main():
    """主入口函数"""
    try:
        # 使用stdio传输启动MCP服务器
        mcp.run(transport="stdio")
        return 0
    except KeyboardInterrupt:
        print("\n服务已停止", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
