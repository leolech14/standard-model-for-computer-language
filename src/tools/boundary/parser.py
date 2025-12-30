"""
Message Parser
==============

Parses conversation transcripts into structured messages.
"""

from pathlib import Path
from typing import List

from .models import Message
from .classifier import MessageClassifier


class MessageParser:
    """Parses conversation transcripts into messages."""

    def __init__(self):
        self.classifier = MessageClassifier()

    def parse_files(self, files: List[Path]) -> List[Message]:
        """Parse all files into individual messages."""
        messages = []
        msg_index = 0

        for file_path in files:
            content = file_path.read_text()
            lines = content.split('\n')

            current_type = None
            current_content = []
            current_start = 0

            for i, line in enumerate(lines):
                if line.startswith('### User Input'):
                    if current_type and current_content:
                        msg = self._create_message(
                            msg_index, current_type,
                            '\n'.join(current_content),
                            current_start, i
                        )
                        messages.append(msg)
                        msg_index += 1
                    current_type = 'user'
                    current_content = []
                    current_start = i
                elif line.startswith('### Planner Response'):
                    if current_type and current_content:
                        msg = self._create_message(
                            msg_index, current_type,
                            '\n'.join(current_content),
                            current_start, i
                        )
                        messages.append(msg)
                        msg_index += 1
                    current_type = 'ai'
                    current_content = []
                    current_start = i
                elif current_type:
                    current_content.append(line)

            # Last message
            if current_type and current_content:
                msg = self._create_message(
                    msg_index, current_type,
                    '\n'.join(current_content),
                    current_start, len(lines)
                )
                messages.append(msg)
                msg_index += 1

        # Deduplicate
        return self._deduplicate(messages)

    def _create_message(
        self,
        index: int,
        msg_type: str,
        content: str,
        start: int,
        end: int
    ) -> Message:
        """Create a fully classified message."""
        # Clean content
        clean_content = content
        if '*User accepted' in clean_content:
            clean_content = clean_content.split('*User accepted')[0].strip()

        # Get first meaningful line
        first_line = ""
        for line in clean_content.split('\n'):
            line = line.strip()
            if line and len(line) > 5 and not line.startswith('```'):
                first_line = line[:100]
                break

        msg = Message(
            index=index,
            type=msg_type,
            content=clean_content,
            line_start=start,
            line_end=end,
            first_line=first_line,
            word_count=len(clean_content.split()),
            has_code='```' in content,
            has_question='?' in clean_content
        )

        # Only classify user messages
        if msg_type == 'user':
            msg.interaction_type = self.classifier.detect_interaction_type(clean_content)
            msg.purpose = self.classifier.detect_purpose(clean_content)
            msg.ideas = self.classifier.extract_ideas(clean_content)
            msg.intensity = self.classifier.calculate_intensity(clean_content)

        return msg

    def _deduplicate(self, messages: List[Message]) -> List[Message]:
        """Remove duplicate messages based on content."""
        seen = set()
        unique = []
        for msg in messages:
            key = msg.content[:200].strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(msg)
        return unique
