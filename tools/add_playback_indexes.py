#!/usr/bin/env python3
"""
Emby Stats - 数据库索引优化工具

为 PlaybackActivity 表创建性能优化索引，显著提升查询性能。

使用方法:
    python tools/add_playback_indexes.py /path/to/playback_reporting.db

Docker 环境:
    docker exec emby-stats python /app/tools/add_playback_indexes.py /data/playback_reporting.db
"""

import aiosqlite
import asyncio
import sys
import time
from pathlib import Path


# 要创建的索引定义
INDEXES = [
    {
        "name": "idx_playback_date_user_item",
        "columns": "DateCreated, UserId, ItemId",
        "description": "用于按日期范围+用户+内容查询",
    },
    {
        "name": "idx_playback_item_date",
        "columns": "ItemId, DateCreated",
        "description": "用于内容聚合统计",
    },
    {
        "name": "idx_playback_user_date",
        "columns": "UserId, DateCreated",
        "description": "用于用户活跃度查询",
    },
    {
        "name": "idx_playback_date",
        "columns": "DateCreated DESC",
        "description": "用于历史记录按时间倒序查询",
    },
]


async def check_index_exists(db: aiosqlite.Connection, index_name: str) -> bool:
    """检查索引是否已存在"""
    cursor = await db.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type='index' AND name=?
        """,
        (index_name,)
    )
    result = await cursor.fetchone()
    return result is not None


async def get_table_count(db: aiosqlite.Connection) -> int:
    """获取 PlaybackActivity 表的记录数"""
    try:
        cursor = await db.execute("SELECT COUNT(*) FROM PlaybackActivity")
        result = await cursor.fetchone()
        return result[0] if result else 0
    except Exception:
        return 0


async def create_indexes(db_path: str) -> bool:
    """
    为 PlaybackActivity 表创建性能优化索引

    Args:
        db_path: 数据库文件路径

    Returns:
        bool: 是否成功完成
    """
    db_file = Path(db_path)

    # 检查数据库文件是否存在
    if not db_file.exists():
        print(f"❌ 错误: 数据库文件不存在: {db_path}")
        return False

    print(f"📊 正在连接数据库: {db_path}")

    try:
        async with aiosqlite.connect(db_path) as db:
            # 获取表记录数
            record_count = await get_table_count(db)
            if record_count == 0:
                print("⚠️  警告: PlaybackActivity 表为空或不存在")
                return False

            print(f"📈 数据库记录数: {record_count:,}")
            print(f"⏱️  预计索引创建时间: {max(1, record_count // 50000)} 秒")
            print()

            # 检查现有索引
            print("🔍 检查现有索引...")
            existing_indexes = []
            for index_def in INDEXES:
                exists = await check_index_exists(db, index_def["name"])
                if exists:
                    existing_indexes.append(index_def["name"])
                    print(f"   ✓ {index_def['name']} (已存在)")

            # 过滤出需要创建的索引
            indexes_to_create = [
                idx for idx in INDEXES
                if idx["name"] not in existing_indexes
            ]

            if not indexes_to_create:
                print("\n✅ 所有索引已存在，无需创建")
                return True

            print()
            print(f"📝 需要创建 {len(indexes_to_create)} 个索引")
            print()

            # 创建索引
            success_count = 0
            failed_indexes = []

            for idx_def in indexes_to_create:
                idx_name = idx_def["name"]
                columns = idx_def["columns"]
                description = idx_def["description"]

                print(f"🔨 创建索引: {idx_name}")
                print(f"   说明: {description}")
                print(f"   列: {columns}")

                start_time = time.time()

                try:
                    # 创建索引
                    await db.execute(f"""
                        CREATE INDEX IF NOT EXISTS {idx_name}
                        ON PlaybackActivity({columns})
                    """)
                    await db.commit()

                    elapsed_time = time.time() - start_time
                    print(f"   ✅ 完成 (耗时 {elapsed_time:.1f}s)")
                    success_count += 1

                except Exception as e:
                    print(f"   ❌ 失败: {e}")
                    failed_indexes.append(idx_name)
                    # 不中断，继续创建其他索引

                print()

            # 汇总结果
            print("=" * 60)
            print(f"✅ 成功创建: {success_count} 个索引")

            if failed_indexes:
                print(f"❌ 创建失败: {len(failed_indexes)} 个索引")
                print(f"   失败列表: {', '.join(failed_indexes)}")
                return False

            print()
            print("🎉 索引优化完成！预计查询性能提升 20-40%")
            print()
            print("💡 提示:")
            print("   - 如需验证索引，运行: sqlite3 <db_path> \".indices PlaybackActivity\"")
            print("   - 重启应用后生效")

            return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage():
    """打印使用说明"""
    print("=" * 60)
    print("Emby Stats - 数据库索引优化工具")
    print("=" * 60)
    print()
    print("使用方法:")
    print("  python tools/add_playback_indexes.py <数据库路径>")
    print()
    print("示例:")
    print("  # 单服务器")
    print("  python tools/add_playback_indexes.py /data/playback_reporting.db")
    print()
    print("  # Docker 环境")
    print("  docker exec emby-stats python /app/tools/add_playback_indexes.py /data/playback_reporting.db")
    print()
    print("  # 多服务器（分别执行）")
    print("  python tools/add_playback_indexes.py /data/server1/playback_reporting.db")
    print("  python tools/add_playback_indexes.py /data/server2/playback_reporting.db")
    print()


async def main():
    """主函数"""
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    db_path = sys.argv[1]

    print()
    print("=" * 60)
    print("🚀 开始索引优化")
    print("=" * 60)
    print()

    success = await create_indexes(db_path)

    print()
    print("=" * 60)

    if success:
        print("✅ 优化成功完成")
        sys.exit(0)
    else:
        print("❌ 优化失败")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
