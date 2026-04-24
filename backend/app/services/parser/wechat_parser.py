"""WeChat chat record parser (HTML format)"""
import re
from typing import Optional
from bs4 import BeautifulSoup
from app.services.parser.base_parser import BaseParser, ParsedMessage


class WechatParser(BaseParser):
    """Parser for WeChat chat export files (HTML format)"""

    @staticmethod
    def parse_html(html_content: str) -> tuple[list[ParsedMessage], str]:
        """
        Parse WeChat HTML export file
        Returns: (list of ParsedMessage, status)
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []

            # Method 1: div-based structure
            chat_area = soup.find('div', class_='chat') or soup.find('div', class_='chat-area')
            if chat_area:
                message_elements = chat_area.find_all('div', class_='message')
            else:
                message_elements = soup.find_all('div', class_=re.compile(r'message|msg'))

            for elem in message_elements:
                try:
                    msg = WechatParser._parse_message_element(elem)
                    if msg:
                        messages.append(msg)
                except Exception:
                    continue

            if messages:
                return messages, "success"

            # Method 2: table-based structure
            rows = soup.find_all('tr')
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        sender = cells[0].get_text(strip=True)
                        content_text = cells[1].get_text(strip=True)
                        time_str = cells[2].get_text(strip=True)
                        timestamp = WechatParser.parse_timestamp(time_str)
                        if timestamp and (sender or content_text):
                            is_from_me = "我" in sender or "You" in sender or "me" in sender.lower()
                            sender = sender.replace("我", "").replace("You", "").strip() or "Unknown"
                            msg = ParsedMessage(
                                sender=sender,
                                content=content_text,
                                timestamp=timestamp,
                                message_type=WechatParser.detect_message_type(content_text),
                                is_from_me=is_from_me
                            )
                            messages.append(msg)
                except Exception:
                    continue

            if messages:
                return messages, "success"

            return [], "failed"
        except Exception:
            return [], "failed"

    @staticmethod
    def _parse_message_element(element) -> Optional[ParsedMessage]:
        """Parse a single message element"""
        sender_elem = element.find('span', class_='sender') or element.find('div', class_='sender')
        sender = sender_elem.get_text(strip=True) if sender_elem else "Unknown"

        content_elem = element.find('div', class_='content') or element.find('p', class_='content')
        content_text = content_elem.get_text(strip=True) if content_elem else ""

        time_elem = element.find('div', class_='time') or element.find('span', class_='time')
        time_str = time_elem.get_text(strip=True) if time_elem else ""
        timestamp = WechatParser.parse_timestamp(time_str)

        if not timestamp:
            return None

        is_from_me = "我" in sender or "You" in sender

        return ParsedMessage(
            sender=sender.replace("我", "").replace("You", "").strip() or "Unknown",
            content=content_text,
            timestamp=timestamp,
            message_type=WechatParser.detect_message_type(content_text),
            is_from_me=is_from_me
        )
