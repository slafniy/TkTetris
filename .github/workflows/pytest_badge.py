"""Script to get pytest output and return % of passed tests"""
import re
import sys

if __name__ == "__main__":
    failed = re.search(r'(\d+) failed', sys.argv[1])
    passed = re.search(r'(\d+) passed', sys.argv[1])

    failed_num = int(failed.group(1)) if failed is not None else 0
    passed_num = int(passed.group(1)) if passed is not None else 0

    print(f'{passed_num / (failed_num + passed_num) * 100:.2f}')
