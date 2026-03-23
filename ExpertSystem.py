import re

def to_rpn(expression):
    # กำหนดลำดับความสำคัญ
    precedence = {'!': 4, '+': 3, '|': 2, '^': 1}
    output = []
    stack = []
    
    tokens = re.findall(r'[A-Z]|\!|\+|\^|\||\(|\)', expression)
    print("0000", tokens)
    for token in tokens:
        if token.isupper():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(token, 0):
                output.append(stack.pop())
            stack.append(token)
    print("sss", stack)
    while stack:
        output.append(stack.pop())
    return output

def evaluate_rpn(rpn_list, solve_func):
    print(rpn_list)
    print(solve_func)
    stack = []
    for token in rpn_list:
        if token.isupper():
            stack.append(solve_func(token))
        elif token == '!':
            val = stack.pop()
            stack.append(not val)
        elif token == '+':
            val2 = stack.pop()
            val1 = stack.pop()
            stack.append(val1 and val2)
        elif token == '|':
            val2 = stack.pop()
            val1 = stack.pop()
            stack.append(val1 or val2)
        elif token == '^':
            val2 = stack.pop()
            val1 = stack.pop()
            stack.append(val1 ^ val2)
            
    return stack[0] if stack else False

class ExpertSystem:
    def __init__(self):
        self.rules = []
        self.facts = set()
        self.queries = []

    def add_fact(self, fact_str):
        for char in fact_str:
            if char.isupper():
                self.facts.add(char)

    def add_rule(self, rule_str):
        if "=>" in rule_str:
            lhs, rhs = rule_str.split("=>")
            self.rules.append((lhs.strip(), rhs.strip()))
    
    def solve(self, target, visited=None):
        if visited is None: visited = set()
        if target in self.facts: return True
        if target in visited: return False
        
        visited.add(target)
        

        for condition_str, conclusion_str in self.rules:
            if target in conclusion_str:
                rpn = to_rpn(condition_str)
                if evaluate_rpn(rpn, lambda t: self.solve(t, visited.copy())):
                    return True
                
        return False