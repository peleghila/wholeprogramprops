import itertools
import ast
import astunparse

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        None

    def generic_visit(self,node):
        #print(type(node).__name__)
        #print([child[0] for child in ast.iter_fields(node)])
        print(astunparse.unparse(node))
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Expr(self,node):
        #print("Expression value: " + str(node.value))
        print(astunparse.unparse(node))
        self.generic_visit(node)

    def visit_Call(self,node):
        if isinstance(node.func,ast.Attribute):
            #print("Call: " + node.func.attr)
            print(astunparse.unparse(node))
            self.childVisit(node.func.value)
        else:
            #print("Call: " + node.func.id)
            print(astunparse.unparse(node))
        self.childVisit(node.args)
        self.childVisit(node.keywords)

    def visit_Lambda(self,node):
        #print("Lambda with args: " + ",".join([a.arg for a in node.args.args]))
        print(astunparse.unparse(node))
        self.childVisit(node.body)

    def visit_BoolOp(self,node):
        opName = type(node.op).__name__
        #print("BoolOp: " + opName)
        print(astunparse.unparse(node))
        self.childVisit(node.values)

    def visit_BinOp(self,node):
        opName = type(node.op).__name__
        #print("BinOp: " + opName)
        print(astunparse.unparse(node))
        self.childVisit(node.left)
        self.childVisit(node.right)

    def visit_Compare(self,node):
        #print("Comparator")
        print(astunparse.unparse(node))
        self.childVisit(node.left)
        self.childVisit(node.comparators)

    def visit_Load(self,node):
        pass #Nop

    def childVisit(self,attr):
        if isinstance(attr,ast.AST):
            self.visit(attr)
        elif isinstance(attr,(list,set,tuple)):
            [self.visit(n) for n in attr]

with open("examples/order-examples.txt") as f:
    lines = list(filter(lambda l: l and not l.startswith("#"), [l.strip() for l in f.readlines()]))

for expr in lines:
    print(expr)
    parseTree = ast.parse(expr)
    analyzer = Analyzer()
    analyzer.visit(parseTree)