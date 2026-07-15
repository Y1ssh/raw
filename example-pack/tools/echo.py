"""A dummy tool. Domain-free — just proves the pack->base wiring.

Real tools (search_corpus, edit_file, forecast) live in real pack repos.
"""


def echo(text: str) -> str:
    """Return the input unchanged. The world's most useless (but wired-up) tool."""
    return text
