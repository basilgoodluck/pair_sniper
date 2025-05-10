import os
import shutil

def delete_pycache(start_dir='.'):
    for root, dirs, files in os.walk(start_dir):
        for d in dirs:
            if d == '__pycache__':
                full_path = os.path.join(root, d)
                print(f"Deleting: {full_path}")
                shutil.rmtree(full_path)

delete_pycache()
