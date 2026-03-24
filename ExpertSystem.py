import re
import sys


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
    stack = []

    # ฟังก์ชันช่วยเช็คว่าเป็นเท็จ (ครอบคลุมทั้ง "F" แท้ และ "df")
    def is_f(val):
        return val in ("F", "df")

    for token in rpn_list:
        if token.isupper():
            stack.append(solve_func(token))
        elif token == '!':
            val = stack.pop()
            if val == "N":
                stack.append("N")
            elif is_f(val):
                stack.append("T")
            else:
                stack.append("F")

        elif token == '+':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 == "F" or v2 == "F":
                stack.append("F")
            elif v1 == "df" or v2 == "df":
                stack.append("df")
            elif v1 == "N" or v2 == "N":
                stack.append("N")
            else:
                stack.append("T")

        elif token == '|':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 == "T" or v2 == "T":
                stack.append("T")
            elif v1 == "N" or v2 == "N":
                stack.append("N")
            elif v1 == "F" or v2 == "F":
                if v1 == "df" or v2 == "df":
                    stack.append("df")
                else:
                    stack.append("F")
            else:
                stack.append("df")

        elif token == '^':
            v2 = stack.pop()
            v1 = stack.pop()
            if v1 == "N" or v2 == "N":
                stack.append("N")
            else:
                b1 = False if is_f(v1) else True
                b2 = False if is_f(v2) else True
                stack.append("F" if b1 == b2 else "T")

    return stack[0] if stack else "df"

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

    def reset_facts(self):
        self.facts.clear()

    def set_facts(self, fact_str):
        self.reset_facts()
        self.add_fact(fact_str)

    def toggle_fact(self, fact):
        if fact in self.facts:
            self.facts.remove(fact)
            return False
        else:
            self.facts.add(fact)
            return True


    def solve(self, target, visited=None, depth=0, ignored_rule=None, silent=False):
        def log(msg):
            if not silent:
                print(msg)

        indent = "  " * depth

        if target in self.facts:
            log(f"{indent}✔ {target} is True (Initial Fact)")
            return "T"
        if visited and target in visited:
            print(f"{indent}⚠ {target} is False (Circular logic detected)")
            return "df"

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
                print(f"{indent}➤ To prove {target}, trying rule: {condition} => {conclusion}")

                res = evaluate_rpn(to_rpn(condition), lambda t: self.solve(t, visited.copy(), depth + 1, silent=silent))

                if res == "T":
                    if conclusion.strip() != target:
                        log(f"{indent}  ➤ Condition is True. Evaluating complex conclusion: {conclusion}")

                        vars_in_conc = list(set(re.findall(r'[A-Z]', conclusion)))
                        known_values = {}

                        for v in vars_in_conc:
                            if v != target:
                                log(f"{indent}    ➤ Checking if '{v}' is forced to True/False by other rules...")
                                val = self.solve(v, visited.copy(), depth + 3, ignored_rule=(condition, conclusion), silent=True)

                                if val == "T":
                                    log(f"{indent}    ✔ '{v}' is explicitly forced to True.")
                                elif val == "F":
                                    log(f"{indent}    ✔ '{v}' is explicitly forced to False by another rule.")
                                else:
                                    log(f"{indent}    ⚠ '{v}' is flexible (No strict proof). Treating as Undetermined.")
                                    val = "N"
                                known_values[v] = val

                        rpn = to_rpn(conclusion)
                        valid_states = set()

                        for combo in itertools.product(["T", "F"], repeat=len(vars_in_conc)):
                            state = dict(zip(vars_in_conc, combo))
                            conflict = False
                            for v in vars_in_conc:
                                if v != target and known_values[v] != "N" and known_values[v] != state[v]:
                                    conflict = True
                                    break
                            if conflict:
                                continue

                            if evaluate_rpn(rpn, lambda x: state[x]) == "T":
                                valid_states.add(state[target])

                        if len(valid_states) == 1:
                            final_val = valid_states.pop()
                            if final_val == "T":
                                log(f"{indent}✔ {target} MUST be True to satisfy '{conclusion}'")
                                possible_results.append("T")
                            else:
                                log(f"{indent}✘ {target} MUST be False to satisfy '{conclusion}'")
                                explicit_false = True
                                possible_results.append("F")
                            if "T" in possible_results and "F" in possible_results:
                                log(f"{indent}  CONTRADICTION DETECTED: '{target}' is proven to be BOTH True and False!")
                                log(f"{indent}  System cannot resolve this paradox. Halting evaluation.")
                                print(f"Contradiction Error: '{target}' has conflicting Truth values.")
                                sys.exit()
                        else:
                            log(f"{indent}⚠ {target} is Undetermined (Ambiguous conclusion '{conclusion}')")
                            possible_results.append("N")
                    else:
                        log(f"{indent}✔ {target} is True (Condition '{condition}' is met)")
                        possible_results.append("T")

                elif res == "N":
                    log(f"{indent}⚠ {target} is Undetermined (Condition '{condition}' cannot be fully determined)")
                    possible_results.append("N")
                elif res == "F":
                    log(f"{indent}✘ Rule skipped: Condition '{condition}' is strictly FALSE.")
                elif res == "df":
                    log(f"{indent}✘ Rule skipped: Condition '{condition}' lacks supporting facts (Default False).")

        if "T" in possible_results:
            return "T"
        if "N" in possible_results:
            return "N"

        if explicit_false:
            print(f"{indent}✘ {target} is False (Proven mathematically by the rule)")
            return "F"
        elif not found_rule:
            print(f"{indent}✘ {target} is False (No supporting facts or rules)")
            return "df"
        else:
            print(f"{indent}✘ {target} is False (All supporting rules failed)")
            return "df"
