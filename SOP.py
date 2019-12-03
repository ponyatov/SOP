
import os,sys

############################################# Marvin Minsky extended frame model

class Frame:
    def __init__(self,V,I=False):
        self.type  = self.__class__.__name__.lower()
        self.val   = V
        self.slot  = {}
        self.nest  = []
        self.immed = I

    ################################### dump

    def __repr__(self): return self.dump()
    # full tree dump
    def dump(self,depth=0,prefix=''):
        tree = self._pad(depth) + self.head(prefix)
        # block infinitive recursion on cycles
        if not depth: Frame._dump = []
        if self in Frame._dump: return tree + ' _/'
        else: Frame._dump.append(self)
        # slot{}s
        for i in self.slot:
            tree += self.slot[i].dump(depth+1,'%s = '%i)
        # nest[]ed
        idx = 0
        for j in self.nest:
            tree += j.dump(depth+1,'%i: '%idx) ; idx += 1
        # subtree dump
        return tree
    # short <T:V> header
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix,self.type,self._val(),id(self))
    def _pad(self,depth):
        return '\n' + ' '*4 * depth
    def _val(self):
        return str(self.val)

    ############################## operators

    # A[key]
    def __getitem__(self,key):
        return self.slot[key]
    # A[key] = B
    def __setitem__(self,key,that):
        if callable(that): self[key] = Cmd(that) ; return self
        assert isinstance(that,Frame)
        self.slot[key] = that ; return self
    # A << B -> A[B.type] = B
    def __lshift__(self,that):
        assert isinstance(that,Frame)
        self[that.type] = that; return self
    # A >> B -> A[B.val] = B
    def __rshift__(self,that):
        if callable(that): self[that.__name__] = Cmd(that) ; return self
        assert isinstance(that,Frame)
        self[that.val ] = that; return self
    # A // B
    def __floordiv__(self,that):
        assert isinstance(that,Frame)
        self.nest.append(that) ; return self

    ############################## stack ops

    # ( a -- a )
    def top(self): return self.nest[-1]
    # ( a b -- a )
    def pop(self): return self.nest.pop(-1)
    # ( a b -- )
    def dot(self): self.nest = []

    ############################## execution

    def eval(self,ctx): ctx // self

###################################################################### primitive

class Primitive(Frame):     pass
class Symbol(Primitive):    pass
class String(Primitive):    pass
class Number(Primitive):    pass

################################################# EDS: Executable Data Structure

class Active(Frame):        pass
class VM(Active):           pass
class Cmd(Active):
    def __init__(self,F,I=False):
        assert callable(F)
        Active.__init__(self,F.__name__,I)
        self.fn = F
    def eval(self,ctx): self.fn(ctx)

################################################################ Virtual Machine

vm = VM('Smalltalk') ; vm << vm

def bye(ctx): sys.exit(0)
vm >> bye

########################################################################## debug

def at(ctx): print(ctx)
vm['@'] = at

def atat(ctx): print(ctx) ; bye(ctx)
vm['@@'] = atat

################################################################## manupulations

def eq(ctx): addr = ctx.pop().val ; ctx[addr] = ctx.pop()
vm['='] = eq

############################################################### no-syntax parser

import ply.lex as lex

tokens = ['string','symbol']

t_ignore         = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

states = (('str','exclusive'),)

t_str_ignore = ''

def t_str(t):
    r"'"
    t.lexer.push_state('str') ; t.lexer.string = ''
def t_str_str(t):
    r"'"
    t.lexer.pop_state() ; return String(t.lexer.string)
def t_str_any(t):
    r"."
    t.lexer.string += t.value

def t_symbol(t):
    r'[`]|[^ \t\r\n\#\\]+'
    return Symbol(t.value)

def t_ANY_error(t): raise SyntaxError(t)

#################################################################### interpreter

def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token
vm['`'] = WORD

def FIND(ctx):
    token = ctx.pop()
    try:             ctx // ctx[token.val] ; return True
    except KeyError: ctx // token          ; return False

def EVAL(ctx): ctx.pop().eval(ctx)

def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if isinstance(ctx.top(),Symbol):
            if not FIND(ctx): raise SyntaxError(ctx.top())
        EVAL(ctx)

############################################################################# IO

class IO(Frame):            pass

##################################################################### networking

class Net(IO):              pass
class IP(Net):              pass
class Port(Net):            pass

def ip(ctx): ctx // IP(ctx.pop().val)
vm >> ip

def port(ctx): ctx // Port(ctx.pop().val)
vm >> port

#################################################################### documenting

class Doc(Frame):           pass
class Color(Doc):           pass
class Font(Doc):            pass
class Size(Doc,Number):     pass

def color(ctx): ctx // Color(ctx.pop().val)
vm >> color

def font(ctx): ctx // Font(ctx.pop().val)
vm >> font

def size(ctx): ctx // Size(ctx.pop().val)
vm >> size

################################################################## Web interface

def WEB(ctx):

    import flask
    web = flask.Flask(vm.val)

    @web.route('/')
    def index(): return flask.render_template('index.html',vm=vm)

    @web.route('/css.css')
    def css(): return flask.Response(flask.render_template('css.css',vm=vm),mimetype='text/css')

    @web.route('/<path:path>.png')
    def png(path): return flask.Response(web.send_static_file(path+'.png'),mimetype='image/png')

    web.run(host=vm['HOST'].val,port=vm['PORT'].val,debug=True,extra_files=sys.argv[1:])

vm >> WEB

#################################################################### system init

if __name__ == '__main__':
    for i in sys.argv[1:]:
        with open(i) as src:
            vm // String(src.read()) ; INTERP(vm)
