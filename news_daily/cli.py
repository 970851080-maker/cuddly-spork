import argparse

from .run import generate_daily, send_daily


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="news_daily")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="抓取新闻并生成日报（Markdown/JSON）")
    g.add_argument("--sources", default="sources.yaml")
    g.add_argument("--date", default=None, help="YYYY-MM-DD（北京时间），默认今天")

    s = sub.add_parser("send", help="发送指定日期日报到通知渠道")
    s.add_argument("--date", required=True, help="YYYY-MM-DD（北京时间）")

    args = parser.parse_args(argv)
    if args.cmd == "generate":
        generate_daily(date_str=args.date, sources_path=args.sources)
        return 0
    if args.cmd == "send":
        send_daily(date_str=args.date)
        return 0
    return 2

