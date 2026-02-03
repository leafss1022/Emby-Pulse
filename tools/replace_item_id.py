#!/usr/bin/env python3
"""
Emby Stats - Item ID 替换工具

用于替换 playback_reporting.db 中的 ItemId（处理剧集洗版后ID变化的情况）

使用方法：
    python replace_item_id.py <旧ID> <新ID> [数据库路径]

示例：
    python replace_item_id.py 209184 209420
    python replace_item_id.py 209184 209420 /data/playback_reporting.db
"""

import sqlite3
import sys
import os
from pathlib import Path


def replace_item_id(db_path: str, old_id: str, new_id: str):
    """替换数据库中的 ItemId"""

    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件不存在: {db_path}")
        return False

    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询受影响的记录数
        cursor.execute("SELECT COUNT(*) FROM PlaybackActivity WHERE ItemId = ?", (old_id,))
        count = cursor.fetchone()[0]

        if count == 0:
            print(f"⚠️  警告: 未找到 ItemId = {old_id} 的记录")
            conn.close()
            return True

        print(f"📊 找到 {count} 条记录需要更新")
        print(f"   旧ID: {old_id}")
        print(f"   新ID: {new_id}")

        # 确认操作
        confirm = input("\n确认执行替换？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            conn.close()
            return False

        # 执行更新
        cursor.execute("UPDATE PlaybackActivity SET ItemId = ? WHERE ItemId = ?", (new_id, old_id))
        updated = cursor.rowcount

        # 提交更改
        conn.commit()
        conn.close()

        print(f"✅ 成功更新 {updated} 条记录")
        return True

    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


def main():
    # 解析命令行参数
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    old_id = sys.argv[1]
    new_id = sys.argv[2]

    # 数据库路径
    if len(sys.argv) >= 4:
        db_path = sys.argv[3]
    else:
        # 默认路径
        db_path = "/data/playback_reporting.db"

    print("=" * 60)
    print("  Emby Stats - Item ID 替换工具")
    print("=" * 60)
    print(f"数据库: {db_path}")
    print()

    # 执行替换
    success = replace_item_id(db_path, old_id, new_id)

    print("=" * 60)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
