import os
import subprocess

BAD_FOLDER = "bad_test_case"
OUTPUT_FILE = "failed_cases.txt"


def test_bad_files():
    if not os.path.exists(BAD_FOLDER):
        print(f"Folder '{BAD_FOLDER}' does not exist.")
        return

    files = sorted(os.listdir(BAD_FOLDER))

    if not files:
        print("No files found in bad_test_case folder.")
        return

    print("=== Running Error Tests ===\n")

    failed_files = []

    for filename in files:
        filepath = os.path.join(BAD_FOLDER, filename)

        if not os.path.isfile(filepath):
            continue

        print(f"--- Testing: {filename} ---")

        try:
            result = subprocess.run(
                ["python3", "main.py", filepath],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if output:
                print("STDOUT:")
                print(output)

            if error:
                print("STDERR:")
                print(error)

            # Check if error exists
            if "Error" in output or "Error" in error:
                print("✅ Error detected\n")
            else:
                print("❌ No error detected (unexpected)\n")
                failed_files.append(filename)

        except subprocess.TimeoutExpired:
            print("❌ Timeout (program may be stuck)\n")
            failed_files.append(filename)

        except Exception as e:
            print(f"❌ Failed to run: {e}\n")
            failed_files.append(filename)

    # Write failed files to output file
    with open(OUTPUT_FILE, "w") as f:
        if failed_files:
            f.write("Files that did NOT produce expected errors:\n")
            for file in failed_files:
                f.write(file + "\n")
        else:
            f.write("All files correctly produced errors.\n")

    print(f"\n📄 Results saved to '{OUTPUT_FILE}'")

    if failed_files:
        print("⚠️ Some files failed the test.")
    else:
        print("🎉 All tests passed.")


if __name__ == "__main__":
    test_bad_files()
