import sys
from ExpertSystem import ExpertSystem
from parser import parse_file

TRUE = 1
FALSE = 0
UNKNOWN = -1


def format_result(val):
    if val == TRUE:
        return "\033[92mTRUE\033[0m"        # green
    elif val == FALSE:
        return "\033[91mFALSE\033[0m"       # red
    else:
        return "\033[93mUNDETERMINED\033[0m" # yellow


def run_queries(es):
    for query in es.queries:
        try:
            result = es.solve(query)
            print(f"\033[96m{query}\033[0m is {format_result(result)}")
        except Exception as e:
            print(f"{query} caused error: {e}")


def interactive_loop(es):
    print("\n--- Interactive mode ---")
    print("Commands:")
    print("  facts ABC   → reset facts")
    print("  toggle A    → toggle a fact")
    print("  ask C       → query a fact")
    print("  run         → run all queries")
    print("  show        → show facts")
    print("  exit\n")

    while True:
        cmd = input("> ").strip()

        if cmd == "exit":
            break

        elif cmd.startswith("facts"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: facts ABC")
                continue

            es.set_facts(parts[1])
            es.reset_solver()
            print("Facts set to:", "".join(sorted(es.facts)))

        elif cmd.startswith("toggle"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isupper():
                print("Usage: toggle A")
                continue

            fact = parts[1]
            state = es.toggle_fact(fact)
            es.reset_solver()
            print(f"{fact} is now {'TRUE' if state else 'FALSE'}")

        elif cmd.startswith("ask"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isupper():
                print("Usage: ask C")
                continue

            query = parts[1]
            es.reset_solver()
            result = es.solve(query)
            print(f"\033[96m{query}\033[0m is {format_result(result)}")

        elif cmd == "run":
            es.reset_solver()
            run_queries(es)

        elif cmd == "show":
            print("Facts:", "".join(sorted(es.facts)))

        else:
            print("Unknown command")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    es = ExpertSystem()

    try:
        parse_file(filepath, es)
    except Exception as e:
        print(f"Error while parsing file: {e}")
        sys.exit(1)

    # First run (normal behavior)
    run_queries(es)

    # Bonus interactive mode
    interactive_loop(es)

if __name__ == "__main__":
    main()
