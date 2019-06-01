
import plex

class RunError(Exception):
    pass
class ParseError(Exception):
    pass

class MyParser:
    def __init__(self):
        letter = plex.Range('azAZ')
        digit = plex.Range('09')
        digit1 = plex.Range('01')
        andop = plex.Str('and')
        orop = plex.Str('or')
        xorop = plex.Str('xor')
        name = letter + plex.Rep(letter|digit)
        space = plex.Any(' \n\t')
        Keyword = plex.Str('print','PRINT')
        binary= plex.Rep1(digit)
        equals = plex.Str( '=')
        par = plex.Str('(')
        parr = plex.Str(')')
        
        self.vL={}
        self.lexicon = plex.Lexicon([
            (Keyword, 'PRINT_TOKEN'),
            (andop, plex.TEXT),
            (orop, plex.TEXT),
            (xorop, plex.TEXT),
            (name, 'ID_TOKEN'),             
            (binary, 'BINARY'),
            (equals, '='),
            (par, '('),
            (parr, ')'),
            (space, plex.IGNORE)			
        ])

    def createScanner(self,fp):
        self.scanner = plex.Scanner(self.lexicon,fp)
        self.la,self.text = self.next_token()
    
    def next_token(self):
        return self.scanner.read()


    def match(self,token):
        if self.la == token:
            self.la,self.text = self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la,token))
            

    def parse(self,fp):
        self.createScanner(fp)
        self.stmt_list()
        
    def stmt_list(self):
        if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
            self.stmt()
            self.stmt_list()
        elif self.la == None: 
            return
        else: 
            raise ParseError('Expected id or print')
            
    def stmt(self):
        if self.la == 'ID_TOKEN': 
            varname = self.text
            self.match('ID_TOKEN')
            self.match('=')
            e = self.expr()
            self.vL[varname] = e
            return {'type' : '=', 'text' : varname, 'expr' : e}
        elif self.la == 'PRINT_TOKEN': 
            self.match('PRINT_TOKEN')
            e = self.expr()
            print('= {:b}'.format(e))
            return {'type' : 'print' , 'expr' : e}
        else: 
            raise ParseError('Expected id or print')
    
    def expr(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY': 
            t = self.term()
            while self.la == 'xor':
                self.match('xor')
                t2 = self.term()
                print('xor : {:b} ^ {:b} '.format(t,t2))
                t = t^t2
            if self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return t
            raise ParseError('Expected xor operator')
        else: 
            raise ParseError('Expected par, id or a binary number')
            
    def term(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY': 
            f = self.factor()
            while self.la == 'or':
                self.match('or')
                f2 = self.factor()
                print('or : {:b} or {:b} '.format(f,f2))
                f = f|f2
            if self.la == ')' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return f
            raise ParseError('Expected | operator')
        else: 
            raise ParseError('Expected par, id or a binary number')
            
    def factor(self):
        if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY': 
            a = self.atom()
            while self.la == 'and':
                self.match('and')
                a2 = self.atom()
                print('and : {:b} and {:b} '.format(a,a2))
                a = a&a2
            if self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
                return a
            raise ParseError('Expected & operator')
        else: 
            raise ParseError('Expected par, an operation or a binary number')
            
    def atom(self):
        if self.la == '(': 
            self.match('(')
            e = self.expr()
            self.match(')')
            return(e)
        elif self.la == 'ID_TOKEN':
            varname = self.text
            self.match('ID_TOKEN')
            if varname in self.vL:
                return self.vL[varname]
            raise RunError("no variable name")
        elif self.la == 'BINARY' :
            binary_num = int(self.text,2)
            self.match('BINARY')
            return (binary_num)
        else: 
            raise ParseError('Expected par, id or a binary number')
    
parser = MyParser()

with open('test.txt', 'r') as fp:
    parser.parse(fp)
