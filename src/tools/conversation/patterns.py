"""
Conversation Patterns
=====================

Regex patterns for topic and mode detection.
"""

from .models import DialogueMode

# Topic detection patterns
TOPIC_PATTERNS = {
    'architecture': r'\b(component|architecture|system|design|structure|layer)\b',
    'atoms': r'\b(atom|particle|node|element|symbol)\b',
    'ast': r'\b(AST|syntax|tree|parse|token)\b',
    'patterns': r'\b(pattern|prefix|suffix|naming|convention)\b',
    'dimensions': r'\b(dimension|WHAT|WHERE|HOW|WHY|WHO|WHEN)\b',
    'graph': r'\b(graph|edge|connection|relationship|link)\b',
    'physics': r'\b(physics|force|mass|charge|spin|particle)\b',
    'astronomy': r'\b(star|constellation|galaxy|universe|cosmos)\b',
    'fractals': r'\b(fractal|scale|self-similar|recursive|mandel)\b',
    'roles': r'\b(Factory|Repository|Analyzer|Validator|Controller|Service)\b',
    'confidence': r'\b(confidence|accuracy|precision|coverage)\b',
    'testing': r'\b(test|benchmark|validate|verify)\b',
    'visualization': r'\b(visual|diagram|chart|image|keyframe)\b',
}

# Mode detection patterns
MODE_PATTERNS = {
    DialogueMode.QUESTIONING: r'\?{1,}|\bwhat\b|\bhow\b|\bwhy\b|\bwhere\b|\bwhen\b',
    DialogueMode.TESTING: r'\*User accepted|```python|run_benchmark|pytest',
    DialogueMode.EXPLORING: r'\blet\'s\b|\bexplore\b|\bshow me\b|\bwhat if\b',
    DialogueMode.EXPLAINING: r'\bbecause\b|\bthis means\b|\bfor example\b|\bin other words\b',
    DialogueMode.DECIDING: r'\bdecided\b|\bchoose\b|\bwill use\b|\bshould\b',
    DialogueMode.BUILDING: r'\bcreate\b|\bimplement\b|\badd\b|\bbuild\b',
    DialogueMode.DEBUGGING: r'\berror\b|\bfix\b|\bissue\b|\bproblem\b',
    DialogueMode.REFLECTING: r'\blearned\b|\brealized\b|\binteresting\b|\binsight\b',
    DialogueMode.ONTOLOGY: r'[A-Z]{4,}|AS ABOVE|SO BELOW|fundamental|essence|nature of',
    DialogueMode.VISUALIZING: r'\bdiagram\b|\bvisualize\b|\bkeyframe\b|\bimage\b',
}

# Visualization symbols
TOPIC_SYMBOLS = {
    'architecture': '',
    'atoms': '',
    'ast': '',
    'patterns': '',
    'dimensions': '',
    'graph': '',
    'physics': '',
    'astronomy': '',
    'fractals': '',
    'roles': '',
    'confidence': '',
    'testing': '',
    'visualization': '',
    'general': '',
}

MODE_SYMBOLS = {
    'questioning': '?',
    'testing': '',
    'exploring': '',
    'explaining': '',
    'deciding': '',
    'building': '',
    'debugging': '',
    'reflecting': '',
    'ontology': '',
    'visualizing': '',
}
