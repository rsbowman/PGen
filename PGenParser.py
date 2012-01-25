from PGen import *
from PGenSemantics import *
from Stack import Stack
import string

# a recursive descent parser for parsing
# a little parser generator language
class PGenParser:
    def __init__(self, lexer, pre, post):
        self.lexer = lexer
        self.nonterms = []
        self.grammar = PGenGrammar(pre, post)
        self.curComp = None
        self.curOrList = None

    def S(self):
        self.lexer.getTok()

        self.lexer.match(NONTERM)
        lhs = self.lexer.tok
        self.lexer.getTok()

        self.lexer.match(GOESTO)
        self.lexer.getTok()   # don't care about the '->'

        rhs = self.e()
        self.grammar.addProduction(Production(lhs, rhs))
        self.lexer.match(END)
        self.lexer.getTok()
        self.verbose('S: '+`rhs`)

        while self.lexer.ttype == NONTERM:
            lhs = self.lexer.tok
            self.lexer.getTok()
            self.lexer.match(GOESTO)
            self.lexer.getTok()

            rhs = self.e()
            self.grammar.addProduction(Production(lhs, rhs))
            self.verbose('S: '+`rhs`)

            self.lexer.match(END)
            self.lexer.getTok()

        self.verbose('success!')

    def e(self):
        t = self.t()
        curOrList = OrList(t)

        self.verbose('e: '+`curOrList`)
            
        while self.lexer.ttype == OR:
            self.lexer.getTok()
            t = self.t()
            curOrList.append(t)
            self.verbose('e: '+`curOrList`)

        return curOrList

    def t(self):
        f = self.f()
        curComp = Composition(f)

        self.verbose('t: '+`curComp`)

        while self.lexer.ttype in [EPSILON, TERM, NONTERM, ACTION, LP]:
            f = self.f()
            curComp.append(f)
            self.verbose('t: '+`f`)

        return curComp

    def f(self):
        g = self.g()
        if self.lexer.ttype == STAR:
            star = StarExpr(g)
            self.verbose('f: '+`g`)
            self.lexer.getTok()
            return star
        elif self.lexer.ttype == PLUS:
            plus = PlusExpr(g)
            self.verbose('f: '+`g`)
            self.lexer.getTok()
            return plus
        else:
            return g

    def g(self):
        if self.lexer.ttype == EPSILON:        #
            self.verbose('epsilon')
            self.lexer.getTok()                #
            ret = EPSILON                      #
        elif self.lexer.ttype == TERM:         #
            self.verbose('g: terminal: %s' % self.lexer.tok)
            ret = Terminal(self.lexer.tok)
            self.lexer.getTok()                #
        elif self.lexer.ttype == NONTERM:       #
            self.verbose('g: nonterminal: %s' % self.lexer.tok)
            ret = NonTerminal(self.lexer.tok)
            self.lexer.getTok()                  #
        elif self.lexer.ttype == LP:
            self.lexer.getTok()
            ret = self.e()
            self.lexer.match(RP)
            self.lexer.getTok()
        else:
            self.error()

        if self.lexer.ttype == ACTION:
            self.verbose('g: action: %s' % self.lexer.tok)
            #print '--------->', ret
            ret.addAction(Action(self.lexer.tok))
            self.lexer.getTok()

        return ret

    def verbose(self, str):
        if debug:
            print str

    def error(self):
        import sys
        print 'error in parser'
        sys.exit(0)

if __name__ == '__main__':
    import sys
    from PGenSemantics import *
    from PGenLexer import PGenLexer
    from string import join
    
    text = sys.stdin.read()
    text = string.split(text, '%%')
    if len(text) == 1:
        pre, post = '', ''
        text = text[0]
    elif len(text) == 2:
        pre = text[0]
        post = ''
        text = text[1]
    elif len(text) > 2:
        pre = text[0]
        post = join(text[2:], '%%')
        text = text[1]

    parser = PGenParser(PGenLexer(text), pre, post)
    parser.S()
    parser.grammar.writeParser(sys.stdout)
