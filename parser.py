
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
		andop = plex.Range('and')
		orop = plex.Range('or')
		xorop = plex.Range('xor')
		name = letter + plex.Rep(letter|digit)
		space = plex.Any(' \n\t')

		Keyword = plex.Str('print','PRINT')
		binary = plex.Rep(digit) +plex.Str('.') + plex.Rep1(digit)
		equals = plex.Str('=')
		par = plex.Str('(')
		parr = plex.Str(')')
		
		self.vL = {}

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
		self.la , self.text = self.next_token()

	def next_token(self):
		return self.scanner.read()
	
	def match(self,token):
		if self.la == token:
			self.la, self.text = self.next_token()
		else:
			raise ParseError(" waiting for something to be received ")

	def parse(self,fp):
		self.createScanner(fp)
	#	while self.la:
    #			print(self.la, self.text)
    #			self.la, self.text = self.next_token()
		self.stmt_list()

	def stmt_list(self):
		if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:  
			raise ParseError("Expected id or print")
	
			
	def stmt(self):
		if self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			self.match('=')
			e = self.expr()
			self.vL[varname] = e
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			self.expr()
		else:
			raise ParseError("Expected id or print")
	
			
	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY': 
			self.term()
			self.term_tail()
		elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == None or self.la == 'PRINT_TOKEN':
			return self.term()
		else:
			raise ParseError("Expected par, id or a binary number")
			
	def term_tail(self):
		if self.la == 'xor': 
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la == ')' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None:
			return
		else:
			raise ParseError("Expected an operation") 
		
	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("Expected par, id or a binary number") 

	def factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la == ')' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == None:
			return
		else:
			raise ParseError("Expected an operation") 

	def factor(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'BINARY':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("Expecting par, id or a bin number.")
		
	
	
	def atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None: 
			return
		else: 
			raise ParseError('Expected an operation')
	
	def atom(self):
		if self.la == '(' :
			self.match('(')
			e = self.expr()
			self.match(')')
			return(e)
		elif self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			if varname in self.vL:
				return self.vL[varname]
			raise RunError("no value")
		elif self.la == 'BINARY':
			binary = self.text
			self.match('BINARY')
			return binary
		else:
			raise ParseError('Expected par, id or a bin number')
			
parser = MyParser()

with open('test.txt', 'r') as fp:
	parser.parse(fp)

