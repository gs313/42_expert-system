import re

def parse_file(filepath, expert_system):
    with open(filepath, "r") as f:
        lines = f.readlines()

    current_lhs = None  # store left side before =>

    for raw_line in lines:
        # 1. Remove comments
        line = raw_line.split("#")[0].strip()

        if not line:
            continue

        # 2. Facts
        if line.startswith("="):
            print(f"fact = {line[1:]}")
            expert_system.add_fact(line[1:])
            continue

        # 3. Queries
        if line.startswith("?"):
            print(f"quries = {[c for c in line[1:] if c.isupper()]}")
            expert_system.queries = [c for c in line[1:] if c.isupper()]
            continue

        # 4. Biconditional
        if line.startswith("<=>"):
            rhs = line[3:].strip()
            if current_lhs:
                print ("================")
                print(current_lhs + "=>" + rhs)
                print(rhs + "=>" + current_lhs)
                expert_system.add_rule(current_lhs + "=>" + rhs)
                expert_system.add_rule(rhs + "=>" + current_lhs)
                current_lhs = None
            continue

        # 5. Implication RHS
        if line.startswith("=>"):
            rhs = line[2:].strip()
            if current_lhs:
                print("==========================")
                print(current_lhs + "=>" + rhs)
                expert_system.add_rule(current_lhs + "=>" + rhs)
                current_lhs = None
            continue

        # 6. Otherwise → LHS
        current_lhs = line
