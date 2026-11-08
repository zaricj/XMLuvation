"""Domain and application error types.

Each error carries a short ``title`` suitable for a dialog caption and a user-facing
message. Technical details belong in the log, not in these messages.
"""

from __future__ import annotations


class XMLuvationError(Exception):
    """Base class for expected, user-actionable failures."""

    title = "Error"

    def __init__(self, message: str, *, title: str | None = None) -> None:
        super().__init__(message)
        if title is not None:
            self.title = title

    @property
    def message(self) -> str:
        return str(self.args[0]) if self.args else ""


class ValidationError(XMLuvationError):
    """Input is missing or inconsistent. Shown as a warning."""

    title = "Invalid input"


class InvalidXPathError(ValidationError):
    title = "XPathSyntaxError"

    def __init__(self, expression: str, detail: str) -> None:
        super().__init__(f"XPath syntax error: {detail}\n\nExpression: {expression}")
        self.expression = expression
        self.detail = detail


class XmlParseError(XMLuvationError):
    title = "Could not parse XML file"


class OutputFileError(XMLuvationError):
    title = "Cannot write output file"


class CsvReadError(XMLuvationError):
    title = "CSV Reading Error"


class Cancelled(Exception):
    """Raised inside a running task when the user requested cancellation."""
