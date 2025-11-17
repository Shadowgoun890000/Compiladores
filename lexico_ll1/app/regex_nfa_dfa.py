from dataclasses import dataclass
from typing import Set, Dict, FrozenSet, List, Optional

# NFA state
class NFAState:
    __slots__=("eps","trans","accepts")
    def __init__(self):
        self.eps:set[NFAState]=set()
        self.trans:dict[str,set[NFAState]]={}
        self.accepts:set[str]=set()

@dataclass
class NFA:
    start: NFAState
    end: NFAState

# Simple regex builder: literals, ., [], ranges, escapes, (), |, *, +, ?
class RegexParseError(Exception): pass

class RegexBuilder:
    def __init__(self, p:str): self.p=p; self.i=0; self.n=len(p)
    def peek(self): return self.p[self.i] if self.i<self.n else ""
    def get(self): ch=self.peek(); self.i+=1; return ch

    def parse(self)->NFA:
        n=self.alt()
        if self.i!=self.n: raise RegexParseError(f"Unexpected at {self.i}")
        return n

    def alt(self)->NFA:
        a=self.concat()
        while self.peek()=="|":
            self.get(); b=self.concat(); a=self._alt(a,b)
        return a

    def concat(self)->NFA:
        parts=[]
        while self.peek() and self.peek() not in ")|":
            parts.append(self.repeat())
        if not parts:
            s1,s2=NFAState(),NFAState(); s1.eps.add(s2); return NFA(s1,s2)
        n=parts[0]
        for p in parts[1:]: n=self._concat(n,p)
        return n

    def repeat(self)->NFA:
        u=self.atom()
        while self.peek() in "*+?":
            op=self.get()
            if op=="*": u=self._star(u)
            elif op=="+": u=self._plus(u)
            else: u=self._opt(u)
        return u

    def atom(self)->NFA:
        ch=self.peek()
        if ch=="(":
            self.get(); inside=self.alt()
            if self.get()!=")": raise RegexParseError("Unmatched (")
            return inside
        if ch=="[":
            self.get(); chars=set(); neg=False
            if self.peek()=="^": neg=True; self.get()
            while self.peek() and self.peek()!="]":
                a=self._esc()
                if self.peek()=="-" and self.p[self.i+1]!="]":
                    self.get(); b=self._esc()
                    for c in range(ord(a),ord(b)+1): chars.add(chr(c))
                else: chars.add(a)
            if self.get()!="]": raise RegexParseError("Unmatched [")
            if neg:
                universe=set(chr(c) for c in range(32,127))
                chars=universe-chars
            return self._class(chars)
        if ch==".":
            self.get(); chars=set(chr(c) for c in range(32,127))
            return self._class(chars)
        if ch=="\\": a=self._esc(); return self._lit(a)
        if not ch:
            s1,s2=NFAState(),NFAState(); s1.eps.add(s2); return NFA(s1,s2)
        self.get(); return self._lit(ch)

    def _esc(self)->str:
        ch=self.get()
        if ch!="\\": return ch
        m={"n":"\n","t":"\t","r":"\r","\\":"\\",'"':'"',"[":"[","]":"]","(":"(",")":")","|":"|","?":"?","*":"*","+":"+"}
        return m.get(self.get(), ch)

    def _lit(self,ch:str)->NFA:
        s1,s2=NFAState(),NFAState(); s1.trans.setdefault(ch,set()).add(s2); return NFA(s1,s2)
    def _class(self,chs:Set[str])->NFA:
        s1,s2=NFAState(),NFAState()
        for c in chs: s1.trans.setdefault(c,set()).add(s2)
        return NFA(s1,s2)
    def _concat(self,a:NFA,b:NFA)->NFA: a.end.eps.add(b.start); return NFA(a.start,b.end)
    def _alt(self,a:NFA,b:NFA)->NFA:
        s,e=NFAState(),NFAState(); s.eps.update([a.start,b.start]); a.end.eps.add(e); b.end.eps.add(e); return NFA(s,e)
    def _star(self,a:NFA)->NFA:
        s,e=NFAState(),NFAState(); s.eps.update([a.start,e]); a.end.eps.update([a.start,e]); return NFA(s,e)
    def _plus(self,a:NFA)->NFA:
        s,e=NFAState(),NFAState(); s.eps.add(a.start); a.end.eps.update([a.start,e]); return NFA(s,e)
    def _opt(self,a:NFA)->NFA:
        s,e=NFAState(),NFAState(); s.eps.update([a.start,e]); a.end.eps.add(e); return NFA(s,e)

def epsilon_closure(states:Set[NFAState])->Set[NFAState]:
    st=list(states); res=set(states)
    while st:
        s=st.pop()
        for t in s.eps:
            if t not in res: res.add(t); st.append(t)
    return res

def move(states:Set[NFAState], ch:str)->Set[NFAState]:
    out=set()
    for s in states:
        if ch in s.trans: out.update(s.trans[ch])
    return out

