"""Enhanced statistics analyzer"""
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List
from statistics import median
from app.models.message import Message


class StatsAnalyzer:
    """Analyze message statistics with comprehensive dimensions"""

    EMOJI_LIST = ["捂脸", "笑哭", "呲牙", "流泪", "发怒", "害羞",
                  "破涕为笑", "旺柴", "奸笑", "偷笑", "阴险", "抠鼻"]

    @staticmethod
    def analyze(messages: List[Message]) -> dict:
        """Generate comprehensive statistics"""
        if not messages:
            return StatsAnalyzer._empty_stats()

        sorted_msgs = sorted(messages, key=lambda m: m.timestamp)

        # Basic counts
        total = len(messages)
        my_msgs = [m for m in messages if m.is_from_me]
        their_msgs = [m for m in messages if not m.is_from_me]
        my_count = len(my_msgs)
        their_count = len(their_msgs)

        # Message types
        type_counts = Counter(m.message_type for m in messages)

        # Message length
        lengths = [len(m.content or "") for m in messages if m.content]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        max_length = max(lengths) if lengths else 0
        min_length = min(lengths) if lengths else 0

        # Time distribution (hourly heatmap)
        time_dist = StatsAnalyzer._get_time_distribution(messages)
        hourly_heatmap = StatsAnalyzer._get_hourly_heatmap(messages)

        # Late night
        late_night = sum(1 for m in messages if 0 <= m.timestamp.hour < 5)

        # Weekend count
        weekend = sum(1 for m in messages if m.timestamp.weekday() >= 5)

        # Time span
        if sorted_msgs:
            time_span_days = (sorted_msgs[-1].timestamp - sorted_msgs[0].timestamp).days
        else:
            time_span_days = 0

        # Response time analysis
        my_response_time, their_response_time = StatsAnalyzer._calc_response_times(sorted_msgs)

        # Conversation analysis
        conversations = StatsAnalyzer._get_conversation_stats(sorted_msgs)

        # Word frequency
        my_top_words, their_top_words = StatsAnalyzer._get_top_words(my_msgs, their_msgs)

        # Emoji usage
        my_emoji, their_emoji = StatsAnalyzer._get_emoji_stats(my_msgs, their_msgs)

        # Daily activity
        my_by_day, their_by_day = StatsAnalyzer._get_daily_activity(my_msgs, their_msgs, sorted_msgs)

        return {
            "total_messages": total,
            "my_messages": my_count,
            "their_messages": their_count,
            "my_percentage": round(my_count / total * 100, 1) if total > 0 else 0,
            "their_percentage": round(their_count / total * 100, 1) if total > 0 else 0,
            "message_types": dict(type_counts),
            "avg_message_length": round(avg_length, 1),
            "max_message_length": max_length,
            "min_message_length": min_length,
            "time_distribution": time_dist,
            "hourly_heatmap": hourly_heatmap,
            "late_night_count": late_night,
            "late_night_percentage": round(late_night / total * 100, 1) if total > 0 else 0,
            "weekend_count": weekend,
            "weekend_percentage": round(weekend / total * 100, 1) if total > 0 else 0,
            "time_span_days": time_span_days,
            "my_median_response_minutes": round(my_response_time, 1),
            "their_median_response_minutes": round(their_response_time, 1),
            "conversations": conversations,
            "my_top_words": my_top_words[:30],
            "their_top_words": their_top_words[:30],
            "my_emoji_top": my_emoji[:10],
            "their_emoji_top": their_emoji[:10],
            "my_by_day": my_by_day,
            "their_by_day": their_by_day,
        }

    @staticmethod
    def _get_time_distribution(messages: List[Message]) -> dict:
        """Get message count by time period"""
        periods = {"凌晨": 0, "早晨": 0, "上午": 0, "中午": 0, "下午": 0, "晚上": 0}
        for msg in messages:
            hour = msg.timestamp.hour
            if 0 <= hour < 6:
                periods["凌晨"] += 1
            elif 6 <= hour < 9:
                periods["早晨"] += 1
            elif 9 <= hour < 12:
                periods["上午"] += 1
            elif 12 <= hour < 14:
                periods["中午"] += 1
            elif 14 <= hour < 18:
                periods["下午"] += 1
            else:
                periods["晚上"] += 1
        return periods

    @staticmethod
    def _get_hourly_heatmap(messages: List[Message]) -> list:
        """Get hourly message count (for heatmap chart)"""
        hourly = [0] * 24
        for msg in messages:
            hourly[msg.timestamp.hour] += 1
        return [{"hour": i, "count": hourly[i]} for i in range(24)]

    @staticmethod
    def _calc_response_times(sorted_msgs: List[Message]) -> tuple:
        """Calculate median response time for each person"""
        my_gaps = []
        their_gaps = []

        for i in range(1, len(sorted_msgs)):
            curr = sorted_msgs[i]
            prev = sorted_msgs[i - 1]

            # Only measure cross-person responses
            if curr.is_from_me != prev.is_from_me:
                gap_min = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < gap_min < 1440:  # Within 24h
                    if curr.is_from_me:
                        my_gaps.append(gap_min)
                    else:
                        their_gaps.append(gap_min)

        my_median = median(my_gaps) if my_gaps else 0
        their_median = median(their_gaps) if their_gaps else 0
        return my_median, their_median

    @staticmethod
    def _get_conversation_stats(sorted_msgs: List[Message]) -> dict:
        """Analyze conversation patterns"""
        if len(sorted_msgs) < 2:
            return {"total": 0, "avg_per_conversation": 0, "max_length": 0, "length_distribution": []}

        # Conversation boundary = gap > 2 hours
        conversations = []
        current = [sorted_msgs[0]]

        for i in range(1, len(sorted_msgs)):
            gap_hours = (sorted_msgs[i].timestamp - sorted_msgs[i-1].timestamp).total_seconds() / 3600
            if gap_hours > 2:
                conversations.append(current)
                current = [sorted_msgs[i]]
            else:
                current.append(sorted_msgs[i])
        conversations.append(current)

        conv_lengths = [len(c) for c in conversations]
        total_convs = len(conversations)

        return {
            "total": total_convs,
            "avg_per_conversation": round(sum(conv_lengths) / total_convs, 1) if total_convs else 0,
            "max_length": max(conv_lengths) if conv_lengths else 0,
            "length_distribution": [
                {"label": "1-5条", "count": sum(1 for l in conv_lengths if 1 <= l <= 5)},
                {"label": "6-15条", "count": sum(1 for l in conv_lengths if 6 <= l <= 15)},
                {"label": "16-30条", "count": sum(1 for l in conv_lengths if 16 <= l <= 30)},
                {"label": "30+条", "count": sum(1 for l in conv_lengths if l > 30)},
            ],
        }

    @staticmethod
    def _get_top_words(my_msgs: List[Message], their_msgs: List[Message]) -> tuple:
        """Get top words for each person"""
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不",
                      "人", "都", "一", "一个", "上", "也", "很", "到", "说",
                      "要", "去", "你", "会", "着", "没有", "看", "好", "自己",
                      "这", "他", "她", "它", "们", "那", "这个", "那个",
                      "什么", "怎么", "为什么", "因为", "所以", "但是",
                      "嗯", "哦", "啊", "吧", "吗", "呢", "哈", "啦", "哟"}

        def get_words(msgs):
            all_text = " ".join(m.content or "" for m in msgs)
            # Basic Chinese word segmentation by character bigrams
            words = []
            for char in all_text:
                if '一' <= char <= '鿿' and char not in stop_words:
                    words.append(char)
            return [w for w, c in Counter(words).most_common(50) if c >= 2]

        return get_words(my_msgs), get_words(their_msgs)

    @staticmethod
    def _get_emoji_stats(my_msgs: List[Message], their_msgs: List[Message]) -> tuple:
        """Extract emoji usage stats"""
        def extract_emoji_words(msgs):
            all_text = " ".join(m.content or "" for m in msgs)
            found = []
            for emoji in StatsAnalyzer.EMOJI_LIST:
                count = all_text.count(f"[{emoji}]")
                if count > 0:
                    found.append((emoji, count))
            return sorted(found, key=lambda x: -x[1])

        return extract_emoji_words(my_msgs), extract_emoji_words(their_msgs)

    @staticmethod
    def _get_daily_activity(my_msgs: List[Message], their_msgs: List[Message],
                            sorted_msgs: List[Message]) -> tuple:
        """Daily activity by day of week"""
        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        my_days = [0] * 7
        their_days = [0] * 7

        for m in my_msgs:
            my_days[m.timestamp.weekday()] += 1
        for m in their_msgs:
            their_days[m.timestamp.weekday()] += 1

        return (
            [{"day": day_names[i], "count": my_days[i]} for i in range(7)],
            [{"day": day_names[i], "count": their_days[i]} for i in range(7)],
        )

    @staticmethod
    def _empty_stats() -> dict:
        return {
            "total_messages": 0,
            "my_messages": 0,
            "their_messages": 0,
            "my_percentage": 0,
            "their_percentage": 0,
            "message_types": {},
            "avg_message_length": 0,
            "max_message_length": 0,
            "min_message_length": 0,
            "time_distribution": {},
            "hourly_heatmap": [],
            "late_night_count": 0,
            "late_night_percentage": 0,
            "weekend_count": 0,
            "weekend_percentage": 0,
            "time_span_days": 0,
            "my_median_response_minutes": 0,
            "their_median_response_minutes": 0,
            "conversations": {},
            "my_top_words": [],
            "their_top_words": [],
            "my_emoji_top": [],
            "their_emoji_top": [],
            "my_by_day": [],
            "their_by_day": [],
        }
