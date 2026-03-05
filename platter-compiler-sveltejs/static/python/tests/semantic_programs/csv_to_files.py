import csv
import os

# Make sure the directories exist
os.makedirs("expected", exist_ok=True)
os.makedirs("source_code", exist_ok=True)

# Read CSV1 (Invalid)
with open("Platter - Test Scripts - Semantics - Invalid.csv", newline='', encoding="utf-8") as csvfile1:
    reader1 = list(csv.DictReader(csvfile1))  # read all rows into memory

    # Write expected outputs
    for row in reader1:
        test_num = row["x1"].strip()
        code = row["Expected Output"].strip()
        if not test_num or not code:
            continue
        filename = os.path.join("expected", f"ts_invalid{test_num}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Created {filename}")

    # Write invalid source code
    for row in reader1:
        test_num = row["x1"].strip()
        code = row["Test Case/Test Scenario"].strip()
        if not test_num or not code:
            continue
        filename = os.path.join("source_code", f"ts_invalid{test_num}.platter")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Created {filename}")

# Read CSV2 (Valid)
with open("Platter - Test Scripts - Semantics - Valid.csv", newline='', encoding="utf-8") as csvfile2:
    reader2 = csv.DictReader(csvfile2)
    for row in reader2:
        test_num = row["x1"].strip()
        code = row["Test Case/Test Scenario"].strip()
        if not test_num or not code:
            continue
        filename = os.path.join("source_code", f"ts_valid{test_num}.platter")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Created {filename}")
