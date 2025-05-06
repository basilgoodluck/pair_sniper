import os
from datetime import datetime

FILE_PATH = "test.txt"

def write_to_file():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File created.\n")
    else:
        with open(FILE_PATH, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File updated.\n")

    print(f"wrote to {FILE_PATH}.")

if __name__ == "__main__":
    write_to_file()
