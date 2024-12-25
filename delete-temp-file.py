import os

db_name = "invoice.db"  # Replace with your database name
temp_files = [f"{db_name}-wal", f"{db_name}-shm", f"{db_name}-journal"]

for temp_file in temp_files:
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Deleted temporary file: {temp_file}")
    else:
        print(f"Temporary file not found: {temp_file}")
