"""JSON chat record parser"""
import json
from datetime import datetime
from app.services.parser.base_parser import BaseParser, ParsedMessage


class JsonParser(BaseParser):
    """Parser for JSON format chat records"""

    FORMATS = ["json"]

    @staticmethod
    def parse(content: str) -> tuple[list[ParsedMessage], str]:
        """
        Parse JSON chat export file. Supports:
          - Array of message objects
          - Object with messages array field
          - Object with records/reports array field
        """
        try:
            data = json.loads(content)

            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = (data.get("messages") or data.get("records")
                         or data.get("chat") or data.get("data")
                         or data.get("list") or [])
                if isinstance(items, dict):
                    items = [items]
            else:
                return [], "failed"

            messages = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                msg = JsonParser._parse_item(item)
                if msg:
                    messages.append(msg)

            if messages:
                return messages, "success"
            return [], "failed"
        except (json.JSONDecodeError, Exception):
            return [], "failed"

    @staticmethod
    def _parse_item(item: dict) -> ParsedMessage | None:
        """Parse a single JSON message object"""
        # Extract sender - try common field names
        sender = (item.get("sender") or item.get("from") or item.get("fromUser")
                  or item.get("from_user") or item.get("name") or item.get("speaker")
                  or "Unknown")

        # Extract content - try common field names
        content = (item.get("content") or item.get("text") or item.get("message")
                   or item.get("msg") or item.get("body") or "")

        # Extract timestamp - try common field names
        ts = (item.get("timestamp") or item.get("time") or item.get("date")
              or item.get("createTime") or item.get("create_time") or item.get("datetime"))

        # Parse timestamp
        timestamp = None
        if ts:
            if isinstance(ts, (int, float)):
                if ts > 1e10:
                    timestamp = datetime.fromtimestamp(ts / 1000)
                else:
                    timestamp = datetime.fromtimestamp(ts)
            elif isinstance(ts, str):
                timestamp = JsonParser.parse_timestamp(ts)

        if not timestamp:
            return None

        # Extract message type
        msg_type = item.get("message_type") or item.get("type") or item.get("msgType") or item.get("msg_type")
        if msg_type and isinstance(msg_type, str) and msg_type.lower() in ["text", "image", "voice", "emoji", "file"]:
            message_type = msg_type.lower()
        else:
            message_type = JsonParser.detect_message_type(content)

        # Determine direction
        is_from_me = item.get("is_from_me") or item.get("isFromMe") or item.get("direction") == "send"
        if isinstance(is_from_me, str):
            is_from_me = is_from_me.lower() in ("true", "1", "yes")

        return ParsedMessage(
            sender=str(sender),
            content=str(content),
            timestamp=timestamp,
            message_type=message_type,
            is_from_me=bool(is_from_me)
        )
