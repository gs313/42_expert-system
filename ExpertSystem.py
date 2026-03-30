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

    # "T"  = True (proven)
    # "F"  = Default False (no info)
    # "N"  = Unknown (ambiguous)
    # "CF" = Constrained False (ถูกบังคับ)

    for token in rpn_list:
        if token.isupper():
            stack.append(solve_func(token))
        elif token == '!':
            val = stack.pop()

            if val == "T":
                stack.append("CF")
            elif val == "CF":
                stack.append("T")
            elif val == "N":
                stack.append("N")
            else:
                stack.append("N")

        elif token == '+':
            v1 = stack.pop()
            v2 = stack.pop()

            if "CF" in (v1, v2):
                stack.append("CF")
            elif "F" in (v1, v2):
                stack.append("F")
            elif "N" in (v1, v2):
                stack.append("N")
            else:
                stack.append("T")

        elif token == '|':
            v1 = stack.pop()
            v2 = stack.pop()

            if "T" in (v1, v2):
                stack.append("T")
            elif "N" in (v1, v2):
                stack.append("N")
            elif "CF" in (v1, v2):
                stack.append("CF")
            else:
                stack.append("F")

        elif token == '^':
            v1 = stack.pop()
            v2 = stack.pop()

            if "N" in (v1, v2):
                stack.append("N")
            elif "F" in (v1, v2):
                stack.append("N")
            else:
                b1 = (v1 == "T")
                b2 = (v2 == "T")
                stack.append("T" if b1 != b2 else "CF")

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

    for combo in itertools.product(["T", "F"], repeat=len(vars_in_conc)):
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

class ReasonerLogger:
    def __init__(self):
        self.logs = []

    def log(self, depth, message):
        indent = "  " * depth

        display_msg = message.replace("CF", "F")

        self.logs.append(f"{indent}{display_msg}")

    def dump(self):
        return "\n".join(self.logs)


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

    def prove(self, target, visited, depth=0, logger=None):
        if logger:
            logger.log(depth, f"Proving {target}")

        if target in self.facts:
            if logger:
                logger.log(depth, f"✔ {target} is True (fact)")
            return "T"

        if target in visited:
            if logger:
                logger.log(depth, f"⚠ Loop on {target} → Unknown")
            return "N"

        visited.add(target)

        results = set()
        has_rule = False

        for condition, conclusion in self.rules:
            if target not in re.findall(r'[A-Z]', conclusion):
                continue

            has_rule = True

            if logger:
                logger.log(depth + 1, f"➤ Rule: {condition} => {conclusion}")

            cond_val = self.eval_condition(condition, visited.copy(), depth + 1, logger)

            if cond_val != "T":
                if logger:
                    logger.log(depth + 1, f"✘ Condition is not True ({cond_val})")
                continue

            val = self.resolve_conclusion(conclusion, target, visited.copy(), depth + 2, logger)

            if val in ("T", "CF"):
                results.add(val)

            elif val == "N":
                results.add("N")

        if len(results) == 0:
            if logger:
                if not has_rule:
                    logger.log(depth, f"✘ {target} = F (no rule)")
                    return "F"
                else:
                    logger.log(depth, f"✘ {target} = F (no valid rule)")
                    return "N"
            return "F"

        if len(results) == 1:
            val = next(iter(results))
            if logger:
                if val == "T":
                    logger.log(depth, f"✔ {target} must be True")
                elif val == "CF":
                    logger.log(depth, f"✔ {target} must be False")
                else:
                    logger.log(depth, f"⚠ {target} is Unknown")
            return val

        if logger:
            logger.log(depth, f"⚠ {target} is Undetermined (conflict: {results})")

        return "N"
    
    def eval_condition(self, expr, visited, depth=0, logger=None):
        rpn = to_rpn(expr)

        if logger:
            logger.log(depth, f"Eval condition: {expr}")

        def resolver(t):
            return self.prove(t, visited.copy(), depth + 1, logger)

        result = evaluate_rpn(rpn, resolver)

        if logger:
            logger.log(depth, f"→ Result: {result}")

        return result
    
    def solve(self, target):
        logger = ReasonerLogger()

        logger.log(0, f"Query {target}")

        result = self.prove(target, set(), 1, logger)

        if result == "T":
            final = "T"
        else:

            possible = set()

            for condition, conclusion in self.rules:
                if target not in re.findall(r'[A-Z]', conclusion):
                    continue

                res = self.eval_condition(condition, set())

                if res == "T":
                    val = self.resolve_conclusion(conclusion, target, set())
                    if val in ("T", "CF"):
                        possible.add(val)
                    elif val == "N":
                        possible.add("N")

        if result == "T":
            final = "T"

        elif len(possible) == 0:
            final = result

        elif len(possible) == 1:
            final = possible.pop()

        else:
            final = "N"

        logger.log(0, f"Result: {target} = {final}")

        print(logger.dump())
        return final
    
    def resolve_conclusion(self, conclusion, target, visited, depth=0, logger=None):
        if logger:
            logger.log(depth, f"Resolving: {conclusion}")

        if '+' in conclusion:
            parts = conclusion.split('+')
            parts = [p.strip() for p in parts]

            for p in parts:
                val = self.prove(p, visited.copy(), depth + 1, logger)

                if val == "F":
                    return None
                if p == target:
                    continue

            if target in parts:
                return "T"

        if conclusion.startswith('!') and len(conclusion) == 2:
            var = conclusion[1]
            val = self.prove(var, visited.copy(), depth + 1, logger)

            if var == target:
                if val == "T":
                    return "CF"
                if val == "CF":
                    return "T"

        rpn = to_rpn(conclusion)

        possible = set()
        for t_val in ["T", "CF"]:
            def resolver(x):
                if x == target:
                    return t_val
                return self.prove(x, visited.copy(), depth + 1, None)

            result = evaluate_rpn(rpn, resolver)

            if result == "T":
                possible.add(t_val)

        if logger:
            logger.log(depth, f"⇒ Possible {target}: {possible}")

        if len(possible) == 1:
            return possible.pop()

        if len(possible) > 1:
            return "N"

        return None