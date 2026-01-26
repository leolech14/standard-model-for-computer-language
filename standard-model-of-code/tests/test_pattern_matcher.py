"""
Tests for PatternMatcher - tree-sitter based atom detection.
"""
import pytest

try:
    import tree_sitter
    import tree_sitter_python
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

try:
    from src.core.pattern_matcher import (
        PatternMatcher,
        AtomMatch,
        detect_atoms,
        ATOM_CONFIDENCE,
    )
except ImportError:
    from core.pattern_matcher import (
        PatternMatcher,
        AtomMatch,
        detect_atoms,
        ATOM_CONFIDENCE,
    )


def parse_python(code: str):
    """Helper to parse Python code."""
    if not HAS_TREE_SITTER:
        pytest.skip("tree-sitter not available")
    parser = tree_sitter.Parser()
    parser.language = tree_sitter.Language(tree_sitter_python.language())
    return parser.parse(bytes(code, 'utf8'))


@pytest.mark.skipif(not HAS_TREE_SITTER, reason="tree-sitter not available")
class TestPatternMatcher:
    """Tests for PatternMatcher class."""

    def test_matcher_initialization(self):
        """PatternMatcher initializes correctly."""
        matcher = PatternMatcher()
        assert matcher.queries_dir is not None

    def test_detect_repository(self):
        """Detects Repository pattern."""
        code = '''
class UserRepository:
    def get(self, id):
        return self.db.find(id)
    def save(self, user):
        self.db.insert(user)
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        repo_atoms = [a for a in atoms if a.type == 'repository']
        assert len(repo_atoms) >= 1
        assert repo_atoms[0].name == 'UserRepository'

    def test_detect_service(self):
        """Detects Service pattern."""
        code = '''
class UserService:
    def execute(self, user_id):
        return self.get_user(user_id)
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        service_atoms = [a for a in atoms if a.type == 'service']
        assert len(service_atoms) >= 1

    def test_detect_validator(self):
        """Detects Validator pattern."""
        code = '''
def validate_email(email):
    if '@' not in email:
        raise ValueError("Invalid")
    return True
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        validator_atoms = [a for a in atoms if a.type == 'validator']
        assert len(validator_atoms) >= 1
        assert validator_atoms[0].name == 'validate_email'

    def test_detect_factory(self):
        """Detects Factory pattern."""
        code = '''
def create_user(name, email):
    return {"name": name, "email": email}
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        factory_atoms = [a for a in atoms if a.type == 'factory']
        assert len(factory_atoms) >= 1
        assert factory_atoms[0].name == 'create_user'

    def test_detect_exception(self):
        """Detects Exception pattern."""
        code = '''
class ValidationError(Exception):
    pass
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        exception_atoms = [a for a in atoms if a.type == 'exception']
        assert len(exception_atoms) >= 1

    def test_detect_test(self):
        """Detects Test pattern."""
        code = '''
def test_user_creation():
    user = create_user("test", "test@example.com")
    assert user["name"] == "test"
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        test_atoms = [a for a in atoms if a.type == 'test']
        assert len(test_atoms) >= 1
        assert test_atoms[0].name == 'test_user_creation'

    def test_detect_query(self):
        """Detects Query pattern."""
        code = '''
def get_user_by_id(user_id):
    return db.find(user_id)

def find_all_users():
    return db.find_all()
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        query_atoms = [a for a in atoms if a.type == 'query']
        assert len(query_atoms) >= 1

    def test_detect_command(self):
        """Detects Command pattern."""
        code = '''
def delete_user(user_id):
    db.delete(user_id)

def update_user(user_id, data):
    db.update(user_id, data)
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        command_atoms = [a for a in atoms if a.type == 'command']
        assert len(command_atoms) >= 1

    def test_detect_handler(self):
        """Detects Handler pattern."""
        code = '''
def handle_user_created(event):
    send_welcome_email(event.user)

def on_error(exception):
    log_error(exception)
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        handler_atoms = [a for a in atoms if a.type == 'handler']
        assert len(handler_atoms) >= 1


class TestAtomMatch:
    """Tests for AtomMatch dataclass."""

    def test_atom_match_fields(self):
        """AtomMatch has all expected fields."""
        atom = AtomMatch(
            type='repository',
            name='UserRepository',
            start_line=1,
            end_line=10,
            start_byte=0,
            end_byte=100,
            confidence=0.92,
            evidence='Pattern: @atom.repository.name',
            capture_name='atom.repository.name'
        )
        assert atom.type == 'repository'
        assert atom.name == 'UserRepository'
        assert atom.confidence == 0.92


class TestAtomConfidence:
    """Tests for confidence scores."""

    def test_confidence_values(self):
        """All atom types have confidence scores."""
        expected_types = [
            'entity', 'repository', 'service', 'controller',
            'handler', 'factory', 'dto', 'validator', 'mapper',
            'query', 'command', 'test', 'exception'
        ]
        for atom_type in expected_types:
            assert atom_type in ATOM_CONFIDENCE
            assert 0.0 < ATOM_CONFIDENCE[atom_type] <= 1.0


@pytest.mark.skipif(not HAS_TREE_SITTER, reason="tree-sitter not available")
class TestAtomSummary:
    """Tests for summary functionality."""

    def test_get_atom_summary(self):
        """get_atom_summary returns correct counts."""
        matcher = PatternMatcher()
        code = '''
class UserRepository:
    def get(self, id): pass

class OrderRepository:
    def get(self, id): pass

def test_repos():
    pass
'''
        atoms = matcher.detect_atoms_in_code(code, 'python')
        summary = matcher.get_atom_summary(atoms)

        assert isinstance(summary, dict)
        assert 'repository' in summary
        assert summary['repository'] >= 1


@pytest.mark.skipif(not HAS_TREE_SITTER, reason="tree-sitter not available")
class TestMultiplePatterns:
    """Tests for code with multiple patterns."""

    def test_complex_module(self):
        """Detects multiple atoms in complex module."""
        code = '''
class UserEntity:
    id: str
    name: str

class UserRepository:
    def get(self, id): pass
    def save(self, user): pass

class UserService:
    def execute(self, user_id): pass

def validate_user(user):
    if not user.name:
        raise ValueError("No name")

def create_user(name):
    return UserEntity(name=name)

class UserNotFoundError(Exception):
    pass

def test_user_service():
    service = UserService()
    assert service is not None
'''
        matcher = PatternMatcher()
        atoms = matcher.detect_atoms_in_code(code, 'python')

        # Should detect multiple different types
        types = {a.type for a in atoms}
        assert len(types) >= 3  # At least 3 different atom types
