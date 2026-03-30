import os
from ExpertSystem import ExpertSystem
from parser import parse_file


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

def main():
    tests = [
        test_and,
        test_or,
        test_xor,
        test_same,
        test_neg,
        test_mix,
        test_nrf,
        test_blyat,
        test_imply_and,
        test_complex_paren
    ]

    passed = 0

    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    main()
