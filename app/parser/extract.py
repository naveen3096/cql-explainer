from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from .grammar.cqlLexer import cqlLexer
from .grammar.cqlParser import cqlParser
from .visitor import CQLStructureVisitor


class CollectingErrorListener(ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"line {line}:{column} {msg}")


def parse_cql(source: str) -> dict:
    lines = source.splitlines()
    error_listener = CollectingErrorListener()

    input_stream = InputStream(source)
    lexer = cqlLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = cqlParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.library()

    if error_listener.errors:
        raise ValueError("; ".join(error_listener.errors))

    visitor = CQLStructureVisitor()
    visitor.visit(tree)

    for d in visitor.definitions:
        d["source"] = "\n".join(lines[d["start_line"] - 1 : d["end_line"]])

    return {
        "library_name": visitor.library_name,
        "usings": visitor.usings,
        "includes": visitor.includes,
        "valuesets": visitor.valuesets,
        "codesystems": visitor.codesystems,
        "contexts": visitor.contexts,
        "definitions": visitor.definitions,
    }
