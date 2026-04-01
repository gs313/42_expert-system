import re
from collections import defaultdict
import itertools


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
            elif val == "F":
                stack.append("T")
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
            else:
                b1 = (v1 == "T")
                b2 = (v2 == "T")
                stack.append("T" if b1 != b2 else "CF")

    return stack[0]





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
        self.lines = []
        self.stack = []

        self.COLORS = {
            "RESET": "\033[0m",
            "GREEN": "\033[92m",
            "RED": "\033[91m",
            "YELLOW": "\033[93m",
            "CYAN": "\033[96m",
            "MAGENTA": "\033[95m",
            "BLUE": "\033[94m",
            "WHITE": "\033[97m",
            "RULE": "\033[94m",
        }

    # =========================
    # 🎨 Smart Color System
    # =========================
    def colorize(self, msg):
        msg = msg.replace("✔", f"{self.COLORS['GREEN']}✔")
        msg = msg.replace("✘", f"{self.COLORS['RED']}✘")
        msg = msg.replace("⚠", f"{self.COLORS['YELLOW']}⚠")
        msg = msg.replace("➤", f"{self.COLORS['CYAN']}➤")

        msg = msg.replace("= T", f"= {self.COLORS['GREEN']}T")
        msg = msg.replace("= F", f"= {self.COLORS['RED']}F")
        msg = msg.replace("= N", f"= {self.COLORS['YELLOW']}N")

        return msg

    # =========================
    # 🌳 Tree prefix
    # =========================
    def _prefix(self):
        prefix = ""
        for is_last in self.stack[:-1]:
            prefix += "    " if is_last else "│   "

        if self.stack:
            prefix += "└── " if self.stack[-1] else "├── "

        return prefix

    # =========================
    # 🧠 Core log
    # =========================
    def log(self, message, is_last=False):
        self.stack.append(is_last)

        line = self._prefix() + self.colorize(message.replace("CF", "F")) + self.COLORS['RESET']
        self.lines.append(line)

        self.stack.pop()
    def error(self, message):
        msg = f"{self.COLORS['RED']}{message}{self.COLORS['RESET']}"
        self.log(msg, is_last=False)

    def push(self, is_last=False):
        self.stack.append(is_last)

    def pop(self):
        if self.stack:
            self.stack.pop()

    # =========================
    # 🎯 Semantic logs (NEW)
    # =========================

    def query(self, target):
        self.lines.append(
            f"{self.COLORS['WHITE']}Query {target}{self.COLORS['RESET']}"
        )

    def rule(self, condition, conclusion, is_last=False):
        msg = f"➤ {self.COLORS['BLUE']}Rule: {self.COLORS['YELLOW']}{condition} => {conclusion} {self.COLORS['RESET']}"
        self.log(msg, is_last)

    def prove(self, target, is_last=False):
        msg = f"{self.COLORS['CYAN']}Proving:{self.COLORS['RESET']} {target}{self.COLORS['RESET']}"
        self.log(msg, is_last)
    def condition(self, expr, is_last=False):
        msg = f"{self.COLORS['CYAN']}Eval:{self.COLORS['RESET']} {expr}{self.COLORS['RESET']}"
        self.log(msg, is_last)

    def resolve(self, conclusion, is_last=False):
        msg = f"{self.COLORS['MAGENTA']}Resolving:{self.COLORS['RESET']} {conclusion}{self.COLORS['RESET']}"
        self.log(msg, is_last)

    def result(self, val, taget, is_last=False):
        if val == "T":
            msg = f"{self.COLORS['GREEN']}Result: {taget} = T{self.COLORS['RESET']}"
        elif val == "F":
            msg = f"{self.COLORS['RED']}Result: {taget} = F{self.COLORS['RESET']}"
        else:
            msg = f"{self.COLORS['YELLOW']}Result: {taget} = N{self.COLORS['RESET']}"
        self.log(msg, is_last)

    def possible(self, target, values, is_last=False):
        msg = f"{self.COLORS['MAGENTA']}Possible {target}:{self.COLORS['RESET']} {values}{self.COLORS['RESET']}"
        self.log(msg, is_last)

    def dump(self):
        return "\n".join(self.lines)


class Rule:
    _id_counter = 0

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.id = Rule._id_counter
        Rule._id_counter += 1

        self.lhs_vars = re.findall(r'[A-Z]', lhs)
        self.rhs_vars = re.findall(r'[A-Z]', rhs)

    def __repr__(self):
        return f"R{self.id}: {self.lhs} => {self.rhs}"

