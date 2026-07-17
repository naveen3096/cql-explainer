from .grammar.cqlVisitor import cqlVisitor
from .grammar.cqlParser import cqlParser


class CQLStructureVisitor(cqlVisitor):
    def __init__(self):
        self.library_name = None
        self.usings = []
        self.includes = []
        self.valuesets = []
        self.codesystems = []
        self.contexts = []
        self.definitions = []

    def visitLibraryDefinition(self, ctx: cqlParser.LibraryDefinitionContext):
        self.library_name = ctx.qualifiedIdentifier().getText()
        return self.visitChildren(ctx)

    def visitUsingDefinition(self, ctx):
        self.usings.append(ctx.getText())
        return self.visitChildren(ctx)

    def visitIncludeDefinition(self, ctx):
        self.includes.append(ctx.getText())
        return self.visitChildren(ctx)

    def visitValuesetDefinition(self, ctx):
        name = ctx.identifier().getText() if ctx.identifier() else None
        self.valuesets.append({"name": name, "text": ctx.getText()})
        return self.visitChildren(ctx)

    def visitCodesystemDefinition(self, ctx):
        self.codesystems.append(ctx.getText())
        return self.visitChildren(ctx)

    def visitContextDefinition(self, ctx):
        self.contexts.append(ctx.getText())
        return self.visitChildren(ctx)

    def visitExpressionDefinition(self, ctx):
        name = ctx.identifier().getText() if ctx.identifier() else "unnamed"
        self.definitions.append({
            "name": name,
            "start_line": ctx.start.line,
            "end_line": ctx.stop.line,
        })
        return self.visitChildren(ctx)
