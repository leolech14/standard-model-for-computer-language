"""
Boundary Mapper
===============

Facade that orchestrates all boundary mapping components.
"""

from pathlib import Path
from typing import List, Dict

from .models import Message, Section, Region
from .parser import MessageParser
from .analyzer import BoundaryAnalyzer
from .reporter import BoundaryReporter


class BoundaryMapper:
    """
    Maps conversation boundaries at multiple levels.

    Composes specialized components:
    - MessageParser: Parses transcripts into messages
    - BoundaryAnalyzer: Identifies sections and regions
    - BoundaryReporter: Generates reports and visualizations

    Usage:
        mapper = BoundaryMapper(['transcript1.md', 'transcript2.md'])
        mapper.parse_messages()
        mapper.identify_sections()
        mapper.identify_regions()
        report = mapper.generate_report()
    """

    def __init__(self, files: List[str]):
        self.files = [Path(f) for f in files]
        self.messages: List[Message] = []
        self.sections: List[Section] = []
        self.regions: List[Region] = []

        # Components
        self._parser = MessageParser()
        self._analyzer = BoundaryAnalyzer()
        self._reporter = BoundaryReporter()

    def parse_messages(self) -> List[Message]:
        """Parse all files into individual messages."""
        self.messages = self._parser.parse_files(self.files)
        print(f"Parsed {len(self.messages)} unique messages")
        return self.messages

    def identify_sections(
        self,
        min_size: int = 2,
        max_size: int = 10
    ) -> List[Section]:
        """Group messages into sections based on theme/purpose shifts."""
        if not self.messages:
            self.parse_messages()

        self.sections = self._analyzer.identify_sections(
            self.messages, min_size, max_size
        )
        print(f"Identified {len(self.sections)} sections")
        return self.sections

    def identify_regions(self, min_sections: int = 2) -> List[Region]:
        """Group sections into large regions."""
        if not self.sections:
            self.identify_sections()

        self.regions = self._analyzer.identify_regions(
            self.sections, min_sections
        )
        print(f"Identified {len(self.regions)} regions")
        return self.regions

    def generate_report(self) -> Dict:
        """Generate full boundary analysis report."""
        if not self.regions:
            self.identify_regions()

        return self._reporter.generate_report(
            self.messages, self.sections, self.regions
        )

    def generate_ascii_map(self) -> str:
        """Generate ASCII visualization of boundaries."""
        if not self.regions:
            self.identify_regions()

        return self._reporter.generate_ascii_map(self.regions)
