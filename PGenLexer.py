from PGen import *

# patterns used by the lexer
idNontermPatt = compile(r'<([a-zA-Z]\w*)>\s*', X) # verbose mode
idTermPatt = compile(r'([a-zA-Z]\w*)\s*', X)
actionPatt = compile(r'\[\s*(.*?)\]\s*', X)
goestoPatt = compile(r'(->)\s*', X)
epsilonPatt = compile(r'(epsilon)\s*', X)
starPatt = compile(r'(\*)\s*', X)
plusPatt = compile(r'(\+)\s*', X)
orPatt = compile(r'(\|)\s*', X)
endPatt = compile(r'(\.)\s*', X)
rpPatt = compile(r'(\))\s*', X)
lpPatt = compile(r'(\()\s*', X)
ws = compile(r'\s*', X)

lexemes = [ (epsilonPatt, EPSILON), (goestoPatt, GOESTO), (starPatt, STAR), 
            (plusPatt, PLUS), (orPatt, OR), (endPatt, END),
            (rpPatt, RP),
            (lpPatt, LP),
            (actionPatt, ACTION),
            (idNontermPatt, NONTERM),
            (idTermPatt, TERM) ]

        
# a lexical analyzer for the parser generator language
class PGenLexer:
    def __init__(self, text):
        self.text = text
        self.tok = ''
        self.ttype = NONE
    # get rid of whitespace at the beginning of the text
        g = ws.match(self.text)
        if g != None:
            self.text = self.text[g.end(0):]

    def getTok(self):
        if self.text == '':
            self.tok = ''
            self.ttype = EOF
            return
        else:
            for lex in lexemes:
                g = lex[0].match(self.text)
                if g != None:
                    self.tok = g.group(1)
                    self.ttype = lex[1]
                    self.text = self.text[g.end(0):]
                    self.p()
                    return

        import sys
        print 'invalid text: ', self.text
        print '               ^'
        sys.exit(0)

    # match gets a token before checking it
    def match(self, toktype):
        if self.ttype != toktype:
            self.error("expecting %s, found %s" % (toktype, self.ttype))

    def error(self, str=None):
        print 'error ',
        if str != None:
            print str

    def p(self):
        if debug:    
            print '-->lexer returned (%s, %s)' %(self.tok, self.ttype)
