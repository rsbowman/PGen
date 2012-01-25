from PGen import *
# classes to support representation of BNF grammar

def indent(listOfStrings):
    ret = []
    for str in listOfStrings:
        ret.append('   '+str)
    return ret

def prettyList(list):
    str = '[%s' % list[0]
    for e in list[1:]:
        str = str+', %s' % e
    str = str + ']'
    return str

# represents a rhs of the form A1 A2 ... An, n>1
class Composition:
    def __init__(self, prod=None):
        self.firstSet = None
        self.action = None
        if prod != None:
            self.list = [prod]
        else:
            self.list = []

    def append(self, prod):
        self.list.append(prod)

    def first(self):
        if self.firstSet == None:
            ret = []
            for prod in self.list:
                ret = ret + prod.first()
                if not prod.derivesEpsilon():
                    self.firstSet = ret
                    break

        return self.firstSet

# old: (assumes epsilon free grammar)
#        return self.list[0].first()

    def derivesEpsilon(self): # if every Ai derives epsilon return 1
        for prod in self.list:
            if not prod.derivesEpsilon():
                return 0
        return 1

    def code(self):
        ret = []
        for prod in self.list:
            ret = ret + prod.code()
        if self.action != None:
            ret = ret + self.action.code()

        return ret

    def addAction(self, action):
        self.action = action

    def getTerminals(self):
        ret = []
        for p in self.list:
            ret = ret + p.getTerminals()
        return ret

    def __repr__(self):
        if len(self.list) == 1:
            return `self.list[0]`

        str = '('
        for prod in self.list:
            str = str + `prod` + ' '
        str = str + ')'
        return str

    def __len__(self):
        return len(self.list)

class Terminal:
    def __init__(self, name):
        self.name = name
        self.action = None

    def addAction(self, a):
        self.action = a

    def first(self):
        return [`self`]

    def derivesEpsilon(self):
        return 0 #nope

    def code(self):
        ret = ['if self.lexer.ttype == %s:' % self.name]
        if self.action != None:
            ret = ret + indent(self.action.code())
        return ret + ['   self.lexer.getTok()', 'else:',
            '   raise PGParserError("expecting %s, found %s"%self.lexer.tok)' % (self.name, '%s', '%s')]

    def getTerminals(self):
        return [self.name]

    def __repr__(self):
        return self.name

    def __len__(self):
        return 1
    

class NonTerminal:
    def __init__(self, name):
        self.name = name
        self.firstSet = None
        self.action = None

    def code(self):
        ret = ['synthAtt_%s = self.%s()' % (self.name, self.name)]
        if self.action != None:
            ret = ret+self.action.code()
        return ret

    def first(self):
        if self.firstSet == None:
            p = getRHS(self.name)  # a hack
            self.firstSet = p.first()

        return self.firstSet

    def addAction(self, action):
        self.action = action

    def __repr__(self):
        return '<%s>' %self.name

    def getTerminals(self):
        return []

    def __len__(self):
        return 1

    def derivesEpsilon(self):
        prod = getRHS(self.name)  # a hack
        return prod.derivesEpsilon()
        
class OrList:
    def __init__(self, prod=None):  # list of productions
        self.firstSet = None
        self.action = None
        if prod == None:
            self.list = []
        else:
            self.list = [prod]

    def append(self, prod):
        self.list.append(prod)

    def addAction(self, action):
        self.action = action

    def first(self):
        if self.firstSet == None:
            ret = []
            for prod in self.list:
                r = prod.first()
                for term in r:
                    if term not in ret:
                        ret.append(term)
            self.firstSet = ret

        return self.firstSet

    def derivesEpsilon(self):
        for prod in self.list:
            if prod.derivesEpsilon():
                return 1
        return 0

    def code(self):
        if self.list == []:
            return []

        ret = []

        if len(self.list) == 1:   
            return self.list[0].code()

        ret = ['if self.lexer.ttype in %s:'% prettyList(self.list[0].first())] + indent(self.list[0].code())
        for prod in self.list[1:]:
            ret = ret + ['elif self.lexer.ttype in %s:' % prettyList(prod.first())] + indent(prod.code())
    
        ret = ret + ['else:', '   raise PGParserError()']

        if self.action != None:
            ret = ret + self.action.code()

        return ret

    def getTerminals(self):
        ret = []
        for p in self.list:
            ret = ret + p.getTerminals()
        return ret
        
    def __repr__(self):
        if self.list == []:
            return ''
        elif len(self.list) == 1:
            return `self.list[0]`
        str = '(' + `self.list[0]`
        for p in self.list[1:]:
            str = str + '|' + `p`
        return str + ')'

    def __len__(self):
        return len(self.list)
            
