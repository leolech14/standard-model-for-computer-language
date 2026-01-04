"""Pytest test fixture."""


def helper():
    """Helper function called by test."""
    return 42


def test_example():
    """Test function - should be detected as entrypoint when include_tests=True."""
    assert helper() == 42


def test_another():
    """Another test function."""
    helper()
    assert True


class TestClass:
    """Test class."""

    def test_method(self):
        """Test method - should be detected as entrypoint."""
        assert helper() == 42
