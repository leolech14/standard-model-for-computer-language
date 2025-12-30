"""
Conversation Parser
===================

Parses chat transcripts into exchanges.
"""

from pathlib import Path
from typing import List, Dict


class ConversationParser:
    """Parses conversation transcripts into exchanges."""

    def parse_files(self, files: List[Path]) -> List[Dict]:
        """Parse all files into ordered exchanges."""
        all_exchanges = []

        for file_path in files:
            content = file_path.read_text()
            lines = content.split('\n')

            current_type = None
            current_content = []
            current_start = 0

            for i, line in enumerate(lines):
                if line.startswith('### User Input'):
                    if current_type and current_content:
                        all_exchanges.append({
                            'type': current_type,
                            'content': '\n'.join(current_content),
                            'start_line': current_start,
                            'end_line': i,
                            'source': file_path.stem,
                        })
                    current_type = 'user'
                    current_content = []
                    current_start = i
                elif line.startswith('### Planner Response'):
                    if current_type and current_content:
                        all_exchanges.append({
                            'type': current_type,
                            'content': '\n'.join(current_content),
                            'start_line': current_start,
                            'end_line': i,
                            'source': file_path.stem,
                        })
                    current_type = 'ai'
                    current_content = []
                    current_start = i
                elif current_type:
                    current_content.append(line)

            # Last segment
            if current_type and current_content:
                all_exchanges.append({
                    'type': current_type,
                    'content': '\n'.join(current_content),
                    'start_line': current_start,
                    'end_line': len(lines),
                    'source': file_path.stem,
                })

        # Deduplicate
        return self._deduplicate(all_exchanges)

    def _deduplicate(self, exchanges: List[Dict]) -> List[Dict]:
        """Remove duplicate exchanges based on content."""
        seen_content = set()
        unique = []

        for ex in exchanges:
            content_key = ex['content'][:200].strip()
            if content_key and content_key not in seen_content:
                seen_content.add(content_key)
                unique.append(ex)

        return unique

    def pair_exchanges(self, exchanges: List[Dict]) -> List[Dict]:
        """Pair user-AI exchanges."""
        pairs = []
        i = 0

        while i < len(exchanges):
            user_ex = exchanges[i] if exchanges[i]['type'] == 'user' else None
            ai_ex = exchanges[i + 1] if i + 1 < len(exchanges) and exchanges[i + 1]['type'] == 'ai' else None

            if user_ex:
                pairs.append({
                    'user': user_ex,
                    'ai': ai_ex,
                    'index': len(pairs)
                })
                i += 2 if ai_ex else 1
            else:
                i += 1

        return pairs