class StarExpr:
    def __init__(self, prod):
        self.prod = prod

    def first(self):
        return self.prod.first()

    def derivesEpsilon(self):
        return 1

    def code(self):
        return [ 'while self.lexer.ttype in %s:' % prettyList(self.prod.first())] + indent(self.prod.code())

    def getTerminals(self):
        return self.prod.getTerminals()

    def __repr__(self):
        return `self.prod`+'*'

    def __len__(self):
        return 1
    

class PlusExpr:
    def __init__(self, prod):
        self.prod = prod

    # because this rule is defined like this, plus exprs will
    # only work if they are the last symbol on the rhs; ie
    # statements of the form A -> B [C] D must have D=epsilon.
    def first(self):
        return self.prod.first()

    def derivesEpsilon(self):
        return 1

    def code(self):
        return ['if self.lexer.ttype in %s:' % prettyList(self.prod.first())] + indent(self.prod.code())
#        return self.prod.code()+['while self.lexer.ttype in %s:' % self.prod.first()] + indent(self.prod.code())

    def getTerminals(self):
        return self.prod.getTerminals()
    
    def __repr__(self):
        return `self.prod`+'+'

    def __len__(self):
        return 1

class Action:
    def __init__(self, codestr):
        self.codestr = codestr

    def first(self):
        return []

    def derivesEpsilon(self):
        return 1

    def code(self):
        return [self.codestr]

    def __repr__(self):
        return self.codestr

    def __len__(self):
        return 1

    def getTerminals(self):
        return []

# this is kinda a hak
# it's so NonTerminal can find the associated production
# when its first method is called
productions = {} # a dict of prods and their rhss
def getRHS(name):
    return productions[name]

class Production:
    def __init__(self, name, rhs):   # rhs is a Composition
        self.name = name
        self.rhs = rhs
        productions[name] = rhs 

    def first(self):
        return self.rhs.first()

    def derivesEpsilon(self):
        return self.rhs.derivesEpsilon()

    def code(self):
        code = self.parseCodeList(self.rhs.code())
        ret = ['def %s(self):'%self.name, '   synthAttRetVal = None']
        ret = ret + indent(code) + ['   return synthAttRetVal']
        return ret

    def parseCodeList(self, list):
        # strings of the form @<name> = ... where @name is the name
        # of this production
        selfActionAssignment = compile(r'@<%s>\s*=(.*)'%self.name, X)
        selfActionReference = compile(r'@<%s>'%self.name, X)
        # strings like @<nterm> where nterm is not our name
        nontermActionReference = compile(r'@<([a-zA-z]\w*?)>', X)
        termActionReference = compile(r'@([a-zA-Z]\w*)', X)
        
        def repl(mobj):
            return 'synthAttRetVal = %s' % mobj.group(1)

        ret = []
        for line in list:
            line = selfActionAssignment.sub(repl, line)
            line = selfActionReference.sub(lambda x: 'synthAttRetVal', line)
            line = nontermActionReference.sub(lambda x: 'synthAtt_%s'%x.group(1), line)
            line = termActionReference.sub(lambda x: 'self.lexer.tok', line)
            ret.append(line)

        return ret

    def getTerminals(self):
        return self.rhs.getTerminals()

    def __repr__(self):
        return '%s -> %s' % (self.name, self.rhs)


class PGenGrammar:
    def __init__(self, pre, post):
        self.prods = []
        self.preface, self.postface = pre, post

    def addProduction(self, prod):
        self.prods.append(prod)

    def code(self):
        ret = ['\nclass PGParser:',
                '   def __init__(self, lexer):',
                '      self.lexer = lexer',
                '      self.lexer.getTok()']

        for prod in self.prods:
            ret = ret + ['\n']
            try:
                ret = ret + indent(prod.code())
            except:
                print prod.name, prod.code()

        ret = ret + ['\n   def error(self):',
                     '      import sys',
                     '      print "Error! Aborting."',
                     '      sys.exit(0)']

        return ret

    def getTerminals(self):
        ret = []
        for prod in self.prods:
            ret = ret + prod.getTerminals()
        return ret

    def writeLexer(self, file):
        def eliminateDuplicates(list):
            d = {}
            for e in list:
                d[e] = e
            return d.keys()

        terms = eliminateDuplicates(self.getTerminals())
         
        file.write("\nlexemeTable = [(%sPatt, %s),\n" %(terms[0], terms[0]))
        for term in terms[1:len(terms)-1]:
            file.write("   (%sPatt, %s),\n" % (term, term))
        file.write("   (%sPatt, %s)]\n\n" % (terms[len(terms)-1], terms[len(terms)-1]))

        f = open('PGenLexerStub.txt', 'r')
        file.write(f.read())
        f.close()

    def writeParser(self, file):
        self.writePreface(file)

        self.writeLexer(file)
        for line in self.code():
            file.write(line + '\n')

        self.writePostface(file)

    def writePreface(self, file):
        file.write(self.preface)

    def writePostface(self, file):
        file.write(self.postface)
