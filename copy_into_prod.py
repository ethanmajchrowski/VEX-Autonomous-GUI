import re
from pathlib import Path
import shutil

def update_autonomous_routine(filepath, routine_name, new_list_code_str):
    filepath = Path(filepath)

    # Backup the file before editing
    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
    shutil.copy(filepath, backup_path)

    # Read the file
    with filepath.open('r') as f:
        lines = f.readlines()

    # Compile the pattern
    pattern = re.compile(rf'^(\s*){re.escape(routine_name)}\s*=')
    in_class = False
    updated = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("class AutonomousRoutines"):
            in_class = True
            continue
        if in_class:
            if stripped.startswith("class "):  # Exited the class
                break
            match = pattern.match(line)
            if match:
                indent = match.group(1)
                lines[i] = "{}{} = {}\n".format(indent, routine_name, new_list_code_str)
                updated = True
                break

    if not updated:
        print("Could not find routine '{}' inside AutonomousRoutines".format(routine_name))
        return

    # Write back the modified content
    with filepath.open('w') as f:
        f.writelines(lines)
