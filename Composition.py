import itertools
import functools
import ast

class OrderInvarianceAnalyzer(ast.NodeVisitor):
    def __init__(self):
        pass

    def generic_visit(self,node):
        print("generic visit: " + type(node).__name__)
        print([child[0] for child in ast.iter_fields(node)])
        return ast.NodeVisitor.generic_visit(self, node)

    def visit_Module(self,node):
        return functools.reduce(lambda x,y: x and y, self.childVisit(node.body),True)

    def visit_Expr(self,node):
        #print("Expression value: " + str(node.value))
        return self.childVisit(node.value)

    def visit_Call(self,node):
        all_args = []
        if isinstance(node.func,ast.Attribute):
            fname = node.func.attr
            all_args.append(self.childVisit(node.func.value))
        else:
            fname = node.func.id
        if fname in ["sorted","len","sum","count"]:
            return True
        elif fname in ["map","filter"]:
            #is iter1 a variable
            return self.childVisit(node.args[1])
        elif fname == "reduce":
            return None #placeholder
        else:
            all_args.extend(self.childVisit(node.args))
            all_args.extend(self.childVisit(node.keywords))
            return functools.reduce(lambda x,y: x and y, all_args,True)
    def visit_Lambda(self,node):
        #print("Lambda with args: " + ",".join([a.arg for a in node.args.args]))
        return self.childVisit(node.body)

    def visit_BoolOp(self,node):
        opName = type(node.op).__name__
        #print("BoolOp: " + opName)
        self.childVisit(node.values)

    def visit_BinOp(self,node):
        opName = type(node.op).__name__
        #print("BinOp: " + opName)
        return self.childVisit(node.left) and self.childVisit(node.right)

    def visit_Compare(self,node):
        #print("Comparator")
        if (len(node.ops) == 1 and isinstance(node.ops[0],ast.In)):
            return True #if it's there, it's there, regardless of order
        self.childVisit(node.left)
        self.childVisit(node.comparators)

    def visit_Subscript(self,node):
        return self.childVisit(node.value) and self.childVisit(node.slice)

    def visit_Index(self,node):
        return self.childVisit(node.value)

    def visit_Load(self,node):
        pass #Nop

    def visit_List(self,node):
        return functools.reduce(lambda x,y: x and y, self.childVisit(node.elts), True)

    def visit_Num(self,node):
        return True

    def visit_Name(self,node):
        #are you a list var? then no.
        return node.id != "inpt" #for now

    def childVisit(self,attr):
        if isinstance(attr,ast.AST):
            return self.visit(attr)
        elif isinstance(attr,(list,set,tuple)):
            return [self.visit(n) for n in attr]

with open("examples/order-examples.txt") as f:
    lines = list(filter(lambda l: l and not l.startswith("#"), [l.strip() for l in f.readlines()]))

for expr in lines:
    print(expr)
    expected = expr.split("#")[1].strip() == "invariant"
    parseTree = ast.parse(expr)
    analyzer = OrderInvarianceAnalyzer()
    result = analyzer.visit(parseTree)
    if result is not None:
        print (str(result) + ", " + str(result == expected))
    else:
        print(result)
