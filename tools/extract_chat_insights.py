#!/usr/bin/env python3
"""
Extract summarized insights from large chat transcript markdown files.

Usage:
    python tools/extract_chat_insights.py /path/to/chat.md
    python tools/extract_chat_insights.py /path/to/chat.md --output summary.md
    python tools/extract_chat_insights.py /path/to/chat.md --mode decisions
    python tools/extract_chat_insights.py /path/to/chat.md --mode user-inputs
    python tools/extract_chat_insights.py /path/to/chat.md --mode all
"""

import argparse
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class ChatSection:
    """A section from the chat transcript."""
    section_type: str  # 'user_input', 'planner_response', 'code', 'heading'
    content: str
    line_number: int
    importance: int = 0  # 0-10 scale


@dataclass
class Insight:
    """An extracted insight or decision."""
    category: str
    content: str
    context: str
    line_number: int


class ChatExtractor:
    """Extract insights from chat transcript markdown files."""

    # Patterns that indicate important content
    IMPORTANCE_PATTERNS = [
        (r'\b(key|critical|important|must|essential)\b', 5, 'priority'),
        (r'\b(decision|decided|chose|choice)\b', 4, 'decision'),
        (r'\b(discovery|discovered|found|realized)\b', 4, 'discovery'),
        (r'\b(problem|issue|bug|error|fix)\b', 3, 'problem'),
        (r'\b(solution|solved|resolved|fixed)\b', 3, 'solution'),
        (r'\b(insight|learned|understand)\b', 3, 'insight'),
        (r'\b(todo|task|next|action)\b', 2, 'action'),
        (r'\b(summary|conclusion|result)\b', 4, 'summary'),
        (r'\b(why|because|reason|rationale)\b', 2, 'rationale'),
        (r'\*\*[^*]+\*\*', 1, 'emphasis'),  # Bold text
        (r'[A-Z]{3,}', 2, 'caps'),  # ALL CAPS words indicate emphasis/urgency
        (r'[!?]{2,}', 3, 'emphasis'),  # Multiple !!! or ??? indicates strong feeling
    ]

    # Section markers
    SECTION_PATTERNS = {
        'user_input': r'^### User Input',
        'planner_response': r'^### Planner Response',
        'heading': r'^#{1,3} ',
        'code_block': r'^```',
        'bullet': r'^\s*[-*]\s',
        'numbered': r'^\s*\d+\.\s',
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.sections: List[ChatSection] = []
        self.insights: List[Insight] = []

    def parse_sections(self) -> List[ChatSection]:
        """Parse the file into sections."""
        sections = []
        current_section = None
        current_content = []
        current_line = 0
        in_code_block = False

        for i, line in enumerate(self.lines):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block

            # Check for section markers
            if not in_code_block:
                if re.match(self.SECTION_PATTERNS['user_input'], line):
                    if current_section:
                        sections.append(ChatSection(
                            section_type=current_section,
                            content='\n'.join(current_content).strip(),
                            line_number=current_line
                        ))
                    current_section = 'user_input'
                    current_content = []
                    current_line = i + 1
                    continue

                elif re.match(self.SECTION_PATTERNS['planner_response'], line):
                    if current_section:
                        sections.append(ChatSection(
                            section_type=current_section,
                            content='\n'.join(current_content).strip(),
                            line_number=current_line
                        ))
                    current_section = 'planner_response'
                    current_content = []
                    current_line = i + 1
                    continue

                elif re.match(r'^#{1,2} [A-Z]', line) and not current_section:
                    # Top-level heading outside of sections
                    if current_section:
                        sections.append(ChatSection(
                            section_type=current_section,
                            content='\n'.join(current_content).strip(),
                            line_number=current_line
                        ))
                    current_section = 'heading'
                    current_content = [line]
                    current_line = i + 1
                    continue

            if current_section:
                current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            sections.append(ChatSection(
                section_type=current_section,
                content='\n'.join(current_content).strip(),
                line_number=current_line
            ))

        # Score importance
        for section in sections:
            section.importance = self._score_importance(section.content)

        self.sections = sections
        return sections

    def _score_importance(self, text: str) -> int:
        """Score the importance of a text block."""
        score = 0
        text_lower = text.lower()

        for pattern, weight, _ in self.IMPORTANCE_PATTERNS:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            score += matches * weight

        # Boost for longer substantive content
        word_count = len(text.split())
        if 50 < word_count < 500:
            score += 2
        elif word_count >= 500:
            score += 1  # Very long might be code dumps

        return min(score, 10)

    def extract_user_inputs(self, min_length: int = 20) -> List[Dict]:
        """Extract all user inputs with context."""
        if not self.sections:
            self.parse_sections()

        inputs = []
        for section in self.sections:
            if section.section_type == 'user_input':
                content = section.content.strip()

                # CLEAN: Remove command acceptance noise
                # Pattern: user question, then "*User accepted the command..."
                if '*User accepted' in content:
                    content = content.split('*User accepted')[0].strip()

                # Also strip from first code block if question is before it
                if '\n```' in content:
                    parts = content.split('\n```')
                    if len(parts[0].strip()) >= min_length:
                        content = parts[0].strip()

                # Skip very short or system messages
                if len(content) >= min_length and 'system-generated' not in content.lower():
                    inputs.append({
                        'line': section.line_number,
                        'content': content[:500] + ('...' if len(content) > 500 else ''),
                        'importance': section.importance,
                        'full_content': content
                    })

        return sorted(inputs, key=lambda x: -x['importance'])

    def extract_decisions(self) -> List[Insight]:
        """Extract decisions and their rationale."""
        if not self.sections:
            self.parse_sections()

        decisions = []

        # Look for explicit decision markers in content
        for section in self.sections:
            text = section.content

            # Method 1: Look for bullet points with action verbs
            bullet_pattern = r'[-*]\s*\*\*([^*]+)\*\*[:\s]*(.+?)(?=\n[-*]|\n\n|$)'
            for match in re.finditer(bullet_pattern, text, re.DOTALL):
                title = match.group(1).strip()
                detail = match.group(2).strip()[:150]
                if len(title) > 5:
                    decisions.append(Insight(
                        category='decision',
                        content=f"{title}: {detail}",
                        context=section.section_type,
                        line_number=section.line_number
                    ))

            # Method 2: Look for "We will/should/must" statements
            action_pattern = r'(?:we|I)\s+(?:will|should|must|need to)\s+([^.!?\n]{20,150})[.!?]'
            for match in re.finditer(action_pattern, text, re.IGNORECASE):
                content = match.group(1).strip()
                decisions.append(Insight(
                    category='decision',
                    content=content,
                    context=section.section_type,
                    line_number=section.line_number
                ))

            # Method 3: Look for explicit "Decision:" markers
            explicit_pattern = r'(?:decision|decided|choosing)[:\s]+([^.!?\n]{15,200})[.!?\n]'
            for match in re.finditer(explicit_pattern, text, re.IGNORECASE):
                content = match.group(1).strip()
                if not content.startswith(('that', 'to ', 'the ')):  # Skip fragments
                    decisions.append(Insight(
                        category='decision',
                        content=content,
                        context=section.section_type,
                        line_number=section.line_number
                    ))

            # Method 4: Look for table rows with decisions (| Decision | ... |)
            table_pattern = r'\|\s*\*\*([^|*]+)\*\*\s*\|([^|]+)\|'
            for match in re.finditer(table_pattern, text):
                key = match.group(1).strip()
                val = match.group(2).strip()
                if len(key) > 3 and len(val) > 3:
                    decisions.append(Insight(
                        category='decision',
                        content=f"{key}: {val}",
                        context=section.section_type,
                        line_number=section.line_number
                    ))

        return decisions

    def extract_key_findings(self) -> List[Insight]:
        """Extract key findings and discoveries."""
        if not self.sections:
            self.parse_sections()

        findings = []

        for section in self.sections:
            text = section.content

            # Method 1: Look for insight/finding headers
            header_pattern = r'(?:KEY INSIGHT|FINDING|DISCOVERY|LEARNED)[:\s]*\n*([^\n]{20,300})'
            for match in re.finditer(header_pattern, text, re.IGNORECASE):
                content = match.group(1).strip()
                if not content.startswith(('```', '|', '-')):
                    findings.append(Insight(
                        category='finding',
                        content=content,
                        context=section.section_type,
                        line_number=section.line_number
                    ))

            # Method 2: Look for "This means/shows/proves" patterns
            inference_pattern = r'(?:this|that)\s+(?:means|shows|proves|indicates|suggests)\s+([^.!?\n]{20,200})[.!?]'
            for match in re.finditer(inference_pattern, text, re.IGNORECASE):
                findings.append(Insight(
                    category='finding',
                    content=match.group(1).strip(),
                    context=section.section_type,
                    line_number=section.line_number
                ))

            # Method 3: Look for > blockquotes (often contain insights)
            quote_pattern = r'^>\s*\*\*([^*\n]+)\*\*\s*(.+?)(?=\n[^>]|\n\n|$)'
            for match in re.finditer(quote_pattern, text, re.MULTILINE | re.DOTALL):
                content = f"{match.group(1).strip()}: {match.group(2).strip()[:100]}"
                findings.append(Insight(
                    category='finding',
                    content=content,
                    context=section.section_type,
                    line_number=section.line_number
                ))

            # Method 4: Look for analogy explanations
            analogy_pattern = r'(?:like|just as|similar to)\s+([^,]{10,100}),\s*([^.!?\n]{20,150})[.!?]'
            for match in re.finditer(analogy_pattern, text, re.IGNORECASE):
                content = f"{match.group(1).strip()} → {match.group(2).strip()}"
                findings.append(Insight(
                    category='finding',
                    content=content,
                    context=section.section_type,
                    line_number=section.line_number
                ))

            # Method 5: Look for equation-style insights (X = Y)
            equation_pattern = r'(?:^|\n)\s*\*\*([^*=]+)\s*=\s*([^*\n]+)\*\*'
            for match in re.finditer(equation_pattern, text):
                content = f"{match.group(1).strip()} = {match.group(2).strip()}"
                if len(content) > 10:
                    findings.append(Insight(
                        category='finding',
                        content=content,
                        context=section.section_type,
                        line_number=section.line_number
                    ))

        return findings

    def extract_action_items(self) -> List[Insight]:
        """Extract TODOs and action items."""
        if not self.sections:
            self.parse_sections()

        actions = []
        action_patterns = [
            r'(?:TODO|FIXME|XXX)[:\s]+(.+?)(?:\n|$)',
            r'- \[ \]\s+(.+?)(?:\n|$)',
            r'next[:\s]+(.+?)(?:\n|$)',
            r'(?:need|should|must)\s+(?:to\s+)?(.+?)(?:\n|$)',
        ]

        for section in self.sections:
            text = section.content
            for pattern in action_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 10:
                        actions.append(Insight(
                            category='action',
                            content=match[:200],
                            context=section.section_type,
                            line_number=section.line_number
                        ))

        return actions

    def extract_code_changes(self) -> List[Dict]:
        """Extract code file mentions and changes."""
        changes = []
        file_pattern = r'\*(?:Edited|Viewed|Created)\s+\[([^\]]+)\]'

        matches = re.findall(file_pattern, self.content)
        file_counts = defaultdict(int)
        for match in matches:
            file_counts[match] += 1

        for file, count in sorted(file_counts.items(), key=lambda x: -x[1]):
            changes.append({
                'file': file,
                'touch_count': count
            })

        return changes

    def get_statistics(self) -> Dict:
        """Get statistics about the chat transcript."""
        if not self.sections:
            self.parse_sections()

        stats = {
            'file': str(self.file_path),
            'file_size_kb': self.file_path.stat().st_size / 1024,
            'total_lines': len(self.lines),
            'sections': {
                'user_inputs': len([s for s in self.sections if s.section_type == 'user_input']),
                'planner_responses': len([s for s in self.sections if s.section_type == 'planner_response']),
                'headings': len([s for s in self.sections if s.section_type == 'heading']),
            },
            'high_importance_sections': len([s for s in self.sections if s.importance >= 5]),
        }
        return stats

    def generate_summary(self) -> str:
        """Generate a comprehensive summary of the chat transcript."""
        stats = self.get_statistics()
        user_inputs = self.extract_user_inputs()
        decisions = self.extract_decisions()
        findings = self.extract_key_findings()
        actions = self.extract_action_items()
        code_changes = self.extract_code_changes()

        summary = []
        summary.append(f"# Chat Transcript Summary")
        summary.append(f"\n**Source:** `{stats['file']}`")
        summary.append(f"**Size:** {stats['file_size_kb']:.1f} KB ({stats['total_lines']} lines)")
        summary.append(f"**Sections:** {stats['sections']['user_inputs']} user inputs, {stats['sections']['planner_responses']} responses")
        summary.append(f"**High-importance sections:** {stats['high_importance_sections']}")

        # Top user inputs
        summary.append("\n## Key User Requests (by importance)")
        for i, inp in enumerate(user_inputs[:10], 1):
            content = inp['content'].replace('\n', ' ')[:150]
            summary.append(f"{i}. [L{inp['line']}] (importance: {inp['importance']}) {content}")

        # Decisions
        if decisions:
            summary.append("\n## Decisions Made")
            seen = set()
            for d in decisions[:15]:
                if d.content not in seen:
                    summary.append(f"- [L{d.line_number}] {d.content[:150]}")
                    seen.add(d.content)

        # Findings
        if findings:
            summary.append("\n## Key Findings")
            seen = set()
            for f in findings[:10]:
                if f.content not in seen:
                    summary.append(f"- [L{f.line_number}] {f.content[:150]}")
                    seen.add(f.content)

        # Action items
        if actions:
            summary.append("\n## Action Items")
            seen = set()
            for a in actions[:10]:
                if a.content not in seen:
                    summary.append(f"- [ ] {a.content[:100]}")
                    seen.add(a.content)

        # Most touched files
        if code_changes:
            summary.append("\n## Most Modified Files")
            for c in code_changes[:15]:
                summary.append(f"- `{c['file']}` ({c['touch_count']} touches)")

        return '\n'.join(summary)

    def extract_by_keyword(self, keyword: str, context_lines: int = 3) -> List[Dict]:
        """Extract sections containing a specific keyword."""
        results = []
        keyword_lower = keyword.lower()

        for i, line in enumerate(self.lines):
            if keyword_lower in line.lower():
                start = max(0, i - context_lines)
                end = min(len(self.lines), i + context_lines + 1)
                context = '\n'.join(self.lines[start:end])
                results.append({
                    'line': i + 1,
                    'match': line.strip(),
                    'context': context
                })

        return results


def main():
    parser = argparse.ArgumentParser(description='Extract insights from chat transcript markdown files')
    parser.add_argument('file', help='Path to the markdown file')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--mode', '-m', choices=['summary', 'decisions', 'user-inputs', 'findings', 'actions', 'files', 'stats', 'all'],
                       default='summary', help='Extraction mode')
    parser.add_argument('--keyword', '-k', help='Search for specific keyword')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--top', '-t', type=int, default=20, help='Number of top results to show')

    args = parser.parse_args()

    extractor = ChatExtractor(args.file)

    output = ""

    if args.keyword:
        results = extractor.extract_by_keyword(args.keyword)
        if args.json:
            output = json.dumps(results, indent=2)
        else:
            output = f"# Keyword Search: '{args.keyword}'\n\n"
            for r in results[:args.top]:
                output += f"## Line {r['line']}\n```\n{r['context']}\n```\n\n"

    elif args.mode == 'summary':
        output = extractor.generate_summary()

    elif args.mode == 'decisions':
        decisions = extractor.extract_decisions()
        if args.json:
            output = json.dumps([{'category': d.category, 'content': d.content, 'line': d.line_number} for d in decisions], indent=2)
        else:
            output = "# Decisions\n\n" + '\n'.join([f"- [L{d.line_number}] {d.content}" for d in decisions[:args.top]])

    elif args.mode == 'user-inputs':
        inputs = extractor.extract_user_inputs()
        if args.json:
            output = json.dumps(inputs[:args.top], indent=2)
        else:
            output = "# User Inputs (by importance)\n\n"
            for inp in inputs[:args.top]:
                output += f"## Line {inp['line']} (importance: {inp['importance']})\n{inp['content']}\n\n"

    elif args.mode == 'findings':
        findings = extractor.extract_key_findings()
        if args.json:
            output = json.dumps([{'category': f.category, 'content': f.content, 'line': f.line_number} for f in findings], indent=2)
        else:
            output = "# Key Findings\n\n" + '\n'.join([f"- [L{f.line_number}] {f.content}" for f in findings[:args.top]])

    elif args.mode == 'actions':
        actions = extractor.extract_action_items()
        if args.json:
            output = json.dumps([{'content': a.content, 'line': a.line_number} for a in actions], indent=2)
        else:
            output = "# Action Items\n\n" + '\n'.join([f"- [ ] {a.content}" for a in actions[:args.top]])

    elif args.mode == 'files':
        files = extractor.extract_code_changes()
        if args.json:
            output = json.dumps(files, indent=2)
        else:
            output = "# Modified Files\n\n" + '\n'.join([f"- `{f['file']}` ({f['touch_count']} touches)" for f in files[:args.top]])

    elif args.mode == 'stats':
        stats = extractor.get_statistics()
        if args.json:
            output = json.dumps(stats, indent=2)
        else:
            output = f"# Statistics\n\n```json\n{json.dumps(stats, indent=2)}\n```"

    elif args.mode == 'all':
        output = extractor.generate_summary()
        output += "\n\n---\n\n"
        output += "# Detailed Extractions\n\n"

        decisions = extractor.extract_decisions()
        if decisions:
            output += "## All Decisions\n" + '\n'.join([f"- [L{d.line_number}] {d.content}" for d in decisions]) + "\n\n"

        findings = extractor.extract_key_findings()
        if findings:
            output += "## All Findings\n" + '\n'.join([f"- [L{f.line_number}] {f.content}" for f in findings]) + "\n\n"

    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
