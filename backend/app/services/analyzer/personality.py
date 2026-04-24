"""Enhanced personality analyzer with multi-dimensional weighted scoring"""
import re
from typing import List
from statistics import median, stdev
from collections import Counter
from app.models.message import Message


class PersonalityAnalyzer:
    """Analyze personality traits using multi-factor models"""

    # ---- Large sentiment dictionaries ----

    POSITIVE_WORDS = {
        "开心", "快乐", "幸福", "感动", "温暖", "甜蜜", "美好", "棒", "赞", "优秀",
        "喜欢", "爱", "爱你", "么么", "真好", "完美", "厉害", "加油", "哈哈", "哇",
        "好看", "好吃", "好玩", "好棒", "好美", "好可爱", "可爱", "漂亮", "帅",
        "恭喜", "祝福", "幸运", "期待", "期待", "希望", "满足", "满意", "舒服",
        "轻松", "自由", "爽", "酷", "妙", "优秀", "惊艳", "绝了", "牛", "牛逼",
        "好看", "香", "赚了", "笑死", "好家伙", "太棒", "太美", "太好了",
    }

    NEGATIVE_WORDS = {
        "累", "困", "烦", "无聊", "难过", "伤心", "生气", "讨厌", "郁闷",
        "无奈", "压力", "烦死了", "无语", "崩溃", "傻", "哼", "糟糕",
        "恶心", "恐怖", "可怕", "担心", "焦虑", "紧张", "痛苦", "难受",
        "垃圾", "差劲", "垃圾", "恶心", "失败", "惨", "惨了", "完蛋",
        "气死", "火大", "烦躁", "疲惫", "绝望", "后悔", "失望", "伤心",
        "悲伤", "孤独", "寂寞", "心痛", "心疼", "疼", "痛", "苦",
        "麻烦", "头疼", "头晕", "生病", "感冒", "发烧", "倒霉", "背",
    }

    RATIONAL_WORDS = {
        "应该": 2, "因为": 3, "所以": 3, "但是": 2, "而且": 2,
        "或者": 2, "如果": 3, "可能": 2, "分析": 3, "觉得": 1,
        "认为": 3, "逻辑": 4, "事实": 3, "原因": 3, "结果": 2,
        "对比": 3, "比较": 2, "相对": 2, "考虑": 2, "判断": 3,
        "结论": 3, "依据": 4, "根据": 3, "数据": 3, "调查": 3,
        "研究": 3, "证明": 3, "解释": 2, "说明": 2, "实际上": 3,
        "本质上": 4, "一般来说": 3, "理论上": 4, "否则": 3,
        "尽管": 3, "虽然": 2, "然而": 3, "因此": 3,
    }

    EMOTIONAL_WORDS = {
        "感觉": 2, "心情": 3, "情绪": 3, "感动": 4, "温暖": 3,
        "幸福": 3, "甜蜜": 3, "想": 1, "好想": 2, "希望": 2,
        "但愿": 2, "怕": 2, "害怕": 3, "忍不住": 3, "突然": 1,
        "好像": 1, "仿佛": 2, "心动": 3, "心疼": 4, "心酸": 4,
        "眼眶": 4, "流泪": 3, "哭": 3, "笑": 2, "微笑": 2,
        "想念": 4, "牵挂": 4, "依赖": 4, "拥抱": 3,
    }

    DIRECT_WORDS = {
        "直接": 3, "肯定": 3, "一定": 3, "必须": 4, "绝对": 4,
        "就是": 2, "不是": 2, "要": 1, "不要": 2, "行": 1,
        "不行": 2, "可以": 1, "不可以": 2, "好": 1, "不好": 2,
        "去": 1, "来": 1, "做": 1, "说": 1, "找": 1,
        "给": 1, "拿": 1, "走": 1, "买": 1, "吃": 1,
        "废话": 3, "当然": 2, "明显": 3, "简单": 2,
    }

    INDIRECT_WORDS = {
        "可能": 2, "也许": 3, "大概": 2, "好像": 2, "似乎": 3,
        "要不": 2, "你觉得": 3, "要不要": 2, "好不好": 2,
        "有点": 1, "稍微": 2, "不太": 1, "不一定": 2,
        "考虑一下": 3, "再说吧": 3, "随便": 2, "都行": 2,
        "看你": 2, "随便吧": 2, "无所谓": 3, "慢慢": 1,
        "或许": 3, "说不定": 3, "按理说": 3,
    }

    INTIMATE_WORDS = {
        "宝贝": 4, "宝宝": 4, "亲爱的": 4, "老公": 4, "老婆": 4,
        "想你了": 4, "爱你": 4, "么么": 4, "抱抱": 4, "亲": 3,
        "晚安": 2, "早安": 2, "想你": 4, "在一起": 4, "永远": 3,
        "乖乖": 3, "笨蛋": 2, "傻瓜": 2, "猪": 2, "坏蛋": 2,
        "男朋友": 3, "女朋友": 3, "对象": 2,
    }

    # Time periods
    PERIODS = ["凌晨", "早晨", "上午", "中午", "下午", "晚上", "深夜"]

    @staticmethod
    def analyze(messages: List[Message]) -> dict:
        """Analyze personality characteristics with improved algorithms"""
        if not messages:
            return PersonalityAnalyzer._empty_result()

        sorted_msgs = sorted(messages, key=lambda m: m.timestamp)
        my_msgs = [m for m in sorted_msgs if m.is_from_me]
        their_msgs = [m for m in sorted_msgs if not m.is_from_me]

        if not my_msgs or not their_msgs:
            return PersonalityAnalyzer._empty_result()

        # Compute all dimensions
        my_extro = PersonalityAnalyzer._calc_extroversion(my_msgs, their_msgs, sorted_msgs)
        their_extro = PersonalityAnalyzer._calc_extroversion(their_msgs, my_msgs, sorted_msgs)

        my_rational = PersonalityAnalyzer._calc_rational(my_msgs)
        their_rational = PersonalityAnalyzer._calc_rational(their_msgs)

        my_positive = PersonalityAnalyzer._calc_positive(my_msgs)
        their_positive = PersonalityAnalyzer._calc_positive(their_msgs)

        my_direct = PersonalityAnalyzer._calc_directness(my_msgs)
        their_direct = PersonalityAnalyzer._calc_directness(their_msgs)

        my_style = PersonalityAnalyzer._get_interaction_style(my_msgs, sorted_msgs)
        their_style = PersonalityAnalyzer._get_interaction_style(their_msgs, sorted_msgs)

        summary, details = PersonalityAnalyzer._generate_summary(
            my_extro, their_extro, my_rational, their_rational,
            my_positive, their_positive, my_direct, their_direct
        )

        return {
            "my_extroversion_score": round(my_extro, 1),
            "their_extroversion_score": round(their_extro, 1),
            "my_rational_score": round(my_rational, 1),
            "their_rational_score": round(their_rational, 1),
            "my_positive_score": round(my_positive, 1),
            "their_positive_score": round(their_positive, 1),
            "my_direct_score": round(my_direct, 1),
            "their_direct_score": round(their_direct, 1),
            "my_interaction_style": my_style,
            "their_interaction_style": their_style,
            "summary": summary,
            "details": details,
        }

    # ---- Extroversion: multi-factor ----

    @staticmethod
    def _calc_extroversion(me: List[Message], other: List[Message],
                           all_msgs: List[Message]) -> float:
        """Extroversion: volume + initiative + response + energy"""
        if not all_msgs or not me:
            return 50.0

        # 1) Volume ratio (30%)
        vol_ratio = len(me) / len(all_msgs) * 100  # 0-100
        vol_score = min(vol_ratio * 1.5, 100)

        # 2) Initiative — who starts conversations (30%)
        init_score = PersonalityAnalyzer._initiative_score(me, all_msgs)

        # 3) Avg message length vs counterpart (15%)
        my_avg_len = sum(len(m.content or "") for m in me) / len(me)
        other_avg_len = sum(len(m.content or "") for m in other) / len(other) if other else my_avg_len
        if my_avg_len + other_avg_len > 0:
            len_ratio = my_avg_len / (my_avg_len + other_avg_len)
        else:
            len_ratio = 0.5
        len_score = len_ratio * 100

        # 4) Energy — exclamation + question mark usage (15%)
        exclam_count = sum(1 for m in me if "！" in (m.content or "") or "!" in (m.content or ""))
        exclam_ratio = exclam_count / len(me) if me else 0
        energy_score = min(exclam_ratio * 200, 100)

        # 5) Response speed (10%)
        speed_score = PersonalityAnalyzer._response_speed_score(me, all_msgs)

        return (vol_score * 0.30 + init_score * 0.30 +
                len_score * 0.15 + energy_score * 0.15 + speed_score * 0.10)

    @staticmethod
    def _initiative_score(my_msgs: List[Message], all_msgs: List[Message]) -> float:
        """How often does this person start conversations?"""
        if len(all_msgs) < 2:
            return 50.0

        # A conversation boundary = gap > 2 hours
        my_starts = 0
        total_starts = 0
        for i in range(1, len(all_msgs)):
            gap = (all_msgs[i].timestamp - all_msgs[i - 1].timestamp).total_seconds() / 3600
            if gap > 2:
                total_starts += 1
                if all_msgs[i].is_from_me == my_msgs[0].is_from_me:
                    my_starts += 1

        if total_starts == 0:
            return 50.0
        return (my_starts / total_starts) * 100

    @staticmethod
    def _response_speed_score(my_msgs: List[Message], all_msgs: List[Message]) -> float:
        """Score based on how quickly the person responds"""
        gaps = []
        for i in range(1, len(all_msgs)):
            curr = all_msgs[i]
            prev = all_msgs[i - 1]
            if curr.is_from_me and not prev.is_from_me:
                gap_min = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < gap_min < 1440:  # Within 24 hours
                    gaps.append(gap_min)

        if not gaps:
            return 50.0

        median_gap = median(gaps)
        # Fast response < 5 min → 100, slow > 2 hours → 0
        score = max(0, min(100, 100 - (median_gap / 120) * 100))
        return score

    # ---- Rational vs Emotional ----

    @staticmethod
    def _calc_rational(messages: List[Message]) -> float:
        """Rational vs emotional: weighted keyword model"""
        if not messages:
            return 50.0

        all_text = " ".join(m.content or "" for m in messages)

        # Score rational words
        rational_score = 0
        for word, weight in PersonalityAnalyzer.RATIONAL_WORDS.items():
            count = all_text.count(word)
            rational_score += count * weight

        # Score emotional words
        emotional_score = 0
        for word, weight in PersonalityAnalyzer.EMOTIONAL_WORDS.items():
            count = all_text.count(word)
            emotional_score += count * weight

        total = rational_score + emotional_score
        if total == 0:
            return 50.0

        # Ratio → score, centered at 50
        ratio = rational_score / total
        return min(95, max(5, ratio * 100))

    # ---- Positive vs Negative ----

    @staticmethod
    def _calc_positive(messages: List[Message]) -> float:
        """Positive vs negative: dictionary + emoji + negation"""
        if not messages:
            return 50.0

        pos_score = 0
        neg_score = 0

        for msg in messages:
            text = msg.content or ""
            # Count positive words (with negation check)
            for word in PersonalityAnalyzer.POSITIVE_WORDS:
                idx = text.find(word)
                while idx != -1:
                    # Check for negation within 2 chars before
                    start = max(0, idx - 2)
                    prefix = text[start:idx]
                    if not any(neg in prefix for neg in ["不", "没", "别", "无"]):
                        pos_score += 1
                    else:
                        neg_score += 1  # Negated positive = negative
                    idx = text.find(word, idx + 1)

            # Count negative words
            for word in PersonalityAnalyzer.NEGATIVE_WORDS:
                count = text.count(word)
                neg_score += count

            # Emoji sentiment
            if msg.message_type == "emoji":
                # Emoji-only messages are often positive
                if "捂脸" in text or "笑哭" in text or "呲牙" in text:
                    pos_score += 1
                elif "流泪" in text or "发怒" in text:
                    neg_score += 1

        total = pos_score + neg_score
        if total == 0:
            return 50.0

        return min(95, max(5, (pos_score / total) * 100))

    # ---- Directness ----

    @staticmethod
    def _calc_directness(messages: List[Message]) -> float:
        """Direct vs indirect: multi-factor"""
        if not messages:
            return 50.0

        all_text = " ".join(m.content or "" for m in messages)

        # 1) Direct / indirect word ratio (50%)
        direct_score = sum(count * PersonalityAnalyzer.DIRECT_WORDS.get(word, 1)
                          for word, count in Counter(all_text.split()).items()
                          if word in PersonalityAnalyzer.DIRECT_WORDS)
        indirect_score = sum(count * PersonalityAnalyzer.INDIRECT_WORDS.get(word, 1)
                            for word, count in Counter(all_text.split()).items()
                            if word in PersonalityAnalyzer.INDIRECT_WORDS)
        word_total = direct_score + indirect_score
        word_ratio = direct_score / word_total if word_total > 0 else 0.5

        # 2) Sentence length factor (30%) — direct people use shorter sentences
        lengths = [len(m.content or "") for m in messages if m.content]
        short_count = sum(1 for l in lengths if 1 <= l <= 15)
        short_ratio = short_count / len(lengths) if lengths else 0.5
        len_factor = min(short_ratio * 2, 1)  # 0-1

        # 3) Question mark usage (20%) — indirect people ask more
        q_count = sum(1 for m in messages if "？" in (m.content or "") or "?" in (m.content or ""))
        q_ratio = q_count / len(messages)
        q_factor = 1 - min(q_ratio * 2, 1)  # Less questions = more direct

        score = (word_ratio * 0.50 + len_factor * 0.30 + q_factor * 0.20) * 100
        return min(95, max(5, score))

    # ---- Interaction Style ----

    @staticmethod
    def _get_interaction_style(messages: List[Message], all_msgs: List[Message]) -> str:
        """Classify interaction style with more granular categories"""
        if not messages:
            return "未知"

        text = " ".join(m.content or "" for m in messages)

        q_ratio = sum(1 for m in messages if "？" in (m.content or "") or "?" in (m.content or "")) / len(messages)
        avg_len = sum(len(m.content or "") for m in messages) / len(messages)
        long_msg_ratio = sum(1 for m in messages if len(m.content or "") > 50) / len(messages)
        exclam_ratio = sum(1 for m in messages if "！" in (m.content or "") or "!" in (m.content or "")) / len(messages)
        emoji_ratio = sum(1 for m in messages if m.message_type == "emoji") / len(messages)
        image_ratio = sum(1 for m in messages if m.message_type == "image") / len(messages)
        intimate_count = sum(1 for word in PersonalityAnalyzer.INTIMATE_WORDS if word in text)
        rational_count = sum(text.count(w) for w in PersonalityAnalyzer.RATIONAL_WORDS)
        neg_count = sum(text.count(w) for w in PersonalityAnalyzer.NEGATIVE_WORDS)
        short_ratio = sum(1 for m in messages if 1 <= len(m.content or "") <= 5) / len(messages)

        if intimate_count > 10:
            return "黏人撒娇型"
        if q_ratio > 0.4:
            return "刨根问底型"
        if q_ratio > 0.25 and avg_len > 30:
            return "深度探讨型"
        if emoji_ratio > 0.4:
            return "表情包狂魔"
        if emoji_ratio > 0.2 and exclam_ratio > 0.2:
            return "活泼可爱型"
        if image_ratio > 0.2:
            return "图片分享控"
        if long_msg_ratio > 0.4 and rational_count > 10:
            return "分析输出型"
        if long_msg_ratio > 0.35:
            return "絮叨倾诉型"
        if short_ratio > 0.5 and exclam_ratio < 0.1:
            return "冷淡简洁型"
        if short_ratio > 0.4 and exclam_ratio > 0.2:
            return "简短热情型"
        if exclam_ratio > 0.35:
            return "情绪外放型"
        if neg_count > len(messages) * 0.3:
            return "情绪宣泄型"
        if rational_count > 15 and avg_len > 20:
            return "理性陈述型"
        if avg_len > 40 and q_ratio > 0.15:
            return "细心关怀型"
        if intimate_count > 3 and exclam_ratio > 0.15:
            return "热情互动型"

        return "平衡互动型"

    # ---- Summary ----

    @staticmethod
    def _generate_summary(my_extro, their_extro, my_rat, their_rat,
                          my_pos, their_pos, my_dir, their_dir) -> tuple:
        """Generate detailed personality summary"""
        parts = []

        # Extroversion
        if my_extro > 65:
            parts.append("你比较外向主动，喜欢发起对话，消息量较大")
        elif my_extro < 35:
            parts.append("你相对内向被动，倾向于回应而非发起对话")
        else:
            parts.append("你的外向程度适中")

        if their_extro > 65:
            parts.append(f"对方比较外向主动，经常主动找你聊")
        elif their_extro < 35:
            parts.append(f"对方相对内向，不太主动聊天")
        else:
            parts.append(f"对方外向程度适中")

        # Rational
        diff_rat = my_rat - their_rat
        if my_rat > 65:
            parts.append("你偏向理性思考，喜欢分析问题")
        elif my_rat < 35:
            parts.append("你偏向感性，更注重情感表达")

        if abs(diff_rat) > 15:
            if diff_rat > 0:
                parts.append("相比之下你比对方更理性")
            else:
                parts.append("相比之下对方比你更理性")

        # Positive
        if my_pos > 65:
            parts.append("你整体心态积极乐观")
        elif my_pos < 35:
            parts.append("你有时表露消极情绪")

        if their_pos > 65:
            parts.append("对方也偏向积极乐观")
        elif their_pos < 35:
            parts.append("对方有时表露消极情绪")

        # Directness
        if my_dir > 65:
            parts.append("你说话直来直去，不绕弯子")
        elif my_dir < 35:
            parts.append("你说话比较委婉，会照顾对方感受")

        if abs(my_dir - their_dir) < 15:
            parts.append("双方沟通风格相近，交流顺畅")

        if not parts:
            parts.append("双方性格特征不明显，需要更多数据")

        summary = "，".join(parts)

        details = {
            "my_style_traits": PersonalityAnalyzer._trait_description(my_extro, my_rat, my_pos, my_dir),
            "their_style_traits": PersonalityAnalyzer._trait_description(their_extro, their_rat, their_pos, their_dir),
        }
        return summary, details

    @staticmethod
    def _trait_description(extro, rat, pos, direc) -> list:
        """Generate detailed trait tags across multiple dimensions"""
        tags = []

        # 外向性维度（5段）
        if extro >= 80:
            tags.append("极度外向")
        elif extro >= 65:
            tags.append("外向主动")
        elif extro >= 45:
            tags.append("张弛有度")
        elif extro >= 30:
            tags.append("内敛低调")
        else:
            tags.append("高度内向")

        # 理性/感性维度（5段）
        if rat >= 80:
            tags.append("高度理性")
        elif rat >= 65:
            tags.append("逻辑导向")
        elif rat >= 45:
            tags.append("情理兼顾")
        elif rat >= 30:
            tags.append("感性主导")
        else:
            tags.append("高度感性")

        # 情绪倾向维度（5段）
        if pos >= 80:
            tags.append("极度乐观")
        elif pos >= 65:
            tags.append("积极阳光")
        elif pos >= 45:
            tags.append("情绪稳定")
        elif pos >= 30:
            tags.append("偶尔低落")
        else:
            tags.append("情绪偏负面")

        # 表达方式维度（5段）
        if direc >= 80:
            tags.append("极度直接")
        elif direc >= 65:
            tags.append("直来直去")
        elif direc >= 45:
            tags.append("表达得体")
        elif direc >= 30:
            tags.append("委婉含蓄")
        else:
            tags.append("高度迂回")

        # 复合标签（基于多维度组合）
        if extro >= 65 and pos >= 65:
            tags.append("社交达人")
        if rat >= 65 and direc >= 65:
            tags.append("务实高效")
        if rat < 35 and pos >= 65:
            tags.append("浪漫主义")
        if extro < 35 and rat >= 65:
            tags.append("深思熟虑")
        if pos < 35 and rat < 35:
            tags.append("敏感细腻")
        if extro >= 65 and direc >= 65:
            tags.append("强势主导")
        if extro < 35 and direc < 35:
            tags.append("温和被动")
        if abs(rat - 50) < 15 and abs(pos - 50) < 15:
            tags.append("平衡型人格")

        return tags

    @staticmethod
    def _empty_result() -> dict:
        return {
            "my_extroversion_score": 50.0,
            "their_extroversion_score": 50.0,
            "my_rational_score": 50.0,
            "their_rational_score": 50.0,
            "my_positive_score": 50.0,
            "their_positive_score": 50.0,
            "my_direct_score": 50.0,
            "their_direct_score": 50.0,
            "my_interaction_style": "未知",
            "their_interaction_style": "未知",
            "summary": "数据不足，无法分析",
            "details": {},
        }
