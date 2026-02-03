"""
容器文件浏览路由
提供前端可用的目录浏览能力，便于选择数据库文件路径
"""
import os
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/files", tags=["files"])


def _normalize_path(path: str) -> str:
    """
    将传入路径转换为容器内的绝对路径
    """
    if not path:
        return "/"
    # 如果是相对路径，认为是相对于根目录的路径
    normalized = os.path.abspath(path if os.path.isabs(path) else os.path.join("/", path))
    # 避免出现空路径
    return normalized or "/"


@router.get("")
async def browse_files(
    path: str = Query("/", description="需要浏览的目录路径"),
    show_hidden: bool = Query(False, description="是否显示隐藏文件和目录"),
):
    """
    列出指定路径下的文件和目录
    """
    target_path = _normalize_path(path)

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="路径不存在")

    # 如果传入的是文件，则使用其上级目录，方便前端展示
    if os.path.isfile(target_path):
        target_path = os.path.dirname(target_path) or "/"

    if not os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail="路径不是目录")

    try:
        entries = []
        with os.scandir(target_path) as iterator:
            for entry in sorted(
                iterator,
                key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower())
            ):
                if not show_hidden and entry.name.startswith("."):
                    continue
                try:
                    stat = entry.stat(follow_symlinks=False)
                except (FileNotFoundError, PermissionError):
                    # 跳过在列举过程中被删除或无权限的文件
                    continue
                entries.append({
                    "name": entry.name,
                    "path": entry.path,
                    "is_dir": entry.is_dir(follow_symlinks=False),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })
    except PermissionError:
        raise HTTPException(status_code=403, detail="没有权限访问该路径")

    # 计算上级目录
    parent_path = None
    if target_path != "/":
        parent_candidate = os.path.dirname(target_path.rstrip("/")) or "/"
        parent_path = parent_candidate if parent_candidate != target_path else "/"

    return {
        "cwd": target_path,
        "parent": parent_path,
        "entries": entries
    }


