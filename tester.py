import pandas as pd
from ExpertSystem import ExpertSystem
from parser import parse_file, parse_strings
import argparse


def run_test(filepath, expected):
    es = ExpertSystem()

    try:
        parse_file(filepath, es)
    except Exception as e:
        print(f"\033[93m[ERROR]\033[0m parsing {filepath}: {e}")
        return False

    success = True

	#debug
    # for rule in es.rules:
    #     print(rule)
    for query, expected_result in expected.items():
        try:
            result = es.solve(query)

            if result != expected_result:
                print(
                    f"\033[91m[FAIL]\033[0m {filepath} | {query}: expected {expected_result}, got {result}"
                )
                success = False
            else:
                print(
                    f"\033[92m[PASS]\033[0m {filepath} | {query}: {result}"
                )

        except Exception as e:
            print(f"\033[93m[ERROR]\033[0m {filepath} | {query}: {e}")
            success = False

    return success

def run_test_string(content, expected):
    es = ExpertSystem()

    try:
        parse_strings(content, es)
    except Exception as e:
        return {"error": str(e)}

    results = []

    for query, expected_result in expected.items():
        try:
            result = es.solve(query)
            if result == "N":
                result = "F"
            results.append({
                "Query": query,
                "Expected": expected_result,
                "Got": result,
                "Pass": result == expected_result
            })
        except Exception as e:
            results.append({
                "Query": query,
                "Expected": expected_result,
                "Got": f"ERROR: {e}",
                "Pass": False
            })

    return pd.DataFrame(results)

def show_test_string(title, content, expected):
    print(f"\n=== {title} ===")

    df = run_test_string(content, expected)

    if isinstance(df, dict):
        print("❌ ERROR:", df["error"])
        return

    display(df)

    score = df["Pass"].sum()
    total = len(df)

    print(f"Result: {score}/{total} passed")

def test_and():
    return run_test(
        "./good_test_case/and.txt",
        {
            "E": "T",
            "F": "N"
        }
    )


def test_or():
    return run_test(
        "./good_test_case/or.txt",
        {
            "A": "T",
        }
    )


def test_xor():
    return run_test(
        "./good_test_case/XOR.txt",
        {
            "A": "N"
        }
    )

def test_same():
    return run_test(
        "./good_test_case/same.txt",
        {
            "A": "T"
        }
    )

def test_neg():
    return run_test(
        "./good_test_case/neg.txt",
        {
            "A": "N"
        }
    )

def test_neg2():
    return run_test(
        "./good_test_case/neg2.txt",
        {
            "E": "N"
        }
    )

def test_mix():
    return run_test(
        "./good_test_case/mix.txt",
        {
            "C": "T"
        }
    )

def test_nrf():
    return run_test(
        "./good_test_case/no_related_fact.txt",
        {
            "A": "F"
        }
    )

def test_blyat():
    return run_test(
        "./good_test_case/blyat.txt",
        {
            "E": "T"
        }
    )

def test_imply_and():
    return run_test(
        "./good_test_case/imply_and.txt",
        {
            "E": "T"
        }
    )

def test_complex_paren():
    return run_test(
        "./good_test_case/complex_parenthesis.txt",
        {
            "G":"T",
            "V":"N",
            "B":"T",
            "X":"T"
        }
    )

def test_long_rule():
    return run_test(
        "./good_test_case/very_long_rule.txt",
        {
            "C":"T"
        }
    )

def test_in_left_side():
    return run_test(
        "./good_test_case/in_leftside_of_rule.txt",
        {
            "A":"F"
        }
    )

def test_bidirectional():
    return run_test(
        "./good_test_case/Bidirectional.txt",
        {
            "D":"T"
        }
    )

def test_slack1():
        return run_test(
        "./good_test_case/slack1.txt",
        {
            "A":"F"
        }
        )

def test_or_conclusion():
        return run_test(
        "./good_test_case/or_conclusion.txt",
        {
            "A":"T",
            "B":"N",
            "C":"N"
        }
        )

def test_or_conclusion2():
        return run_test(
        "./good_test_case/or_conclusion2.txt",
        {
            "B":"N",
            "D":"N",
            "C":"N"
        }
        )
def test_or_conclusion3():
        return run_test(
        "./good_test_case/or_conclusion3.txt",
        {
            "B":"N",
            "C":"N"
        }
        )

def test_xor_conclusion():
        return run_test(
        "./good_test_case/xor_conclusion.txt",
        {
            "B":"N",
            "C":"N",
            "A":"T"
        }
        )
def test_xor_conclusion2():
        return run_test(
        "./good_test_case/xor_conclusion2.txt",
        {
            "B":"N",
            "C":"N",
            "D":"N"
        }
        )
def test_xor_conclusion3():
        return run_test(
        "./good_test_case/xor_conclusion3.txt",
        {
            "B":"N",
            "C":"N",
        }
        )

def test_from_subject():
        return run_test(
        "./good_test_case/from_subject.txt",
        {
            "C":"N",
        }
        )


def main():
    parser = argparse.ArgumentParser(description="Expert System")

    parser.add_argument(
        "-m", "--mandatory",
        action="store_true",
        help="Enable mandatory test"
    )

    parser.add_argument(
        "-b", "--bonus",
        action="store_true",
        help="Enable bonus test"
    )

    parser.add_argument(
        "-a", "--additional",
        action="store_true",
        help="Enable additional test"
    )

    args = parser.parse_args()

    if not (args.mandatory or args.bonus or args.additional):
        print("No test suite selected.")
        parser.print_help()
        return

    tests_mandatory = [
        test_and, #and in condition
        test_or, #or in condition
        test_xor, #xor in condition
        test_neg, #negation
        test_neg2, #negation again
        test_imply_and, #and in conclusion
        test_complex_paren, #parenthesis
    ]
    tests_bonus = [
        test_bidirectional, # <=>
        test_or_conclusion,
        test_or_conclusion2,
        test_or_conclusion3,
        test_xor_conclusion,
        test_xor_conclusion2,
        test_xor_conclusion3,
    ]

    tests_other = [
        test_same,
        test_mix,
        test_nrf,
        test_blyat,
        test_long_rule,
        test_in_left_side,
        test_from_subject
    ]

    if args.mandatory:
        m_passed = 0

        for test in tests_mandatory:
            print(f"\nRunning {test.__name__}...")
            if test():
                m_passed += 1

    if args.bonus:
        b_passed = 0

        for test in tests_bonus:
            print(f"\nRunning {test.__name__}...")
            if test():
                b_passed += 1
    if args.additional:
        o_passed = 0

        for test in tests_other:
            print(f"\nRunning {test.__name__}...")
            if test():
                o_passed += 1
    if args.mandatory:
        print(f"\n mandatory : {m_passed}/{len(tests_mandatory)} tests passed")
    if args.bonus:
        print(f"\n bonus: {b_passed}/{len(tests_bonus)} tests passed")
    if args.additional:
        print(f"\n additional: {o_passed}/{len(tests_other)} tests passed")


if __name__ == "__main__":
    main()
