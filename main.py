import sys
from ExpertSystem import ExpertSystem
from parser import parse_file   # the function we just wrote


TRUE = 1
FALSE = 0
UNKNOWN = -1


def format_result(val):
    if val == TRUE:
        return "TRUE"
    elif val == FALSE:
        return "FALSE"
    else:
        return "UNDETERMINED"


def main():
    # 1. Check arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    # 2. Init system
    es = ExpertSystem()

    # 3. Parse input file
    try:
        parse_file(filepath, es)
    except Exception as e:
        print(f"Error while parsing file: {e}")
        sys.exit(1)

    # 4. Debug (optional)
    # print("Rules:", es.rules)
    # print("Facts:", es.facts)
    # print("Queries:", es.queries)

    # 5. Solve queries
    for query in es.queries:
        try:
            result = es.solve(query)
            print(f"{query} is {format_result(result)}")
        except Exception as e:
            print(f"{query} caused error: {e}")


if __name__ == "__main__":
    main()
