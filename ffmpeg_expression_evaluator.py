import ast
parsley = """
def hlg_oetf(sysgam, v):
    vgam=v**(1/sysgam)*12
    return (0.5 * vgam**0.5
            if vgam <= 1
            else 0.17883277 * log(vgam - 0.28466892) + 0.55991073)

def hlg_eotf(sysgam, v):
    vgam=((v*2)**2
          if v < 0.5
          else exp((v-0.55991073)/0.17883277) + 0.28466892)
    return (vgam/12)**1.25

def smpte_oetf(peaknits, v):
    vv = v * peaknits / 10000
    vp = vv ** 0.1593017578125
    fn = 0.8359375 + 18.8515625 * vp
    fd = 1 + 18.6875 * vp
    return (fn / fd) ** 78.84375

def smpte_eotf(peaknits, v):
    vp = v ** (1 / 78.84375)
    fn = max(vp - 0.8359375, 0)
    fd = 18.8515625 - 18.6875 * vp
    return (fn / fd) ** (1 / 0.1593017578125) * 10000 / peaknits

def gamma_oetf(v):
    return v ** (1/2.4)

def smpte_to_hlg(val):
    return hlg_oetf(1.25, smpte_eotf(1000, val / 65535)) * 65535

def hlg_to_gamma(val):
    return gamma_oetf(hlg_eotf(1.25, val / 65535)) * 65535

def hlg_to_smpte(val):
    return smpte_eotf(1000, hlg_oetf(1.25, val / 65535)) * 65535


def smpte_to_linear(val):
    return smpte_eotf(1000, val / 65535) * 65535

def linear_to_gamma_dithered_8bit(val):
    return val ** (1 / 2.6) + (random(1) - 0.5) * 255
"""

class FnEvaluator(ast.NodeVisitor):
    def __init__(self, functions):
        self.assigns = {}
        self.functions = functions
    def visit(self, val):
        if isinstance(val, basestring):
            return val
        else:
            return super(FnEvaluator, self).visit(val)
    def visit_Assign(self, assign):
        self.assigns[assign.targets[0].id] = assign.value
        assert(assign.value is not None)
    def visit_Return(self, ret):
        return self.visit(ret.value)
    def visit_Call(self, call):
        assert isinstance(call.func, ast.Name)
        if call.func.id in self.functions:
            return FnEvaluator(self.functions).eval_fn(call.func.id, map(self.visit, call.args))
        else:
            return call.func.id + '(' + ','.join(map(self.visit, call.args)) + ')'
    def visit_BinOp(self, binop):
        if isinstance(binop.op, ast.Pow):
            return 'pow(%s,%s)' % (self.visit(binop.left), self.visit(binop.right))
        op = ({
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/'
        })[type(binop.op)]
        return '(' + self.visit(binop.left) + op + self.visit(binop.right) + ')'
    def visit_Num(self, num):
        return str(num.n)
    def visit_Name(self, name):
        return self.visit(self.assigns[name.id])
    def visit_IfExp(self, ifexp):
        return 'if(%s,%s,%s)' % (self.visit(ifexp.test), self.visit(ifexp.body), self.visit(ifexp.orelse))
    def visit_Compare(self, cmp):
        assert len(cmp.ops) == 1
        op = ({
            ast.Eq: 'eq',
            ast.NotEq: 'neq',
            ast.Lt: 'lt',
            ast.LtE: 'lte',
            ast.Gt: 'gt',
            ast.GtE: 'gte',
        })[type(cmp.ops[0])]
        return '%s(%s,%s)' % (op, self.visit(cmp.left), self.visit(cmp.comparators[0]))

    def generic_visit(self, node):
        raise NotImplementedError(str(node))

    def eval_fn(self, name, argvals):
        fn = self.functions[name]
        self.assigns = {}
        for arg, val in zip(fn.args.args, argvals):
            assert isinstance(arg, ast.Name)
            self.assigns[arg.id] = val
        for stmt in fn.body:
            out = self.visit(stmt)
        return out

if __name__ == "__main__":
    functions = dict((fn.name, fn) for fn in ast.parse(parsley).body)
    print FnEvaluator(functions).eval_fn('smpte_to_hlg', ['val']).replace(',', r'\\,')
    #print FnEvaluator(functions).eval_fn('hlg_to_gamma', ['val']).replace(',', r'\\,')
    #print FnEvaluator(functions).eval_fn('hlg_to_smpte', ['val']).replace(',', r'\\,')
    print FnEvaluator(functions).eval_fn('smpte_to_linear', ['val']).replace(',', r'\\,')
    print FnEvaluator(functions).eval_fn('linear_to_gamma_dithered_8bit', ['val']).replace(',', r'\\,')

    exec (parsley + "\nprint smpte_eotf(1000, smpte_oetf(1000, 0.75))") in {}

