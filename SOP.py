
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

