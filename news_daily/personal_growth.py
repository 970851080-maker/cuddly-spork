from __future__ import annotations

from dataclasses import asdict

from .user_profile import UserProfile


def build_personal_growth(profile: UserProfile | None) -> dict[str, list[str]]:
    """
    Returns { "en": [...], "zh": [...] } lines.
    Keep it blunt, actionable, non-clinical.
    """
    if profile is None:
        return {
            "en": [
                "Career: Treat today as a compounding day — deliver measurable outputs, not vibes.",
                "Money: Make debt payoff automatic and block high-risk spending channels.",
                "Health: Fix sleep + daily steps first; everything else gets easier after that.",
            ],
            "zh": [
                "事业：把“每天交付”当复利，不要靠情绪和热血。",
                "钱：先把还债自动化，把高风险消费入口封死。",
                "健康：先救睡眠+日走路，其他都会跟着变好。",
            ],
        }

    # Tailor with a few profile-specific anchors (no fortune-telling).
    p = asdict(profile)
    city_next = p.get("next_city") or ""
    role = p.get("current_role") or "MEP/机电岗位"
    debt = profile.debt_cny or 0
    income = profile.take_home_monthly_cny or 0

    debt_line_en = (
        f"Money: Your priority is to clear ~CNY {debt} debt; automate repayment right after salary hits."
        if debt
        else "Money: Keep a strict budget; build an emergency buffer first."
    )
    debt_line_zh = f"钱：你最优先的是把欠款约 {debt} 元清掉；工资一到就自动还。" if debt else "钱：先立预算，再攒应急金。"

    move_line_en = f"Career: The move to {city_next} is a leverage point — show leadership via schedule/cost/acceptance control." if city_next else "Career: Your next role change is a leverage point — show leadership via schedule/cost/acceptance control."
    move_line_zh = f"事业：去 {city_next} 是杠杆点——用进度/成本/验收三件事把负责人坐实。" if city_next else "事业：下一次岗位变化是杠杆点——用进度/成本/验收三件事把负责人坐实。"

    return {
        "en": [
            f"Career: Your advantage is execution bursts. Your risk is relapse into short-term dopamine spending when stressed.",
            move_line_en,
            "Career: Track weekly deliverables (photos, quantities, approvals, close-out items) so your value is undeniable.",
            debt_line_en,
            "Relationships: No paid chat apps, no early money-gifting; only relationships that increase stability.",
            "Health: Sleep window + daily steps + simple diet structure; consider dermatology for acne if persistent.",
        ],
        "zh": [
            "事业：你强在关键期能冲上去；你最大的坑是压力一大就回到“短平快止痛（花钱/上头）”。",
            move_line_zh,
            "事业：每周留“交付证据”（照片、工程量、审批、销项清单），让价值不可替代。",
            debt_line_zh,
            "情感：不碰付费聊天；不在关系早期送钱；只选能让你更稳定的关系。",
            "健康：固定睡眠+日走路+饮食结构；痤疮反复就按皮肤科方案治。",
        ],
    }

