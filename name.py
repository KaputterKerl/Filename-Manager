import os
import sys

SPECIAL_CHAR_REPLACEMENTS = {
    'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
    'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
    'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
    'ç': 'c', 'ñ': 'n'
}

OPERATION_NAMES = {
    '1': 'Add prefix', 
    '2': 'Replace spaces', 
    '3': 'Lowercase', 
    '4': 'Uppercase', 
    '5': 'Special chars'
}

def show_menu():
    print("=" * 60)
    print("           FILE NAME MANAGER")
    print("=" * 60)
    print("1. Add prefix_ to filenames")
    print("2. Replace_spaces_with_underscores")
    print("3. convert to lowercase")
    print("4. CONVERT TO UPPERCASE")
    print("5. Replace special characters")
    print("6. Exit")
    print("=" * 60)
    print("Multiple operations: '1,3' for prefix then lowercase")
    print("All files must be in the 'Files' folder")
    print("=" * 60)

def get_files():
    directory = "./Files"
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        print("Create 'Files' folder in script directory.")
        return None, None
    
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return directory, files

def filter_files(files, extensions_input):
    if not extensions_input:
        return files
    
    extensions = []
    for ext in extensions_input.split(','):
        ext = ext.strip()
        if ext:
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext.lower())
    
    if not extensions:
        return files
    
    filtered = []
    for file in files:
        file_lower = file.lower()
        if any(file_lower.endswith(ext) for ext in extensions):
            filtered.append(file)
    
    return filtered

def show_preview(files, title, process_files=None):
    if process_files is None:
        process_files = files
    
    print(f"\n{title}:")
    print("-" * 50)
    for file in files:
        print(f"  {file}")
    print("-" * 50)
    print(f"Total: {len(files)}")
    if len(process_files) < len(files):
        print(f"To process: {len(process_files)}")

def ask_extensions():
    print("\nLeave empty for all files.")
    print("Multiple: '.txt,.jpg,.png'")
    return input("File endings: ").strip()

def get_files_with_extensions():
    directory, files = get_files()
    if not directory or not files:
        return None, None, None
    
    extensions = ask_extensions()
    if extensions:
        original_count = len(files)
        files = filter_files(files, extensions)
        if not files:
            print("No files with specified endings.")
            return None, None, None
        print(f"Filtered: {len(files)} files (from {original_count})")
    
    return directory, files, extensions

def process_choice(choice):
    # Route to single or multiple operations
    if ',' in choice:
        return process_multiple(choice)
    else:
        return process_single(choice)

def process_single(choice):
    # Process single operation
    result = get_files_with_extensions()
    if result[0] is None:
        input("Press Enter to continue...")
        return False
    
    directory, files, _ = result
    
    operations = {
        "1": add_prefix,
        "2": replace_spaces, 
        "3": to_lowercase,
        "4": to_uppercase,
        "5": replace_special
    }
    
    if choice in operations:
        return operations[choice](directory, files)
    else:
        print("Invalid choice. Enter 1-5 or comma-separated.")
        input("Press Enter to continue...")
        return False

def process_multiple(ops_input):
    # Process multiple operations in optimal order
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "=" * 60)
    print("        MULTIPLE OPERATIONS")
    print("=" * 60)
    
    operations = []
    for op in ops_input.split(','):
        op = op.strip()
        if op in OPERATION_NAMES:
            operations.append(op)
    
    if not operations:
        print("No valid operations.")
        input("Press Enter to continue...")
        return False
    
    operations = sort_ops(operations)
    
    print("Operations (optimal order):")
    for i, op in enumerate(operations, 1):
        print(f"  {i}. {OPERATION_NAMES[op]}")
    
    result = get_files_with_extensions()
    if result[0] is None:
        input("Press Enter to continue...")
        return False
    
    directory, files, _ = result
    
    prefix = ""
    if '1' in operations:
        prefix = input("\nEnter prefix: ").strip()
        if not prefix:
            print("No prefix entered.")
            input("Press Enter to continue...")
            return False
    
    show_preview(files, "Files to process")
    
    # Show preview of changes
    print(f"\nPreview:")
    print("-" * 60)
    for file in files[:5]:
        new_name = apply_ops(file, operations, prefix)
        print(f"'{file}' -> '{new_name}'")
    if len(files) > 5:
        print(f"... and {len(files) - 5} more")
    print("-" * 60)
    
    if not confirm_operation():
        return False
    
    success_count = rename_files(directory, files, 
                                lambda f: apply_ops(f, operations, prefix), 
                                "Multiple operations")
    
    # Show final summary
    show_summary(success_count, len(files), 0, "")
    return True

def sort_ops(operations):
    priority = {'1': 1, '5': 2, '2': 3, '3': 4, '4': 4}
    case_ops = [op for op in operations if op in ['3', '4']]
    other_ops = [op for op in operations if op not in ['3', '4']]
    other_ops.sort(key=lambda x: priority.get(x, 5))
    
    if '4' in case_ops and '3' in case_ops:
        case_ops = ['4']  
    elif case_ops:
        case_ops.sort(reverse=True)
    
    return other_ops + case_ops

def apply_ops(filename, operations, prefix=""):
    result = filename
    
    for op in operations:
        if op == '1':
            result = prefix + result
        elif op == '2':
            result = result.replace(' ', '_')
        elif op == '3':
            result = result.lower()
        elif op == '4':
            result = result.upper()
        elif op == '5':
            for old_char, new_char in SPECIAL_CHAR_REPLACEMENTS.items():
                result = result.replace(old_char, new_char)
    
    return result

