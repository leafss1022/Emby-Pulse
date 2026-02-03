"""
查询参数解析工具
提供可重用的参数解析函数，消除代码重复
"""
from datetime import datetime, timedelta
from typing import Optional, List


def parse_comma_separated(value: Optional[str]) -> Optional[List[str]]:
    """
    解析逗号分隔的字符串为列表

    Args:
        value: 逗号分隔的字符串，例如 "a,b,c"

    Returns:
        字符串列表，如果输入为 None 或空字符串则返回 None

    Examples:
        >>> parse_comma_separated("a, b, c")
        ['a', 'b', 'c']
        >>> parse_comma_separated("")
        None
        >>> parse_comma_separated(None)
        None
    """
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


class FilterParams:
    """统一的筛选参数容器，用于存储解析后的参数"""

    def __init__(
        self,
        users: Optional[str] = None,
        clients: Optional[str] = None,
        devices: Optional[str] = None,
        item_types: Optional[str] = None,
        playback_methods: Optional[str] = None,
    ):
        """
        初始化筛选参数

        Args:
            users: 用户ID列表（逗号分隔）
            clients: 客户端列表（逗号分隔）
            devices: 设备列表（逗号分隔）
            item_types: 媒体类型列表（逗号分隔）
            playback_methods: 播放方式列表（逗号分隔）
        """
        self.user_list = parse_comma_separated(users)
        self.client_list = parse_comma_separated(clients)
        self.device_list = parse_comma_separated(devices)
        self.type_list = parse_comma_separated(item_types)
        self.method_list = parse_comma_separated(playback_methods)

    def to_dict(self):
        """返回解析后的参数字典，用于传递给 build_filter_conditions"""
        return {
            "users": self.user_list,
            "clients": self.client_list,
            "devices": self.device_list,
            "item_types": self.type_list,
            "playback_methods": self.method_list,
        }


def build_filter_conditions(
    days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    users: Optional[List[str]] = None,
    clients: Optional[List[str]] = None,
    devices: Optional[List[str]] = None,
    item_types: Optional[List[str]] = None,
    playback_methods: Optional[List[str]] = None,
    search: Optional[str] = None,
    local_date_func=None,
    name_mapping_service=None,
) -> tuple[str, list]:
    """
    构建通用的筛选条件
    返回 (WHERE 子句部分, 参数列表)

    Args:
        days: 天数范围
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        users: 用户ID列表
        clients: 客户端列表
        devices: 设备列表
        item_types: 媒体类型列表
        playback_methods: 播放方式列表
        search: 搜索关键词
        local_date_func: 用于转换日期的函数 (来自 database.py)
        name_mapping_service: 名称映射服务实例 (来自 name_mappings.py)
    """
    conditions = []
    params = []

    # 使用传入的 local_date 函数，如果没有传入则使用默认的列名
    if local_date_func:
        date_col = local_date_func("DateCreated")
    else:
        date_col = "date(DateCreated)"

    # 日期范围筛选
    if start_date and end_date:
        conditions.append(f"{date_col} >= date(?) AND {date_col} <= date(?)")
        params.extend([start_date, end_date])
    elif start_date:
        conditions.append(f"{date_col} >= date(?)")
        params.append(start_date)
    elif end_date:
        conditions.append(f"{date_col} <= date(?)")
        params.append(end_date)
    elif days:
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        conditions.append(f"{date_col} >= date(?)")
        params.append(since_date)

    # 用户筛选
    if users and len(users) > 0:
        placeholders = ",".join(["?" for _ in users])
        conditions.append(f"UserId IN ({placeholders})")
        params.extend(users)

    # 客户端筛选
    if name_mapping_service:
        expanded_clients = name_mapping_service.expand_client_filters(clients)
    else:
        expanded_clients = clients
    if expanded_clients and len(expanded_clients) > 0:
        placeholders = ",".join(["?" for _ in expanded_clients])
        conditions.append(f"ClientName IN ({placeholders})")
        params.extend(expanded_clients)

    # 设备筛选
    if name_mapping_service:
        expanded_devices = name_mapping_service.expand_device_filters(devices)
    else:
        expanded_devices = devices
    if expanded_devices and len(expanded_devices) > 0:
        placeholders = ",".join(["?" for _ in expanded_devices])
        conditions.append(f"DeviceName IN ({placeholders})")
        params.extend(expanded_devices)

    # 媒体类型筛选
    if item_types and len(item_types) > 0:
        placeholders = ",".join(["?" for _ in item_types])
        conditions.append(f"ItemType IN ({placeholders})")
        params.extend(item_types)

    # 播放方式筛选
    if playback_methods and len(playback_methods) > 0:
        placeholders = ",".join(["?" for _ in playback_methods])
        conditions.append(f"PlaybackMethod IN ({placeholders})")
        params.extend(playback_methods)

    # 搜索关键词筛选
    if search and search.strip():
        conditions.append("ItemName LIKE ?")
        params.append(f"%{search.strip()}%")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, params
