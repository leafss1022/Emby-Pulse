# Emby Stats

Emby 播放统计分析面板，提供直观的播放数据可视化。

## 功能特性

- **多服务器支持** - 管理多个 Emby 服务器，Web 界面配置
- **实时播放监控** - 查看当前正在播放的内容
- **播放趋势分析** - 按天/周/月查看播放趋势图表
- **热门内容排行** - 剧集、电影播放次数和时长排名
- **用户统计** - 各用户播放时长和次数统计
- **设备/客户端统计** - 播放设备和客户端分布
- **播放历史** - 最近播放记录查询，支持搜索
- **观影报告推送** - 通过 Telegram Bot 推送每日/每周/每月报告
- **名称映射** - 自定义客户端/设备显示名称
- **PWA 支持** - 可添加到主屏幕作为独立应用
- **管理员认证** - 使用 Emby 管理员账号登录保护

## 快速开始

### Docker Compose（推荐）

```yaml
services:
  emby-stats:
    image: qc0624/emby-stats:latest
    container_name: emby-stats
    ports:
      - "8899:8000"
    volumes:
      # 挂载 Emby 数据目录（包含 playback_reporting.db）
      - /path/to/emby/data:/data:ro
      # 配置持久化（保存服务器配置）
      - emby-stats-config:/config
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped

volumes:
  emby-stats-config:
```

### Docker Run

```bash
docker run -d \
  --name emby-stats \
  -p 8899:8000 \
  -v /path/to/emby/data:/data:ro \
  -v emby-stats-config:/config \
  -e TZ=Asia/Shanghai \
  qc0624/emby-stats:latest
```

访问 `http://your-server:8899`，使用 Emby **管理员账号**登录。

## 多服务器支持

v1.7 新增多服务器管理功能：

- **添加服务器**：登录后点击右上角服务器图标 → 添加服务器
- **文件选择器**：添加时可通过文件浏览器选择数据库路径
- **切换服务器**：登录页面或顶部栏下拉菜单选择
- **自动迁移**：旧版环境变量配置会自动迁移为第一个服务器

**多服务器配置示例：**

```yaml
volumes:
  # 服务器1
  - /path/to/emby1/data:/data1:ro
  # 服务器2
  - /path/to/emby2/data:/data2:ro
  # 配置持久化
  - emby-stats-config:/config
```

然后在 Web 界面添加服务器，数据库路径填写容器内路径（如 `/data1/playback_reporting.db`）。

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `EMBY_URL` | 否 | - | Emby 服务器地址（旧版配置，会自动迁移） |
| `EMBY_API_KEY` | 否 | - | Emby API Key（旧版配置，会自动迁移） |
| `TZ` | 否 | `UTC` | 时区设置（如 `Asia/Shanghai`） |
| `MIN_PLAY_SECONDS` | 否 | `60` | 最小播放秒数，低于此值不计入统计 |

> **注意**：推荐通过 Web 界面管理服务器配置，环境变量仅用于向后兼容。

## 数据目录

需要将 Emby 的 data 目录（包含 `playback_reporting.db`）挂载到容器：

```
/data                           # 容器内路径
└── playback_reporting.db       # 播放记录数据库（必需）
```

> 播放统计依赖 Emby 的 **Playback Reporting** 插件，请确保已安装并启用。

## 常见问题

**Q: 显示无数据？**
A: 请确认 Emby 已安装 Playback Reporting 插件，并且有播放记录。

**Q: 无法登录？**
A: 请使用 Emby 管理员账号登录，普通用户无权访问。

**Q: 海报不显示？**
A: 检查服务器地址是否正确配置，容器需要能访问 Emby 服务器。

## License

MIT
