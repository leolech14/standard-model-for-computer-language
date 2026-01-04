"""Flask entrypoint fixture."""
from flask import Flask

app = Flask(__name__)


def helper():
    """Helper function called by route handlers."""
    return "processed"


@app.route("/")
def index():
    """Index route - should be detected as entrypoint."""
    return helper()


@app.route("/about")
def about():
    """About route - should be detected as entrypoint."""
    helper()
    return "About page"


@app.route("/api/data", methods=["POST"])
def create_data():
    """Create data - should be detected as entrypoint."""
    return helper()


if __name__ == "__main__":
    app.run()
