"""
MarkdownService for rendering markdown to HTML with syntax highlighting.
"""

import logging
from typing import Optional
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)


class MarkdownService:
    """Service for converting markdown to HTML with code highlighting."""

    def __init__(self):
        """Initialize markdown service with extensions."""
        self.md = markdown.Markdown(
            extensions=[
                "extra",
                "codehilite",
                "fenced_code",
                "tables",
                "toc",
                "nl2br",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "linenums": False,
                    "guess_lang": True,
                }
            },
        )

    def render_to_html(self, markdown_text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            markdown_text: The markdown content to render.

        Returns:
            Rendered HTML string.
        """
        if not markdown_text:
            return ""

        try:
            # Reset markdown instance to clear any state
            self.md.reset()

            # Convert markdown to HTML
            html = self.md.convert(markdown_text)

            logger.debug(f"Rendered {len(markdown_text)} chars of markdown to HTML")
            return html

        except Exception as e:
            logger.error(f"Error rendering markdown: {e}")
            # Return escaped markdown as fallback
            return f"<pre>{markdown_text}</pre>"

    def highlight_code(
        self, code: str, language: Optional[str] = None, line_numbers: bool = False
    ) -> str:
        """
        Highlight code with Pygments syntax highlighting.

        Args:
            code: The code to highlight.
            language: Programming language (e.g., 'python', 'javascript'). If None, will guess.
            line_numbers: Whether to include line numbers.

        Returns:
            HTML string with syntax-highlighted code.
        """
        if not code:
            return ""

        try:
            # Get lexer
            if language:
                try:
                    lexer = get_lexer_by_name(language, stripall=True)
                except ClassNotFound:
                    logger.warning(f"Unknown language: {language}, guessing...")
                    lexer = guess_lexer(code)
            else:
                lexer = guess_lexer(code)

            # Configure formatter
            formatter = HtmlFormatter(
                linenos="table" if line_numbers else False,
                cssclass="highlight",
                style="github-dark",
            )

            # Highlight code
            highlighted = highlight(code, lexer, formatter)

            logger.debug(f"Highlighted {len(code)} chars of {lexer.name} code")
            return highlighted

        except Exception as e:
            logger.error(f"Error highlighting code: {e}")
            # Return escaped code as fallback
            return f"<pre><code>{code}</code></pre>"

    def get_css(self, style: str = "github-dark") -> str:
        """
        Get CSS for syntax highlighting.

        Args:
            style: Pygments style name.

        Returns:
            CSS string for the specified style.
        """
        formatter = HtmlFormatter(style=style, cssclass="highlight")
        return formatter.get_style_defs(".highlight")
