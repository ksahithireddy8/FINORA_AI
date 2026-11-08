import shutil
from modules.excel_manager import EXCEL_FILE

backup_file = EXCEL_FILE.with_name(
    "finora_data_backup.xlsx"
)

shutil.copy2(EXCEL_FILE, backup_file)

print("Backup created successfully!")
print("Backup location:", backup_file)