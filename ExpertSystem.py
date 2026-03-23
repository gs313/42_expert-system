import re

def to_rpn(expression):
    precedence = {'!': 4, '+': 3, '|': 2, '^': 1}
    output = []
    stack = []
    
    tokens = re.findall(r'[A-Z]|\!|\+|\^|\||\(|\)', expression)
    
    for token in tokens:
        if token.isupper():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop() 
        else:
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(token, 0):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())
    return output

def evaluate_rpn(rpn_list, solve_func):
    print(rpn_list)
    stack = []
    for token in rpn_list:
        if token.isupper():
            stack.append(solve_func(token))
            
        elif token == '!':
            val = stack.pop()
            if val is None:
                stack.append(None)
            else:
                stack.append(not val)
                
        elif token == '+':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 is False or v2 is False:
                stack.append(False)
            elif v1 is None or v2 is None:
                stack.append(None)
            else:
                stack.append(True)
                
        elif token == '|':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 is True or v2 is True:
                stack.append(True)
            elif v1 is None or v2 is None:
                stack.append(None)
            else:
                stack.append(False)
                
        elif token == '^':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 is None or v2 is None:
                stack.append(None)
            else:
                stack.append(v1 ^ v2)
                
    return stack[0] if stack else False

import itertools

def resolve_complex_conclusion(conclusion_str, target, get_val_func):
    vars_in_conc = list(set(re.findall(r'[A-Z]', conclusion_str)))
    if len(vars_in_conc) == 1 and vars_in_conc[0] == target:
        return True
        
    rpn = to_rpn(conclusion_str)
    known_values = {}

    for v in vars_in_conc:
        if v != target:
            val = get_val_func(v)
            if val is not True:
                val = None
            known_values[v] = val
            
    valid_states_for_target = set()
    
    for combo in itertools.product([True, False], repeat=len(vars_in_conc)):
        state = dict(zip(vars_in_conc, combo))
        conflict = False
        
        for v in vars_in_conc:
            if v != target:
                if known_values[v] is True and state[v] is False:
                    conflict = True
                    break
                    
        if conflict:
            continue
            
        if evaluate_rpn(rpn, lambda x: state[x]) is True:
            valid_states_for_target.add(state[target])
            
    if len(valid_states_for_target) == 1:
        return valid_states_for_target.pop()
    return None

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
        if "<=>" in rule_str:
            lhs, rhs = rule_str.split("<=>")
            lhs, rhs = lhs.strip(), rhs.strip()
            self.rules.append((lhs, rhs))
            self.rules.append((rhs, lhs)) 

        elif "=>" in rule_str:
            lhs, rhs = rule_str.split("=>")
            self.rules.append((lhs.strip(), rhs.strip()))
    
    def solve(self, target, visited=None, depth=0, ignored_rule=None, silent=False):
        def log(msg):
            if not silent:
                print(msg)
                
        indent = "  " * depth
        
        if target in self.facts:
            log(f"{indent}✔ {target} is True (Initial Fact)")
            return True
        
        if visited and target in visited:
            log(f"{indent}⚠ {target} is False (Circular logic detected)")
            return False

        visited = visited or set()
        visited.add(target)
        
        found_rule = False
        possible_results = []
        explicit_false = False

        for condition, conclusion in self.rules:
            if (condition, conclusion) == ignored_rule:
                continue
                
            if target in re.findall(r'[A-Z]', conclusion):
                found_rule = True
                log(f"{indent}➤ To prove {target}, trying rule: {condition} => {conclusion}")

                res = evaluate_rpn(to_rpn(condition), lambda t: self.solve(t, visited.copy(), depth + 1, silent=silent))
                
                if res is True:
                    if '|' in conclusion or '^' in conclusion:
                        log(f"{indent}  ➤ Condition is True. Evaluating complex conclusion: {conclusion}")
                        
                        vars_in_conc = list(set(re.findall(r'[A-Z]', conclusion)))
                        known_values = {}

                        for v in vars_in_conc:
                            if v != target:
                                log(f"{indent}    ➤ Checking if '{v}' is forced to True by other rules...")
                                
                                val = self.solve(v, visited.copy(), depth + 3, ignored_rule=(condition, conclusion), silent=True)
                                
                                if val is True:
                                    log(f"{indent}    ✔ '{v}' is explicitly forced to True by another rule.")
                                else:
                                    log(f"{indent}    ⚠ '{v}' is not forced by other rules (Treating as flexible/Undetermined).")
                                    val = None
                                known_values[v] = val
                        
                        rpn = to_rpn(conclusion)
                        valid_states = set()
                        import itertools
                        for combo in itertools.product([True, False], repeat=len(vars_in_conc)):
                            state = dict(zip(vars_in_conc, combo))
                            conflict = False
                            for v in vars_in_conc:
                                if v != target and known_values[v] is True and state[v] is False:
                                    conflict = True
                                    break
                            if conflict:
                                continue
                                
                            if evaluate_rpn(rpn, lambda x: state[x]) is True:
                                valid_states.add(state[target])
                                
                        if len(valid_states) == 1:
                            final_val = valid_states.pop()
                            if final_val is True:
                                log(f"{indent}✔ {target} MUST be True to satisfy '{conclusion}'")
                                possible_results.append(True)
                            else:
                                log(f"{indent}✘ {target} MUST be False to satisfy '{conclusion}'")
                                explicit_false = True
                                possible_results.append(False)
                        else:
                            log(f"{indent}⚠ {target} is Undetermined (Ambiguous conclusion '{conclusion}')")
                            possible_results.append(None)
                    else:
                        log(f"{indent}✔ {target} is True (Condition '{condition}' is met)")
                        possible_results.append(True)
                elif res is None:
                    log(f"{indent}⚠ {target} is Undetermined (Condition '{condition}' cannot be fully determined)")
                    possible_results.append(None)

        if True in possible_results:
            return True
        if None in possible_results:
            return None

        if explicit_false:
            log(f"{indent}✘ {target} is False (Proven mathematically by the rule)")
        elif not found_rule:
            log(f"{indent}✘ {target} is False (No supporting facts or rules)")
        else:
            log(f"{indent}✘ {target} is False (All supporting rules failed)")
            
        return False