def confirm_operation():
    confirm = input("\nProceed? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Cancelled.")
        input("Press Enter to continue...")
        return False
    return True

def process_files_with_condition(directory, files, condition_func, process_func, 
                               operation_name, skipped_reason, show_changes=True):
    to_process = [f for f in files if condition_func(f)]
    skipped = [f for f in files if not condition_func(f)]
    
    if not to_process:
        print(f"All files already {skipped_reason}.")
        input("Press Enter to continue...")
        return False
    
    show_preview(files, "Files", to_process)
    
    if skipped:
        print(f"{len(skipped)} files {skipped_reason} (skipped)")
    
    if show_changes:
        print(f"\n{len(to_process)} files to process:")
        print("-" * 50)
        for file in to_process:
            new_name = process_func(file)
            print(f"'{file}' -> '{new_name}'")
        print("-" * 50)
    
    if not confirm_operation():
        return False
    
    success_count = rename_files(directory, to_process, process_func, operation_name)
    show_summary(success_count, len(to_process), len(skipped), skipped_reason)
    return True

def add_prefix(directory, files):
    print("\n" + "=" * 40)
    print("        ADD PREFIX")
    print("=" * 40)
    
    show_preview(files, "Files")
    
    prefix = input("\nEnter prefix: ").strip()
    if not prefix:
        print("No prefix entered.")
        input("Press Enter to continue...")
        return False
    
    # Case-insensitive prefix check
    prefix_lower = prefix.lower()
    
    return process_files_with_condition(
        directory, files,
        lambda f: not f.lower().startswith(prefix_lower), 
        lambda f: prefix + f,
        "Adding prefix",
        "have prefix"
    )

def replace_spaces(directory, files):
    print("\n" + "=" * 40)
    print("   REPLACE SPACES")
    print("=" * 40)
    
    return process_files_with_condition(
        directory, files,
        lambda f: ' ' in f,
        lambda f: f.replace(' ', '_'),
        "Replacing spaces", 
        "no spaces"
    )

def to_lowercase(directory, files):
    print("\n" + "=" * 40)
    print("        LOWERCASE")
    print("=" * 40)
    
    return process_files_with_condition(
        directory, files,
        lambda f: not f.islower(),
        lambda f: f.lower(),
        "Lowercase",
        "already lowercase"
    )

def to_uppercase(directory, files):
    print("\n" + "=" * 40)
    print("        UPPERCASE")
    print("=" * 40)
    
    return process_files_with_condition(
        directory, files,
        lambda f: not f.isupper(),
        lambda f: f.upper(),
        "Uppercase",
        "already uppercase"
    )

def replace_special(directory, files):
    print("\n" + "=" * 40)
    print("     SPECIAL CHARACTERS")
    print("=" * 40)
    
    def has_special_chars(filename):
        return any(char in SPECIAL_CHAR_REPLACEMENTS for char in filename)
    
    def replace_special_chars(filename):
        result = filename
        for old_char, new_char in SPECIAL_CHAR_REPLACEMENTS.items():
            result = result.replace(old_char, new_char)
        return result
    
    to_process = [f for f in files if has_special_chars(f)]
    no_special = [f for f in files if not has_special_chars(f)]
    
    if not to_process:
        print("No files with special characters.")
        input("Press Enter to continue...")
        return False
    
    show_preview(files, "Files", to_process)
    
    print("\nCharacter replacements:")
    print("-" * 30)
    for old_char, new_char in SPECIAL_CHAR_REPLACEMENTS.items():
        print(f"  '{old_char}' -> '{new_char}'")
    print("-" * 30)
    
    if no_special:
        print(f"{len(no_special)} files have no special chars (skipped)")
    
    print(f"\n{len(to_process)} files to process:")
    print("-" * 60)
    for file in to_process:
        new_name = replace_special_chars(file)
        print(f"'{file}' -> '{new_name}'")
    print("-" * 60)
    
    if not confirm_operation():
        return False
    
    success_count = rename_files(directory, to_process, replace_special_chars, "Special chars")
    show_summary(success_count, len(to_process), len(no_special), "no special chars")
    return True

def rename_files(directory, files, rename_func, operation_name):
    print(f"\n{operation_name}:")
    success_count = 0
    
    for file in files:
        old_path = os.path.join(directory, file)
        new_name = rename_func(file)
        new_path = os.path.join(directory, new_name)
        
        try:
            if old_path != new_path and not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"Renamed: '{file}' -> '{new_name}'")
                success_count += 1
            elif old_path == new_path:
                pass  
            else:
                print(f"Error: '{new_name}' exists. Skipping '{file}'")
        except Exception as e:
            print(f"Error: {e}")
    
    return success_count

def show_summary(success_count, total_processed, skipped_count, skipped_reason):
    # Show operation summary
    print("\n" + "=" * 40)
    print("COMPLETED")
    print("=" * 40)
    print(f"Success: {success_count} files")
    print(f"Errors:  {total_processed - success_count} files")
    if skipped_count > 0:
        print(f"Skipped ({skipped_reason}): {skipped_count} files")
    print(f"Total:   {total_processed} files")
    print("=" * 40)
    input("\nPress Enter to continue...")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_menu()
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "6":
            print("Exiting...")
            break
        else:
            process_choice(choice)

if __name__ == "__main__":
    main()