"""Big Five personality analyzer for chat messages"""
from typing import List
from statistics import median
from collections import Counter
from app.models.message import Message


class PersonalityAnalyzer:
    """Big Five (OCEAN) personality analysis from chat behavior"""

    # ── Openness (开放性) ──────────────────────────────────────────────
    OPENNESS_WORDS = {
        "想象", "创意", "艺术", "哲学", "文化", "旅行", "探索", "发现", "新奇",
        "有趣", "奇怪", "好奇", "思考", "梦想", "灵感", "创作", "设计", "审美",
        "诗", "音乐", "电影", "书", "读书", "学习", "研究", "理解", "感悟",
        "不一样", "独特", "另类", "跨界", "尝试", "体验", "感受", "视角",
    }

    # ── Conscientiousness (尽责性) ────────────────────────────────────
    CONSCIENTIOUSNESS_WORDS = {
        "计划", "安排", "准时", "按时", "完成", "任务", "目标", "效率", "认真",
        "负责", "仔细", "检查", "确认", "提醒", "记得", "别忘", "注意", "规划",
        "步骤", "流程", "方案", "总结", "复盘", "进度", "截止", "deadline",
        "坚持", "习惯", "自律", "专注", "细心", "严格", "标准",
    }

    # ── Extraversion (外向性) ─────────────────────────────────────────
    # (computed behaviorally, not keyword-based)

    # ── Agreeableness (宜人性) ────────────────────────────────────────
    AGREEABLENESS_WORDS = {
        "谢谢": 3, "感谢": 3, "辛苦": 2, "麻烦你": 3, "不好意思": 3,
        "对不起": 3, "抱歉": 3, "没关系": 2, "好的": 1, "嗯嗯": 1,
        "明白": 1, "理解": 2, "支持": 2, "帮": 2, "帮忙": 3,
        "一起": 2, "我们": 1, "照顾": 3, "关心": 3, "在乎": 3,
        "体谅": 3, "包容": 3, "温柔": 2, "善良": 2, "贴心": 3,
        "放心": 2, "别担心": 3, "没事": 1, "加油": 2, "鼓励": 2,
    }
    DISAGREEABLENESS_WORDS = {
        "烦": 2, "讨厌": 3, "滚": 4, "闭嘴": 4, "无语": 2,
        "傻": 2, "蠢": 3, "废物": 4, "没用": 3, "算了": 1,
        "随便": 1, "不管": 1, "懒得": 2, "不想": 1, "不理": 2,
    }

    # ── Neuroticism (神经质) ──────────────────────────────────────────
    NEUROTICISM_WORDS = {
        "焦虑": 4, "担心": 3, "害怕": 3, "恐惧": 4, "紧张": 3,
        "压力": 3, "崩溃": 4, "绝望": 4, "后悔": 3, "自责": 4,
        "失眠": 3, "难受": 3, "痛苦": 4, "心慌": 3, "不安": 3,
        "烦躁": 3, "抑郁": 4, "委屈": 3, "心疼": 2, "难过": 3,
        "伤心": 3, "哭": 2, "泪": 2, "怎么办": 2, "完了": 3,
        "糟糕": 3, "惨": 3, "倒霉": 2, "不行了": 3, "受不了": 3,
    }
    STABILITY_WORDS = {
        "没事": 2, "放心": 2, "稳": 2, "冷静": 3, "淡定": 3,
        "无所谓": 2, "随缘": 2, "看开": 3, "想开了": 3, "平静": 3,
    }

    # ── Interaction style ─────────────────────────────────────────────
    INTIMATE_WORDS = {
        "宝贝", "宝宝", "亲爱的", "老公", "老婆", "想你了", "爱你",
        "么么", "抱抱", "亲", "想你", "在一起", "永远", "乖乖",
    }

    @staticmethod
    def analyze(messages: List[Message]) -> dict:
        if not messages:
            return PersonalityAnalyzer._empty_result()

        sorted_msgs = sorted(messages, key=lambda m: m.timestamp)
        my_msgs = [m for m in sorted_msgs if m.is_from_me]
        their_msgs = [m for m in sorted_msgs if not m.is_from_me]

        if not my_msgs or not their_msgs:
            return PersonalityAnalyzer._empty_result()

        # Big Five scores (0-100)
        my_O = PersonalityAnalyzer._calc_openness(my_msgs)
        their_O = PersonalityAnalyzer._calc_openness(their_msgs)

        my_C = PersonalityAnalyzer._calc_conscientiousness(my_msgs, sorted_msgs)
        their_C = PersonalityAnalyzer._calc_conscientiousness(their_msgs, sorted_msgs)

        my_E = PersonalityAnalyzer._calc_extraversion(my_msgs, their_msgs, sorted_msgs)
        their_E = PersonalityAnalyzer._calc_extraversion(their_msgs, my_msgs, sorted_msgs)

        my_A = PersonalityAnalyzer._calc_agreeableness(my_msgs)
        their_A = PersonalityAnalyzer._calc_agreeableness(their_msgs)

        my_N = PersonalityAnalyzer._calc_neuroticism(my_msgs)
        their_N = PersonalityAnalyzer._calc_neuroticism(their_msgs)

        my_style = PersonalityAnalyzer._get_interaction_style(my_msgs, sorted_msgs)
        their_style = PersonalityAnalyzer._get_interaction_style(their_msgs, sorted_msgs)

        summary = PersonalityAnalyzer._generate_summary(
            my_O, my_C, my_E, my_A, my_N,
            their_O, their_C, their_E, their_A, their_N
        )

        return {
            # Legacy fields (kept for frontend compatibility)
            "my_extroversion_score": round(my_E, 1),
            "their_extroversion_score": round(their_E, 1),
            "my_rational_score": round(my_C, 1),
            "their_rational_score": round(their_C, 1),
            "my_positive_score": round(my_A, 1),
            "their_positive_score": round(their_A, 1),
            "my_direct_score": round(100 - my_N, 1),
            "their_direct_score": round(100 - their_N, 1),
            # Big Five fields
            "my_openness": round(my_O, 1),
            "their_openness": round(their_O, 1),
            "my_conscientiousness": round(my_C, 1),
            "their_conscientiousness": round(their_C, 1),
            "my_extraversion": round(my_E, 1),
            "their_extraversion": round(their_E, 1),
            "my_agreeableness": round(my_A, 1),
            "their_agreeableness": round(their_A, 1),
            "my_neuroticism": round(my_N, 1),
            "their_neuroticism": round(their_N, 1),
            "my_interaction_style": my_style,
            "their_interaction_style": their_style,
            "summary": summary,
            "details": {
                "my_style_traits": PersonalityAnalyzer._trait_tags(my_O, my_C, my_E, my_A, my_N),
                "their_style_traits": PersonalityAnalyzer._trait_tags(their_O, their_C, their_E, their_A, their_N),
            },
        }

    # ── O: Openness ───────────────────────────────────────────────────

    @staticmethod
    def _calc_openness(msgs: List[Message]) -> float:
        if not msgs:
            return 50.0
        text = " ".join(m.content or "" for m in msgs)
        # 1) Openness keyword density
        kw_count = sum(text.count(w) for w in PersonalityAnalyzer.OPENNESS_WORDS)
        kw_score = min(kw_count / len(msgs) * 50, 100)
        # 2) Vocabulary richness (unique chars / total chars)
        chars = [c for m in msgs for c in (m.content or "") if '一' <= c <= '鿿']
        richness = len(set(chars)) / len(chars) * 100 if chars else 50
        # 3) Avg message length (longer = more expressive)
        avg_len = sum(len(m.content or "") for m in msgs) / len(msgs)
        len_score = min(avg_len / 80 * 100, 100)
        return min(95, max(5, kw_score * 0.5 + richness * 0.3 + len_score * 0.2))

    # ── C: Conscientiousness ──────────────────────────────────────────

    @staticmethod
    def _calc_conscientiousness(msgs: List[Message], all_msgs: List[Message]) -> float:
        if not msgs:
            return 50.0
        text = " ".join(m.content or "" for m in msgs)
        # 1) Conscientiousness keywords
        kw_count = sum(text.count(w) for w in PersonalityAnalyzer.CONSCIENTIOUSNESS_WORDS)
        kw_score = min(kw_count / len(msgs) * 60, 100)
        # 2) Response consistency (low variance in response time = conscientious)
        gaps = []
        for i in range(1, len(all_msgs)):
            curr, prev = all_msgs[i], all_msgs[i - 1]
            if curr.is_from_me == msgs[0].is_from_me and curr.is_from_me != prev.is_from_me:
                gap = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < gap < 1440:
                    gaps.append(gap)
        if len(gaps) >= 3:
            from statistics import stdev
            consistency = max(0, 100 - min(stdev(gaps) / 60 * 100, 100))
        else:
            consistency = 50.0
        # 3) Punctuation usage (conscientious people use proper punctuation)
        punct_count = sum(
            1 for m in msgs
            if any(p in (m.content or "") for p in ["。", "，", "！", "？", "、"])
        )
        punct_score = punct_count / len(msgs) * 100
        return min(95, max(5, kw_score * 0.4 + consistency * 0.4 + punct_score * 0.2))

    # ── E: Extraversion ───────────────────────────────────────────────

    @staticmethod
    def _calc_extraversion(me: List[Message], other: List[Message], all_msgs: List[Message]) -> float:
        if not all_msgs or not me:
            return 50.0
        # 1) Message volume ratio (30%)
        vol_score = min(len(me) / len(all_msgs) * 150, 100)
        # 2) Conversation initiation (30%)
        my_starts = total_starts = 0
        for i in range(1, len(all_msgs)):
            gap = (all_msgs[i].timestamp - all_msgs[i - 1].timestamp).total_seconds() / 3600
            if gap > 2:
                total_starts += 1
                if all_msgs[i].is_from_me == me[0].is_from_me:
                    my_starts += 1
        init_score = (my_starts / total_starts * 100) if total_starts > 0 else 50.0
        # 3) Energy markers: !, emoji (20%)
        energy = sum(
            1 for m in me
            if "！" in (m.content or "") or "!" in (m.content or "")
        ) / len(me) * 100
        energy_score = min(energy * 2, 100)
        # 4) Response speed (20%)
        gaps = []
        for i in range(1, len(all_msgs)):
            curr, prev = all_msgs[i], all_msgs[i - 1]
            if curr.is_from_me == me[0].is_from_me and curr.is_from_me != prev.is_from_me:
                gap = (curr.timestamp - prev.timestamp).total_seconds() / 60
                if 0 < gap < 1440:
                    gaps.append(gap)
        speed_score = max(0, min(100, 100 - (median(gaps) / 120 * 100))) if gaps else 50.0
        return min(95, max(5,
            vol_score * 0.30 + init_score * 0.30 +
            energy_score * 0.20 + speed_score * 0.20
        ))

    # ── A: Agreeableness ──────────────────────────────────────────────

    @staticmethod
    def _calc_agreeableness(msgs: List[Message]) -> float:
        if not msgs:
            return 50.0
        text = " ".join(m.content or "" for m in msgs)
        agree = sum(text.count(w) * wt for w, wt in PersonalityAnalyzer.AGREEABLENESS_WORDS.items())
        disagree = sum(text.count(w) * wt for w, wt in PersonalityAnalyzer.DISAGREEABLENESS_WORDS.items())
        total = agree + disagree
        if total == 0:
            base = 50.0
        else:
            base = agree / total * 100
        # Bonus: intimate words
        intimate = sum(1 for w in PersonalityAnalyzer.INTIMATE_WORDS if w in text)
        bonus = min(intimate * 3, 15)
        return min(95, max(5, base * 0.85 + bonus))

    # ── N: Neuroticism ────────────────────────────────────────────────

    @staticmethod
    def _calc_neuroticism(msgs: List[Message]) -> float:
        if not msgs:
            return 50.0
        text = " ".join(m.content or "" for m in msgs)
        neuro = sum(text.count(w) * wt for w, wt in PersonalityAnalyzer.NEUROTICISM_WORDS.items())
        stable = sum(text.count(w) * wt for w, wt in PersonalityAnalyzer.STABILITY_WORDS.items())
        total = neuro + stable
        if total == 0:
            return 30.0  # Default: slightly stable
        return min(95, max(5, neuro / total * 100))

    # ── Interaction style ─────────────────────────────────────────────

    @staticmethod
    def _get_interaction_style(msgs: List[Message], all_msgs: List[Message]) -> str:
        if not msgs:
            return "未知"
        text = " ".join(m.content or "" for m in msgs)
        q_ratio = sum(1 for m in msgs if "？" in (m.content or "") or "?" in (m.content or "")) / len(msgs)
        avg_len = sum(len(m.content or "") for m in msgs) / len(msgs)
        long_ratio = sum(1 for m in msgs if len(m.content or "") > 50) / len(msgs)
        exclam_ratio = sum(1 for m in msgs if "！" in (m.content or "") or "!" in (m.content or "")) / len(msgs)
        emoji_ratio = sum(1 for m in msgs if m.message_type == "emoji") / len(msgs)
        image_ratio = sum(1 for m in msgs if m.message_type == "image") / len(msgs)
        intimate = sum(1 for w in PersonalityAnalyzer.INTIMATE_WORDS if w in text)
        neuro_kw = sum(text.count(w) for w in PersonalityAnalyzer.NEUROTICISM_WORDS)
        short_ratio = sum(1 for m in msgs if 1 <= len(m.content or "") <= 5) / len(msgs)
        conscientious_kw = sum(text.count(w) for w in PersonalityAnalyzer.CONSCIENTIOUSNESS_WORDS)

        if intimate > 10:
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
        if long_ratio > 0.4 and conscientious_kw > 5:
            return "条理输出型"
        if long_ratio > 0.35:
            return "絮叨倾诉型"
        if short_ratio > 0.5 and exclam_ratio < 0.1:
            return "冷淡简洁型"
        if short_ratio > 0.4 and exclam_ratio > 0.2:
            return "简短热情型"
        if exclam_ratio > 0.35:
            return "情绪外放型"
        if neuro_kw > len(msgs) * 0.3:
            return "情绪宣泄型"
        if avg_len > 40 and q_ratio > 0.15:
            return "细心关怀型"
        if intimate > 3 and exclam_ratio > 0.15:
            return "热情互动型"
        return "平衡互动型"

    # ── Trait tags ────────────────────────────────────────────────────

    @staticmethod
    def _trait_tags(O, C, E, A, N) -> list:
        tags = []

        # O: Openness
        if O >= 70:   tags.append("思维开放")
        elif O >= 50: tags.append("乐于探索")
        else:         tags.append("务实传统")

        # C: Conscientiousness
        if C >= 75:   tags.append("高度自律")
        elif C >= 55: tags.append("认真负责")
        elif C >= 35: tags.append("随性自在")
        else:         tags.append("自由散漫")

        # E: Extraversion
        if E >= 75:   tags.append("极度外向")
        elif E >= 55: tags.append("活跃主动")
        elif E >= 35: tags.append("内外兼顾")
        else:         tags.append("内敛沉静")

        # A: Agreeableness
        if A >= 75:   tags.append("温暖体贴")
        elif A >= 55: tags.append("友善合作")
        elif A >= 35: tags.append("独立自主")
        else:         tags.append("直率强势")

        # N: Neuroticism (inverted: low N = stable)
        if N <= 25:   tags.append("情绪稳定")
        elif N <= 45: tags.append("偶有波动")
        elif N <= 65: tags.append("情感细腻")
        else:         tags.append("情绪敏感")

        # Composite tags based on Big Five combinations
        if E >= 60 and A >= 60:   tags.append("社交达人")
        if C >= 65 and N <= 35:   tags.append("稳健可靠")
        if O >= 65 and E >= 60:   tags.append("创意活跃")
        if O >= 65 and N >= 55:   tags.append("感性艺术")
        if C >= 65 and A >= 65:   tags.append("成熟稳重")
        if E <= 35 and O >= 65:   tags.append("深思熟虑")
        if A >= 70 and N >= 55:   tags.append("共情能力强")
        if C >= 70 and E >= 65:   tags.append("目标导向")
        if N <= 25 and A >= 65:   tags.append("平和包容")
        if E <= 30 and N <= 30:   tags.append("冷静理智")

        return tags

    # ── Summary ───────────────────────────────────────────────────────

    @staticmethod
    def _generate_summary(my_O, my_C, my_E, my_A, my_N,
                          their_O, their_C, their_E, their_A, their_N) -> str:
        parts = []

        # E
        if my_E >= 65:
            parts.append("你外向主动，喜欢发起对话")
        elif my_E <= 35:
            parts.append("你偏内向，倾向于回应而非主动")

        if their_E >= 65:
            parts.append("对方外向活跃，经常主动联系")
        elif their_E <= 35:
            parts.append("对方较为内敛，不太主动")

        # O
        if my_O >= 65:
            parts.append("你思维开放，话题多样")
        if their_O >= 65:
            parts.append("对方思维活跃，善于表达")

        # C
        if my_C >= 65:
            parts.append("你做事认真有条理")
        if their_C >= 65:
            parts.append("对方回复及时、有责任感")

        # A
        if my_A >= 65:
            parts.append("你温和友善，善于照顾对方感受")
        elif my_A <= 35:
            parts.append("你表达直接，不太在意措辞")

        # N
        if my_N >= 65:
            parts.append("你情感细腻，容易受情绪影响")
        elif my_N <= 25:
            parts.append("你情绪稳定，不易受外界干扰")

        # Compatibility
        e_diff = abs(my_E - their_E)
        a_diff = abs(my_A - their_A)
        if e_diff < 20 and a_diff < 20:
            parts.append("双方性格相近，沟通顺畅")
        elif e_diff > 40:
            parts.append("双方外向程度差异较大，沟通节奏可能不同步")

        return "，".join(parts) if parts else "数据不足，无法生成完整分析"

    # ── Empty result ──────────────────────────────────────────────────

    @staticmethod
    def _empty_result() -> dict:
        base = {k: 50.0 for k in [
            "my_extroversion_score", "their_extroversion_score",
            "my_rational_score", "their_rational_score",
            "my_positive_score", "their_positive_score",
            "my_direct_score", "their_direct_score",
            "my_openness", "their_openness",
            "my_conscientiousness", "their_conscientiousness",
            "my_extraversion", "their_extraversion",
            "my_agreeableness", "their_agreeableness",
            "my_neuroticism", "their_neuroticism",
        ]}
        base.update({
            "my_interaction_style": "未知",
            "their_interaction_style": "未知",
            "summary": "数据不足，无法分析",
            "details": {},
        })
        return base
