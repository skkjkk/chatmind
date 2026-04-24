"""Analyzer services initialization"""
from app.services.analyzer.stats import StatsAnalyzer
from app.services.analyzer.personality import PersonalityAnalyzer
from app.services.analyzer.relation import RelationAnalyzer

__all__ = ["StatsAnalyzer", "PersonalityAnalyzer", "RelationAnalyzer"]