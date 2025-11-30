import py_compile
import glob
import sys

def main():
    files = [f for f in glob.glob("**/*.py", recursive=True) if "__pycache__" not in f]
    failed = []
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
        except Exception as e:
            print("ERROR:", f, str(e))
            failed.append((f, str(e)))
    if failed:
        print(f"Syntax check completed: {len(failed)} file(s) failed.")
        sys.exit(1)
    print("Syntax check completed: no errors found.")

if __name__ == '__main__':
    main()
