import re

# ---------------- NORMALIZE ----------------
def normalize(expr):
    return re.sub(r'\s+', '', expr)


# ---------------- CHARACTER VALIDATION ----------------
VALID_EXPR = re.compile(r'^[A-Z\!\+\|\^\(\)\s]+$')


def validate_expression(expr):
    if not VALID_EXPR.match(expr):
        raise ValueError(f"Invalid characters in expression: {expr}")


# ---------------- SYNTAX VALIDATION ----------------
def validate_expression_syntax(expr):
    tokens = re.findall(r'[A-Z]|\!|\+|\^|\||\(|\)', expr)

    if not tokens:
        raise ValueError(f"Empty expression: {expr}")

    prev = None

    for token in tokens:

        if token.isupper():
            if prev and (prev.isupper() or prev == ')'):
                raise ValueError(f"Missing operator in expression: {expr}")

        elif token == '!':
            if prev and (prev.isupper() or prev == ')'):
                raise ValueError(f"Invalid NOT placement: {expr}")

        elif token in ['+', '|', '^']:
            if prev is None or prev in ['+', '|', '^', '!', '(']:
                raise ValueError(f"Invalid operator placement: {expr}")

        elif token == '(':
            if prev and (prev.isupper() or prev == ')'):
                raise ValueError(f"Missing operator before '(': {expr}")

        elif token == ')':
            if prev in ['+', '|', '^', '!', '(']:
                raise ValueError(f"Invalid closing parenthesis: {expr}")

        prev = token

    if tokens[-1] in ['+', '|', '^', '!']:
        raise ValueError(f"Expression cannot end with operator: {expr}")

    # Parentheses balance
    balance = 0
    for t in tokens:
        if t == '(':
            balance += 1
        elif t == ')':
            balance -= 1
        if balance < 0:
            raise ValueError(f"Unbalanced parentheses: {expr}")

    if balance != 0:
        raise ValueError(f"Unbalanced parentheses: {expr}")


# ---------------- RULE VALIDATION ----------------
def validate_rule_syntax(line):
    # count <=> first
    count_bi = line.count("<=>")
    count_imp = line.count("=>") - 2 * count_bi  # remove those inside <=>

    if count_bi > 1:
        raise ValueError(f"Invalid rule (multiple <=>): {line}")

    if count_imp > 1:
        raise ValueError(f"Invalid rule (multiple =>): {line}")

    if count_bi == 1 and count_imp > 0:
        raise ValueError(f"Invalid rule (mixed => and <=>): {line}")

    if re.search(r'(=>\s*=>)|(<=>\s*<=>)', line):
        raise ValueError(f"Invalid rule syntax: {line}")


# ---------------- MAIN PARSER ----------------
def parse_file(filepath, expert_system):
    with open(filepath, "r") as f:
        lines = f.readlines()

    current_lhs = None

    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.split("#")[0].strip()

        if not line:
            continue

        # ---------------- FACTS ----------------
        if line.startswith("="):
            facts = line[1:].strip()
            if not all(c.isupper() for c in facts):
                raise ValueError(f"Invalid facts at line {line_num}: {facts}")
            # print(f"fact = {facts}")
            expert_system.add_fact(facts)
            continue

        # ---------------- QUERIES ----------------
        if line.startswith("?"):
            queries = line[1:].strip()
            if not all(c.isupper() for c in queries):
                raise ValueError(f"Invalid queries at line {line_num}: {queries}")
            # print(f"quries = {queries}")
            expert_system.queries = list(queries)
            continue

        # ---------------- FULL BICONDITIONAL ----------------
        if "<=>" in line:
            validate_rule_syntax(line)

            lhs, rhs = line.split("<=>")
            lhs = normalize(lhs.strip())
            rhs = normalize(rhs.strip())

            if not lhs or not rhs:
                raise ValueError(f"Invalid rule at line {line_num}: {line}")

            validate_expression(lhs)
            validate_expression_syntax(lhs)

            validate_expression(rhs)
            validate_expression_syntax(rhs)

            # print(lhs + "=>" + rhs)
            # print((rhs + "=>" + lhs))
            expert_system.add_rule(lhs + "=>" + rhs)
            expert_system.add_rule(rhs + "=>" + lhs)
            continue

        # ---------------- FULL IMPLICATION ----------------
        if "=>" in line:
            validate_rule_syntax(line)

            lhs, rhs = line.split("=>")
            lhs = normalize(lhs.strip())
            rhs = normalize(rhs.strip())

            if not lhs or not rhs:
                raise ValueError(f"Invalid rule at line {line_num}: {line}")

            validate_expression(lhs)
            validate_expression_syntax(lhs)

            validate_expression(rhs)
            validate_expression_syntax(rhs)

            # print (lhs + "=>" + rhs)
            expert_system.add_rule(lhs + "=>" + rhs)
            continue

        # ---------------- SPLIT BICONDITIONAL ----------------
        if line.startswith("<=>"):
            rhs = normalize(line[3:].strip())

            if current_lhs is None:
                raise ValueError(f"Missing LHS before <=> at line {line_num}")

            lhs = normalize(current_lhs)

            validate_expression(lhs)
            validate_expression_syntax(lhs)

            validate_expression(rhs)
            validate_expression_syntax(rhs)

            # print ((lhs + "=>" + rhs))
            # print (rhs + "=>" + lhs)
            expert_system.add_rule(lhs + "=>" + rhs)
            expert_system.add_rule(rhs + "=>" + lhs)

            current_lhs = None
            continue

        # ---------------- SPLIT IMPLICATION ----------------
        if line.startswith("=>"):
            rhs = normalize(line[2:].strip())

            if current_lhs is None:
                raise ValueError(f"Missing LHS before => at line {line_num}")

            lhs = normalize(current_lhs)

            validate_expression(lhs)
            validate_expression_syntax(lhs)

            validate_expression(rhs)
            validate_expression_syntax(rhs)

            # print(lhs + "=>" + rhs)
            expert_system.add_rule(lhs + "=>" + rhs)

            current_lhs = None
            continue

        # ---------------- LHS ----------------
        validate_expression(line)
        validate_expression_syntax(line)

        current_lhs = normalize(line)
