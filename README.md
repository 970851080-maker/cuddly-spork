# 晨间新闻日报（自动化）

每天北京时间 **08:00** 自动抓取多来源国内外重要新闻，完成去重、分类、中文精简摘要，并输出 Markdown 与 JSON，同时发送到邮箱（可选飞书/企业微信）。

## 特点

- 多来源：RSS/官方网页优先（`sources.yaml` 管理）
- 去重：SQLite 存历史 + 文本相似度去重
- 分类：固定 **12 个领域**（自然科学/工程技术/医学健康/农业食品/经济金融/政治治理/法律规则/社会文化/历史地理/教育认知/艺术审美/哲学宗教命理）
- 关注强化：住建部、发改委、财政部、交通运输部、基建/房地产/城市更新/工程建设、山西太原、哈尔滨、武汉；并额外输出“新闻联播要点”
- 最后一段“和我有什么关系”会根据当天内容动态分析与你的工程管理、暖通/机电、一建备考和太原回流相关的 3-5 条
- 输出：`output/daily/YYYY-MM-DD.md` 与 `output/daily/YYYY-MM-DD.json`
- 可选推送：SMTP 邮件、飞书 webhook、企业微信 webhook

## 快速开始（本地）

1) 安装依赖

```bash
python -m venv .venv
. .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2) 生成当天日报（北京时间）

```bash
python -m news_daily generate --sources sources.yaml
```

3) 发送到邮箱（可选）

```bash
setx NEWS_DAILY_SMTP_HOST smtp.qq.com
setx NEWS_DAILY_SMTP_PORT 465
setx NEWS_DAILY_SMTP_USER your@qq.com
setx NEWS_DAILY_SMTP_PASS "qq_smtp_auth_code"
setx NEWS_DAILY_EMAIL_TO "yl970851080@gmail.com,970851080@qq.com"
python -m news_daily send --date 2026-05-26
```

## 配置

- 新闻源：`sources.yaml`
- 数据库：默认 `output/news_daily.sqlite3`
- 输出目录：默认 `output/daily/`

### 环境变量（可选）

- `NEWS_DAILY_DB_PATH`：SQLite 路径
- `NEWS_DAILY_OUTPUT_DIR`：输出目录
- `NEWS_DAILY_HTTP_TIMEOUT`：抓取超时秒数（默认 15）
- `NEWS_DAILY_USER_PROFILE_JSON`：个人画像（JSON 字符串，可放 GitHub Secrets），用于“个人发展（大白话）”段落的定制化输出
- `NEWS_DAILY_BILINGUAL_SEPARATOR`：双语分隔符（默认 `---`）

#### SMTP 邮件
- `NEWS_DAILY_SMTP_HOST` / `NEWS_DAILY_SMTP_PORT`
- `NEWS_DAILY_SMTP_USER` / `NEWS_DAILY_SMTP_PASS`
- `NEWS_DAILY_EMAIL_TO`：逗号分隔收件人
- `NEWS_DAILY_EMAIL_FROM`：可选，默认同 `SMTP_USER`

如果没有配置 SMTP 或 webhook，`send` 命令会失败提示，避免自动任务看似成功但实际未发送。

#### Webhook
- `NEWS_DAILY_FEISHU_WEBHOOK`
- `NEWS_DAILY_WECOM_WEBHOOK`

## GitHub Actions（定时）

已提供两个工作流：

- `send_0800_bjt.yml`：北京时间 08:00 先生成当天日报，再发送邮件/推送，并提交生成文件（UTC 00:00）
- `fetch_0730_bjt.yml`：北京时间 07:30 自动抓取并提交，降低 08:00 发送时的抓取波动（UTC 23:30）

在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions` 中配置 SMTP 或 webhook 相关 secrets。收件人已在工作流里固定为 `yl970851080@gmail.com,970851080@qq.com`。

## 测试

```bash
pytest -q
```