from dataclasses import dataclass
@dataclass(frozen=True)
class DFAState:
    id:int
    accepts:frozenset[str]

class DFA:
    def __init__(self):
        self.start:int=0
        self.state_list:list[DFAState]=[]
        self.trans:dict[int,dict[str,int]]={}
        self._map:dict[frozenset[NFAState],int]={}

    def build(self, start_nfa:NFAState, alphabet:set[str]):
        start=frozenset(epsilon_closure({start_nfa}))
        self._map[start]=0
        acc=frozenset().union(*(s.accepts for s in start))
        self.state_list.append(DFAState(0, frozenset(acc))); self.trans[0]={}
        work=[start]; sid=1
        while work:
            S=work.pop(); s_id=self._map[S]
            for ch in alphabet:
                T=frozenset(epsilon_closure(move(set(S),ch)))
                if not T: continue
                if T not in self._map:
                    self._map[T]=sid
                    acc=frozenset().union(*(t.accepts for t in T))
                    self.state_list.append(DFAState(sid, frozenset(acc)))
                    self.trans[s_id][ch]=sid; self.trans[sid]={}; work.append(T); sid+=1
                else:
                    self.trans[s_id][ch]=self._map[T]
        self.start=0

    def minimize(self):
        all_states=set(range(len(self.state_list)))
        groups:dict[frozenset[str],set[int]]={}
        for s in all_states:
            groups.setdefault(self.state_list[s].accepts,set()).add(s)
        P=list(groups.values()); W=[g.copy() for g in P]
        alphabet=set(ch for d in self.trans.values() for ch in d.keys())
        while W:
            A=W.pop()
            for c in alphabet:
                X={s for s in all_states if c in self.trans.get(s,{}) and self.trans[s][c] in A}
                newP=[]
                for Y in P:
                    inter=Y & X; diff=Y - X
                    if inter and diff:
                        newP.extend([inter,diff])
                        if Y in W: W.remove(Y); W.extend([inter,diff])
                        else: W.append(inter if len(inter)<=len(diff) else diff)
                    else: newP.append(Y)
                P=newP
        block={}
        for i,blk in enumerate(P):
            for s in blk: block[s]=i
        new_states=[]; new_trans={i:{} for i in range(len(P))}
        for i,blk in enumerate(P):
            rep=next(iter(blk)); acc=frozenset()
            for s in blk: acc=acc | self.state_list[s].accepts
            new_states.append(DFAState(i,acc))
        for s,outs in self.trans.items():
            bs=block[s]
            for ch,t in outs.items(): new_trans[bs][ch]=block[t]
        self.state_list=new_states; self.trans=new_trans; self.start=block[self.start]

    def to_dot(self, path:str):
        def esc(x:str):
            if x=='"': return r'\"'
            if x=="\\": return r'\\'
            if x=="\n": return r'\\n'
            return x
        with open(path,"w",encoding="utf-8") as f:
            f.write("digraph DFA {\n  rankdir=LR;\n  node [shape=circle];\n")
            f.write(f"  __start__ [shape=point];\n  __start__ -> S{self.start};\n")
            for i,st in enumerate(self.state_list):
                shape="doublecircle" if st.accepts else "circle"
                acc=sorted(list(st.accepts))[:4]; extra="" if len(st.accepts)<=4 else ",…"
                label=f"S{i}" if not st.accepts else f"S{i}\\n[{', '.join(acc)}{extra}]"
                f.write(f'  S{i} [shape={shape}, label="{label}"];\n')
            for s,outs in self.trans.items():
                by={}
                for ch,t in outs.items(): by.setdefault(t,[]).append(ch)
                for t,chs in by.items():
                    lab=",".join(esc(c) for c in sorted(chs))
                    f.write(f'  S{s} -> S{t} [label="{lab}"];\n')
            f.write("}\n")

def build_token_nfa()->NFAState:
    patterns={
        "STRING": r'"[^"\n]*"',
        "NUM": r'((([0-9]+)?\.[0-9]+)|([0-9]+))([eE][+\-]?[0-9]+)?',
        "ID": r'[A-Za-z_][A-Za-z_0-9]*',
        "WS": r'[ \t\r\n]+',
        "COMMENT": r'//[^\n]*',
    }
    # Operators
    ops=["==","!=", "<=", ">=", "||", "&&","{","}","(",")","[","]",";",
         ",",".","=","<",">","+","-","*","/","%","!"]
    super_start=NFAState()
    for name,pat in patterns.items():
        n=RegexBuilder(pat).parse(); n.end.accepts.add(name); super_start.eps.add(n.start)
    for op in ops:
        esc="".join(("\\"+c) if c in r'[](){}.*+?|^$\/' else c for c in op)
        n=RegexBuilder(esc).parse(); n.end.accepts.add(op); super_start.eps.add(n.start)
    return super_start

def build_min_dfa()->DFA:
    start=build_token_nfa()
    alphabet=set(chr(c) for c in range(32,127)) | {"\n","\t","\r"}
    d=DFA(); d.build(start, alphabet); d.minimize(); return d
