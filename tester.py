import subprocess
import os

TEST_DIR = "test_cases"
MAIN_FILE = "main.py"


def run_test(test_file):
    expected_file = test_file.replace(".txt", ".expected")

    # Run your program
    result = subprocess.run(
        ["python3", MAIN_FILE, test_file],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()

    # Read expected output
    if not os.path.exists(expected_file):
        return ("NO_EXPECTED", test_file, output, "")

    with open(expected_file, "r") as f:
        expected = f.read().strip()

    if output == expected:
        return ("PASS", test_file, output, expected)
    else:
        return ("FAIL", test_file, output, expected)


def main():
    files = sorted(f for f in os.listdir(TEST_DIR) if f.endswith(".txt"))

    total = len(files)
    passed = 0

    for file in files:
        path = os.path.join(TEST_DIR, file)
        status, test_file, output, expected = run_test(path)

        print(f"\n=== {test_file} ===")

        if status == "PASS":
            print("\033[92mPASS\033[0m")
            passed += 1

        elif status == "FAIL":
            print("\033[91mFAIL\033[0m")
            print("Expected:")
            print(expected)
            print("Got:")
            print(output)

        else:
            print("⚠️ No expected file")
            print("Output:")
            print(output)

    print("\n====================")
    print(f"Passed: {passed}/{total}")


if __name__ == "__main__":
    main()
