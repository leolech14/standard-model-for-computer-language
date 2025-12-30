"""
Boundary Patterns
=================

Regex patterns for classifying conversation messages.
"""

from .models import InteractionType, MessagePurpose


# Interaction type detection patterns
INTERACTION_PATTERNS = {
    InteractionType.QUESTION: [
        r'\?$', r'^(what|how|why|where|when|which|who|can|does|is|are)\b',
        r'\?{2,}', r'tell me', r'explain'
    ],
    InteractionType.COMMAND: [
        r'^(do|make|create|run|execute|generate|build|add|remove|fix|update)\b',
        r'^(lets|let\'s)\b', r'^proceed', r'^continue', r'^go ahead'
    ],
    InteractionType.REFLECTION: [
        r'^(i think|i feel|i believe|seems like|maybe|perhaps)\b',
        r'^(so|ok so|alright so)\b.*\.\.\.'
    ],
    InteractionType.FEEDBACK: [
        r'^(good|great|perfect|nice|awesome|excellent)\b',
        r'^(no|nope|wrong|incorrect|not quite)\b',
        r'^(yes|yeah|yep|correct|exactly)\b'
    ],
    InteractionType.CLARIFICATION: [
        r'^(i mean|what i meant|to clarify|in other words)\b',
        r'^(no,? i meant|actually)\b'
    ],
    InteractionType.CHALLENGE: [
        r'^(but|however|wait)\b', r'\?\!', r'!!+',
        r'^(are you sure|really\?|why not)\b'
    ],
    InteractionType.AGREEMENT: [
        r'^(agreed|exactly|precisely|yes)\b',
        r'^(that\'s right|correct)\b'
    ],
}

# Purpose detection patterns
PURPOSE_PATTERNS = {
    MessagePurpose.UNDERSTAND: [
        r'what (is|are|does)', r'how (does|do|is)', r'why (is|are|does)',
        r'explain', r'tell me more', r'meaning'
    ],
    MessagePurpose.DECIDE: [
        r'should (we|i)', r'which (one|should)', r'choose', r'pick',
        r'better', r'prefer', r'option'
    ],
    MessagePurpose.VALIDATE: [
        r'(is|are) (this|that|it) (correct|right|valid)',
        r'verify', r'check', r'confirm', r'test', r'reliable'
    ],
    MessagePurpose.CREATE: [
        r'create', r'make', r'build', r'generate', r'implement',
        r'add', r'write'
    ],
    MessagePurpose.DEBUG: [
        r'error', r'bug', r'fix', r'broken', r'wrong', r'issue',
        r'not working', r'failed'
    ],
    MessagePurpose.DEFINE: [
        r'define', r'what (is|are) the', r'meaning of',
        r'(is|are) (the|these)', r'called'
    ],
    MessagePurpose.CONNECT: [
        r'relationship', r'connect', r'link', r'between',
        r'related', r'similar', r'like'
    ],
    MessagePurpose.VISUALIZE: [
        r'visual', r'diagram', r'image', r'show', r'display',
        r'represent', r'keyframe', r'infographic'
    ],
    MessagePurpose.ORGANIZE: [
        r'organize', r'structure', r'categorize', r'group',
        r'list', r'order', r'hierarchy'
    ],
    MessagePurpose.CHALLENGE: [
        r'but why', r'doesn\'t make sense', r'disagree',
        r'not sure', r'question'
    ],
}

# Idea extraction patterns
IDEA_PATTERNS = [
    # Definitions
    (r'(\w+)\s+(?:is|are|means?)\s+(.{10,50})', 'definition'),
    # Comparisons
    (r'(\w+)\s+(?:like|similar to|as)\s+(\w+)', 'analogy'),
    # Key terms (ALL CAPS)
    (r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})*)\b', 'key_term'),
    # Conceptual statements
    (r'(the\s+\w+\s+(?:of|is|are)\s+.{10,60})', 'concept'),
]

# ASCII visualization symbols
TYPE_SYMBOLS = {
    'question': '?', 'command': '[]', 'reflection': '',
    'feedback': '[]', 'clarification': '', 'challenge': '',
    'agreement': '', 'exploration': ''
}

PURPOSE_SYMBOLS = {
    'understand': '', 'decide': '', 'validate': '',
    'create': '', 'debug': '', 'define': '',
    'connect': '', 'visualize': '', 'organize': '',
    'challenge': ''
}
