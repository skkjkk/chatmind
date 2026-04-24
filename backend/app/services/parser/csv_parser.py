"""CSV / Excel chat record parser"""
import csv
import io
from datetime import datetime
from app.services.parser.base_parser import BaseParser, ParsedMessage


class CsvParser(BaseParser):
    """Parser for CSV format chat records"""

    @staticmethod
    def parse(content: str) -> tuple[list[ParsedMessage], str]:
        """
        Parse CSV chat export file.
        Expected columns (by header): sender, content, timestamp, message_type, is_from_me
        Also auto-detects common column name variants.
        """
        try:
            reader = csv.DictReader(io.StringIO(content))
            if not reader.fieldnames:
                # Try parsing without header
                return CsvParser._parse_no_header(content)

            messages = []
            for row in reader:
                msg = CsvParser._parse_row(row)
                if msg:
                    messages.append(msg)

            if messages:
                return messages, "success"

            # Fallback to no-header parse
            return CsvParser._parse_no_header(content)

        except Exception:
            return [], "failed"

    @staticmethod
    def _parse_no_header(content: str) -> tuple[list[ParsedMessage], str]:
        """Parse CSV without header row"""
        try:
            reader = csv.reader(io.StringIO(content))
            messages = []
            for row in reader:
                if len(row) < 3:
                    continue
                sender = row[0].strip()
                content_text = row[1].strip()
                ts_str = row[2].strip() if len(row) > 2 else ""

                timestamp = CsvParser.parse_timestamp(ts_str)
                if not timestamp:
                    continue

                is_from_me = False
                if len(row) > 4:
                    is_from_me = row[4].strip().lower() in ("true", "1", "yes")

                messages.append(ParsedMessage(
                    sender=sender,
                    content=content_text,
                    timestamp=timestamp,
                    message_type=CsvParser.detect_message_type(content_text),
                    is_from_me=is_from_me
                ))

            if messages:
                return messages, "success"
            return [], "failed"
        except Exception:
            return [], "failed"

    @staticmethod
    def _parse_row(row: dict) -> ParsedMessage | None:
        """Parse a single CSV row"""
        # Find sender column
        sender = CsvParser._get_value(row, "sender", "from", "from_user", "fromuser", "name", "speaker", "who")
        if not sender:
            return None

        # Find content column
        content = CsvParser._get_value(row, "content", "text", "message", "msg", "body")

        # Find timestamp column
        ts_str = CsvParser._get_value(row, "timestamp", "time", "date", "datetime", "create_time", "createtime")

        timestamp = CsvParser.parse_timestamp(ts_str) if ts_str else None
        if not timestamp:
            return None

        # Find message type column
        msg_type = CsvParser._get_value(row, "message_type", "type", "msg_type", "msgtype")

        if msg_type and msg_type.lower() in ("text", "image", "voice", "emoji", "file", "video"):
            message_type = msg_type.lower()
        else:
            message_type = CsvParser.detect_message_type(content or "")

        # Find is_from_me column
        is_from_me_str = CsvParser._get_value(row, "is_from_me", "is_from_me", "from_me",
                                                 "direction", "isFromMe", "fromMe", "send")
        is_from_me = is_from_me_str.lower() in ("true", "1", "yes", "send", "me") if is_from_me_str else False

        return ParsedMessage(
            sender=sender,
            content=content or "",
            timestamp=timestamp,
            message_type=message_type,
            is_from_me=is_from_me
        )

    @staticmethod
    def _get_value(row: dict, *keys: str) -> str | None:
        """Get first matching value from row dict (case-insensitive)"""
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        for key in keys:
            if key.lower() in row_lower:
                return row_lower[key.lower()].strip()
        return None
