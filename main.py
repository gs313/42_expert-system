import sys
from ExpertSystem import ExpertSystem
from parser import parse_file
import argparse

TRUE = 1
FALSE = 0
UNKNOWN = -1

from parser import (
    validate_expression,
    validate_expression_syntax,
    validate_rule_syntax,
    normalize
)

def validate_rule_input(rule):
    validate_rule_syntax(rule)

    if "<=>" in rule:
        lhs, rhs = rule.split("<=>")
    elif "=>" in rule:
        lhs, rhs = rule.split("=>")
    else:
        raise ValueError("Rule must contain => or <=>")

    lhs = normalize(lhs.strip())
    rhs = normalize(rhs.strip())

    if not lhs or not rhs:
        raise ValueError("Empty LHS or RHS")

    validate_expression(lhs)
    validate_expression_syntax(lhs)

    validate_expression(rhs)
    validate_expression_syntax(rhs)

    return lhs, rhs

def format_result(val):
    if val == "T":
        return "\033[92mTRUE\033[0m"        # green
    elif val == "F":
        return "\033[91mFALSE\033[0m"       # red
    else:
        return "\033[93mUNDETERMINED\033[0m" # yellow


def run_queries(es, mandatory=False):
    for query in es.queries:
        try:
            result = es.solve(query)
            if mandatory and result=="N":
                result = "F"
            print(f"\033[96m{query}\033[0m is {format_result(result)}")
        except Exception as e:
            print(f"{query} caused error: {e}")

def list_rules(es):
    visited = set()
    indexed = []
    idx = 1

    for lhs, rhs in es.rules:
        if (lhs, rhs) in visited:
            continue

        if (rhs, lhs) in es.rules:
            indexed.append((idx, f"{lhs} <=> {rhs}", [(lhs, rhs), (rhs, lhs)]))
            visited.add((lhs, rhs))
            visited.add((rhs, lhs))
        else:
            indexed.append((idx, f"{lhs} => {rhs}", [(lhs, rhs)]))
            visited.add((lhs, rhs))

        idx += 1

    for i, text, _ in indexed:
        print(f"{i}. {text}")

    return indexed

def interactive_loop(es):
    print("\n--- Interactive mode ---")
    print("Commands:")
    print("  facts ABC   → reset facts")
    print("  toggle A    → toggle a fact")
    print("  ask C       → query a fact")
    print("  run         → run all queries")
    print("  show        → show facts and rules")
    print("  add A+B=>C  → add rule")
    print("  del         → delete rule (choose from list)")
    print("  help        → show commands")
    print("  exit\n")

    while True:
        try:
            cmd = input("> ").strip()
        except EOFError:
            print("\nExiting (Ctrl+D)...")
            break
        except KeyboardInterrupt:
            print("\nInterrupted (Ctrl+C). Type 'exit' to quit.")
            continue

        if cmd == "exit":
            break

        elif cmd.startswith("facts"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: facts ABC")
                continue

            es.set_facts(parts[1])
            print("Facts set to:", "".join(sorted(es.facts)))

        elif cmd.startswith("toggle"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isupper():
                print("Usage: toggle A")
                continue

            fact = parts[1]
            state = es.toggle_fact(fact)
            print(f"{fact} is now {'TRUE' if state else 'FALSE'}")

        elif cmd.startswith("ask"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isupper():
                print("Usage: ask C (capital letter only)")
                continue

            query = parts[1]
            result = es.solve(query)
            print(f"\033[96m{query}\033[0m is {format_result(result)}")

        elif cmd == "run":
            run_queries(es)

        elif cmd.startswith("add"):
            rule = cmd[3:].strip()

            if not rule:
                print("Usage: add A+B=>C or A<=>B")
                continue

            try:
                lhs, rhs = validate_rule_input(rule)

                # Check duplicate
                if (lhs, rhs) in es.rules:
                    print("⚠️ Rule already exists")
                    continue

                # If bidirectional, check both
                if "<=>" in rule and (rhs, lhs) in es.rules:
                    print("⚠️ Rule already exists (bidirectional)")
                    continue

                es.add_rule(rule)

                print(f"✅ Rule is valid and added: {lhs} {'<=>' if '<=>' in rule else '=>'} {rhs}")

            except Exception as e:
                print(f"❌ Invalid rule: {e}")

        elif cmd == "del":
            indexed = list_rules(es)

            if not indexed:
                print("No rules to delete.")
                continue

            try:
                choice = int(input("Select rule number to delete: "))
            except ValueError:
                print("Invalid number.")
                continue

            selected = next((r for r in indexed if r[0] == choice), None)

            if not selected:
                print("Invalid selection.")
                continue

            _, text, rule_pairs = selected

            # remove all associated pairs
            for pair in rule_pairs:
                if pair in es.rules:
                    es.rules.remove(pair)

            print(f"Deleted rule: {text}")

        elif cmd == "show":
            print("Rules:")

            visited = set()

            for lhs, rhs in es.rules:
                if (lhs, rhs) in visited:
                    continue

                # check if reverse exists
                if (rhs, lhs) in es.rules:
                    print(f"{lhs} <=> {rhs}")
                    visited.add((lhs, rhs))
                    visited.add((rhs, lhs))
                else:
                    print(f"{lhs} => {rhs}")
                    visited.add((lhs, rhs))
            print("Facts:", "".join(sorted(es.facts)))

        elif cmd == "help":
            print("Commands:")
            print("  facts ABC   → reset facts")
            print("  toggle A    → toggle a fact")
            print("  ask C       → query a fact")
            print("  run         → run all queries")
            print("  show        → show facts and rules")
            print("  add A+B=>C  → add rule")
            print("  del         → delete rule (choose from list)")
            print("  exit\n")

        else:
            print("Unknown command")

def main():
    parser = argparse.ArgumentParser(description="Expert System")

    parser.add_argument(
        "input_file",
        help="Path to input file"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Enable interactive mode after processing queries"
    )

    parser.add_argument(
        "-m", "--mandatory",
        action="store_true",
        help="Enable mandatory mode for evaluation"
    )

    args = parser.parse_args()

    es = ExpertSystem()

    try:
        parse_file(args.input_file, es)
    except Exception as e:
        print(f"Error while parsing file: {e}")
        sys.exit(1)

    run_queries(es,mandatory=args.mandatory)

    # Optional interactive mode
    if args.interactive:
        interactive_loop(es)


if __name__ == "__main__":
    main()