class ExpertSystem:
    def __init__(self):
        self.rules = []
        self.facts = set()
        self.queries = []
        self.graph = defaultdict(list)
        self.rules = []

        self.fact_to_rules = defaultdict(list)   # Fact → Rules (incoming)
        self.rule_to_facts = defaultdict(list)   # Rule → Facts (outgoing)
        self.rule_dependencies = defaultdict(list)  # Rule ← Facts (conditions)

    def add_fact(self, fact_str):
        for char in fact_str:
            if char.isupper():
                self.facts.add(char)

    def add_rule(self, rule_str):
        if "<=>" in rule_str:
            lhs, rhs = rule_str.split("<=>")
            lhs, rhs = lhs.strip(), rhs.strip()
            self._add_rule_obj(lhs, rhs)
            self._add_rule_obj(rhs, lhs)

        elif "=>" in rule_str:
            lhs, rhs = rule_str.split("=>")
            self._add_rule_obj(lhs.strip(), rhs.strip())


    def _add_rule_obj(self, lhs, rhs):
        rule = Rule(lhs, rhs)
        self.rules.append(rule)

        # Rule → Facts (conclusion edges)
        for var in rule.rhs_vars:
            self.rule_to_facts[rule].append(var)
            self.fact_to_rules[var].append(rule)

        # Facts → Rule (condition edges)
        for var in rule.lhs_vars:
            self.rule_dependencies[rule].append(var)

    def delete_rule(self, lhs, rhs):
        to_remove = [r for r in self.rules if r.lhs == lhs and r.rhs == rhs]

        for rule in to_remove:
            self.rules.remove(rule)

            # Remove Rule → Fact
            for var in rule.rhs_vars:
                if rule in self.fact_to_rules[var]:
                    self.fact_to_rules[var].remove(rule)

            # Remove Fact → Rule
            if rule in self.rule_dependencies:
                del self.rule_dependencies[rule]

            if rule in self.rule_to_facts:
                del self.rule_to_facts[rule]

    def rebuild_graph(self):
        self.graph = defaultdict(list)
        for lhs, rhs in self.rules:
            vars_in_rhs = re.findall(r'[A-Z]', rhs)
            for var in vars_in_rhs:
                self.graph[var].append((lhs, rhs))

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
            self.add_fact(fact)
            return True

    def prove(self, target, visited, depth=0, logger=None):
        if logger:
            logger.prove(target)
            logger.push()

        if target in self.facts:
            if logger:
                logger.log(f"✔ {target} is True (fact)")
                logger.pop()
            return "T"

        if target in visited:
            if logger:
                logger.error(f"⚠ Loop on {target} → Unknown")
                logger.pop()
            return "N"

        visited.add(target)

        results = set()

        # ==================================================
        #  Try rules that conclude TARGET
        # ==================================================
        rules = self.fact_to_rules.get(target, [])
        for rule in rules:
            condition = rule.lhs
            conclusion = rule.rhs
            if target not in re.findall(r'[A-Z]', conclusion):
                continue

            if logger:
                logger.rule(condition, conclusion)
                logger.push()

            cond_val = self.eval_condition(condition, visited.copy(), depth + 1, logger, target)

            if cond_val != "T":
                if logger:
                    logger.error( f"✘ Condition is not True ({cond_val})")
                    logger.pop()
                continue

            val = self.resolve_conclusion(conclusion, target, visited.copy(), depth + 2, logger)

            if val in ("T", "CF"):
                results.add(val)
            elif val == "N" and logger:
                results.add("N")

        if len(results) == 0:
            if logger:
                if not rules:
                    logger.log(f"✘ {target} = F (no rule)")
                    logger.result("F", target)
                    logger.pop()
                    return "F"
                else:
                    logger.log(f"✘ {target} = F (no valid rule)")
                    logger.result("N", target)
                    logger.pop()
                    return "N"
            return "F"

        if len(results) == 1:
            val = next(iter(results))
            if logger:
                if val == "T":
                    logger.result("T", target)
                    logger.pop()
                elif val == "CF":

                    logger.result("F", target)
                    logger.pop()
                else:
                    logger.log(f"⚠ {target} is Unknown")
                    logger.pop()
            return val

        if logger:
            logger.log(f"⚠ {target} is Undetermined (conflict: {results})")
            logger.pop()

        return "N"

    def eval_condition(self, expr, visited, depth=0, logger=None, tatget=None):
        rpn = to_rpn(expr)

        if logger:
            # logger.log(f"Eval condition: {expr}")
            logger.condition(expr)
            logger.push()

        def resolver(t):
            return self.prove(t, visited.copy(), depth + 1, logger)

        result = evaluate_rpn(rpn, resolver)

        if logger:
            logger.result(result, tatget)
            logger.pop()

        return result

    def solve(self, target):
        logger = ReasonerLogger()

        # logger.log(f"Query {target}")
        logger.query(target)
        logger.push()

        result = self.prove(target, set(), 1, logger)
        logger.log(f"Result: {target} = {result}")
        logger.pop()

        print(logger.dump())
        return result

    def resolve_conclusion(self, conclusion, target, visited, depth=0, logger=None):
        vars_in_conc = list(set(re.findall(r'[A-Z]', conclusion)))
        rpn = to_rpn(conclusion)

        if logger:
            # logger.log(f"Resolving: {conclusion}")
            logger.pop()
            logger.resolve(conclusion)

        valid = set()
        known_vals = {}
        for combo in itertools.product(["T", "CF"], repeat=len(vars_in_conc)):
            state = dict(zip(vars_in_conc, combo))

            conflict = False

            for v in vars_in_conc:
                if v == target:
                    continue
                if v not in known_vals:
                    known_vals[v] = self.prove(v, visited.copy(), depth + 1, None)

                val = known_vals[v]
                if val == "T" and state[v] != "T":
                    conflict = True
                    break
                if val == "CF" and state[v] != "CF":
                    conflict = True
                    break

            if conflict:
                continue

            def resolver(x):
                if state[x] == "T":
                    return "T"
                else:
                    return "CF"

            result = evaluate_rpn(rpn, resolver)

            if result == "T":
                valid.add(state[target])

        if logger:
            # logger.log(f"Possible {target}: {valid}")
            logger.possible(target, valid)

        if len(valid) == 1:
            return "T" if "T" in valid else "CF"

        if len(valid) > 1:
            if logger:
                logger.log(f"⚠ {target} is Undetermined")
            return "N"

        return None
