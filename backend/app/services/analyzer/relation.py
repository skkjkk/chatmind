"""Enhanced relationship analyzer with multi-dimensional scoring"""
from typing import List, Tuple
from datetime import timedelta
from statistics import median
from collections import Counter
from app.models.message import Message


class RelationAnalyzer:
    """Analyze relationship with comprehensive multi-factor models"""

    INTIMATE_CONTENT = {
        "想你了": 4, "想你": 3, "爱你": 5, "么么": 4, "抱抱": 4,
        "宝贝": 5, "宝宝": 5, "亲爱的": 5, "老公": 5, "老婆": 5,
        "晚安": 2, "早安": 2, "在一起": 5, "永远": 3,
        "梦见": 2, "梦到": 2, "牵手": 4, "拥抱": 4,
        "乖": 3, "乖乖": 3, "笨蛋": 1, "傻瓜": 1,
        "想你": 3, "好想你": 4, "想见你": 4, "见面": 2,
    }

    NEGATIVE_CONTENT = {
        "分手": -5, "冷战": -4, "生气": -3, "失望": -3,
        "算了": -2, "随便你": -3, "不想说": -2,
        "烦": -2, "别烦": -3, "滚": -5, "再见": -2,
    }

    MORNING_GREETINGS = {"早安", "早", "早上好", "早啊", "早安呀", "早早早"}
    NIGHT_GREETINGS = {"晚安", "晚", "晚安啦", "晚安呀", "好梦", "早点睡"}

    @staticmethod
    def analyze(messages: List[Message]) -> dict:
        """Analyze relationship characteristics"""
        if not messages:
            return RelationAnalyzer._empty_result()

        sorted_msgs = sorted(messages, key=lambda m: m.timestamp)
        my_msgs = [m for m in sorted_msgs if m.is_from_me]
        their_msgs = [m for m in sorted_msgs if not m.is_from_me]

        if not my_msgs or not their_msgs:
            return RelationAnalyzer._empty_result()

        # Core metrics
        intimacy = RelationAnalyzer._calc_intimacy(my_msgs, their_msgs, sorted_msgs)

        my_init, their_init = RelationAnalyzer._calc_initiative(my_msgs, their_msgs, sorted_msgs)

        trend = RelationAnalyzer._calc_trend(sorted_msgs)

        response_time = RelationAnalyzer._calc_response_time(sorted_msgs)

        role = RelationAnalyzer._get_role_summary(my_init, their_init, sorted_msgs)

        details = RelationAnalyzer._build_details(sorted_msgs, my_msgs, their_msgs, my_init, their_init, intimacy)

        return {
            "intimacy_score": round(intimacy, 1),
            "my_initiative_index": round(my_init, 1),
            "their_initiative_index": round(their_init, 1),
            "trend": trend,
            "role_summary": role,
            "response_time_minutes": round(response_time, 1),
            "details": details,
        }

    # ---- Intimacy Score: multi-factor model ----

    @staticmethod
    def _calc_intimacy(my_msgs: List[Message], their_msgs: List[Message],
                       all_msgs: List[Message]) -> float:
        """Intimacy 0-100 from communication frequency, response, content, etc."""
        if not all_msgs:
            return 0.0

        scores = []

        # 1) Communication frequency (25%)
        time_span = (all_msgs[-1].timestamp - all_msgs[0].timestamp).days + 1
        daily_rate = len(all_msgs) / max(time_span, 1)
        if daily_rate > 20:
            freq_score = 100
        elif daily_rate > 10:
            freq_score = 80
        elif daily_rate > 5:
            freq_score = 60
        elif daily_rate > 2:
            freq_score = 40
        elif daily_rate > 0.5:
            freq_score = 20
        else:
            freq_score = 10
        scores.append((freq_score, 0.25))

        # 2) Content intimacy (25%) — intimate language usage
        all_text = " ".join(m.content or "" for m in all_msgs)
        intimate_score = 0
        for word, weight in RelationAnalyzer.INTIMATE_CONTENT.items():
            count = all_text.count(word)
            intimate_score += count * weight
        # Cap at 100, scale from 0 to 100
        content_score = min(100, intimate_score * 5)
        scores.append((content_score, 0.25))

        # 3) Response time (20%) — quicker = more intimate
        gaps = []
        for i in range(1, len(all_msgs)):
            curr = all_msgs[i]
            prev = all_msgs[i - 1]
            if curr.is_from_me != prev.is_from_me:
                gap_min = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < gap_min < 1440:
                    gaps.append(gap_min)

        if gaps:
            median_gap = median(gaps)
            # < 5 min = 100, > 4 hours = 0
            gap_score = max(0, min(100, 100 - (median_gap / 240) * 100))
        else:
            gap_score = 50
        scores.append((gap_score, 0.20))

        # 4) Emoji & image usage (15%)
        emoji_count = sum(1 for m in all_msgs if m.message_type == "emoji")
        emoji_ratio = emoji_count / len(all_msgs)
        emoji_score = min(100, emoji_ratio * 200)  # 50% emoji → 100
        scores.append((emoji_score, 0.15))

        # 5）Greeting habits — say good morning/night? (15%)
        greeting_count = 0
        for msg in all_msgs:
            text = (msg.content or "").strip()
            if text in RelationAnalyzer.MORNING_GREETINGS or text in RelationAnalyzer.NIGHT_GREETINGS:
                greeting_count += 1

        daily_greeting_rate = greeting_count / max(time_span, 1)
        greeting_score = min(100, daily_greeting_rate * 500)  # 0.2 greetings/day = 100
        scores.append((greeting_score, 0.15))

        # Weighted average
        total = sum(s * w for s, w in scores)
        return max(0, min(100, total))

    # ---- Initiative Index (fixed) ----

    @staticmethod
    def _calc_initiative(my_msgs: List[Message], their_msgs: List[Message],
                         all_msgs: List[Message]) -> Tuple[float, float]:
        """Calculate initiative (who starts conversations)"""
        if len(all_msgs) < 2:
            return 50.0, 50.0

        # Conversation boundary = gap > 2 hours
        my_starts = 0
        their_starts = 0
        total_starts = 0

        for i in range(1, len(all_msgs)):
            gap_hours = (all_msgs[i].timestamp - all_msgs[i - 1].timestamp).total_seconds() / 3600
            if gap_hours > 2:
                total_starts += 1
                if all_msgs[i].is_from_me:
                    my_starts += 1
                else:
                    their_starts += 1

        if total_starts == 0:
            return 50.0, 50.0

        my_init = (my_starts / total_starts) * 100
        their_init = (their_starts / total_starts) * 100
        return my_init, their_init

    # ---- Response time ----

    @staticmethod
    def _calc_response_time(all_msgs: List[Message]) -> float:
        """Calculate average response time in minutes"""
        gaps = []
        for i in range(1, len(all_msgs)):
            gap_min = (all_msgs[i].timestamp - all_msgs[i - 1].timestamp).total_seconds() / 60
            if 0 < gap_min < 1440:  # Within 24h
                gaps.append(gap_min)

        if not gaps:
            return 0.0

        return median(gaps)

    # ---- Trend ----

    @staticmethod
    def _calc_trend(sorted_msgs: List[Message]) -> dict:
        """Analyze relationship trend with week-by-week comparison"""
        if len(sorted_msgs) < 20:
            return {"direction": "数据不足", "description": "消息量不足以分析趋势", "weekly_counts": []}

        # Group by week
        start_date = sorted_msgs[0].timestamp
        weekly = {}
        for msg in sorted_msgs:
            week_num = (msg.timestamp - start_date).days // 7
            if week_num not in weekly:
                weekly[week_num] = {"total": 0, "my": 0, "positive_score": 0}
            weekly[week_num]["total"] += 1
            if msg.is_from_me:
                weekly[week_num]["my"] += 1

        weeks = sorted(weekly.keys())
        weekly_counts = [weekly[w]["total"] for w in weeks]

        if len(weekly_counts) < 2:
            return {"direction": "平稳", "description": "数据时间跨度短", "weekly_counts": weekly_counts}

        # Compare first half vs second half
        mid = len(weekly_counts) // 2
        first_half = sum(weekly_counts[:mid]) / max(mid, 1)
        second_half = sum(weekly_counts[mid:]) / max(len(weekly_counts) - mid, 1)

        if first_half == 0:
            change_pct = 0
        else:
            change_pct = (second_half - first_half) / first_half * 100

        if change_pct > 30:
            direction = "升温中"
            desc = "最近聊天频率明显增加，关系在升温"
        elif change_pct > 10:
            direction = "轻微升温"
            desc = "聊天频率略有增加"
        elif change_pct < -30:
            direction = "降温中"
            desc = "最近聊天频率明显下降"
        elif change_pct < -10:
            direction = "轻微降温"
            desc = "聊天频率略有减少"
        else:
            direction = "平稳"
            desc = "关系保持稳定"

        return {
            "direction": direction,
            "description": desc,
            "change_percentage": round(change_pct, 1),
            "weekly_counts": weekly_counts,
        }

    # ---- Role summary ----

    @staticmethod
    def _get_role_summary(my_init: float, their_init: float, msgs: List[Message]) -> str:
        """Detailed role description"""
        # Who talks more
        my_msgs = [m for m in msgs if m.is_from_me]
        their_msgs = [m for m in msgs if not m.is_from_me]
        my_pct = len(my_msgs) / len(msgs) * 100 if msgs else 50
        their_pct = len(their_msgs) / len(msgs) * 100 if msgs else 50

        parts = []
        if my_init > 60 and their_init < 40:
            parts.append("你经常主动发起对话")
        elif their_init > 60 and my_init < 40:
            parts.append("对方更常主动找你")

        if my_pct > 60:
            parts.append("你说话更多")
        elif their_pct > 60:
            parts.append("对方说话更多")

        if not parts:
            parts.append("双方互动均衡")

        return "，".join(parts)

    # ---- Details ----

    @staticmethod
    def _build_details(sorted_msgs, my_msgs, their_msgs, my_init, their_init, intimacy) -> dict:
        """Build details for frontend display"""
        # Active time match
        my_hours = Counter(m.timestamp.hour for m in my_msgs)
        their_hours = Counter(m.timestamp.hour for m in their_msgs)
        my_peak_hour = my_hours.most_common(1)[0][0] if my_hours else 12
        their_peak_hour = their_hours.most_common(1)[0][0] if their_hours else 12
        time_match = "契合" if abs(my_peak_hour - their_peak_hour) <= 3 else "有差异"

        # Late night ratio
        late_night_ratio = sum(
            1 for m in sorted_msgs if 0 <= m.timestamp.hour < 5
        ) / len(sorted_msgs) if sorted_msgs else 0

        # Average message length gap
        my_avg_len = sum(len(m.content or "") for m in my_msgs) / len(my_msgs) if my_msgs else 0
        their_avg_len = sum(len(m.content or "") for m in their_msgs) / len(their_msgs) if their_msgs else 0

        return {
            "my_peak_hour": my_peak_hour,
            "their_peak_hour": their_peak_hour,
            "active_time_match": time_match,
            "late_night_ratio": round(late_night_ratio * 100, 1),
            "my_avg_message_length": round(my_avg_len, 1),
            "their_avg_message_length": round(their_avg_len, 1),
        }

    @staticmethod
    def _empty_result() -> dict:
        return {
            "intimacy_score": 0,
            "my_initiative_index": 50.0,
            "their_initiative_index": 50.0,
            "trend": {"direction": "数据不足", "description": "", "weekly_counts": []},
            "role_summary": "数据不足",
            "response_time_minutes": 0,
            "details": {},
        }
