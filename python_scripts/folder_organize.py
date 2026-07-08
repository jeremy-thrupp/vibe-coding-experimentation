def show_menu():
    print("Please enter one of the following commands in this order:")
    print("1.) detect-acronymns")
    print("- this will detect acronymns that need to be preserved. Add these to the rename scripts.")
    print("==========")
    print("You then have the option of renaming your current directory, or to traverse through all folders and subfolders.")
    print("2.1) rename-current-folder")
    print("OR")
    print("2.2) rename-folder-traverse <dry-run-false> <hide-folders-from-preview>")
    print("- hide-folders-from-preview hides folder names in the preview")
    print("- dry-run-false enforces the script to rename files and folders. Proceed with caution.")
    print("=========="  )
    print("Run this after cleanup: ")
    print("3.1) remaining-filenames")
    print("==========")
    print("Other utilities: ")
    print("4.1) count-folders")
    print("- counts folders and subfolders in your current directory.")
    print("4.2) recommend-cleanup")
    print("- prints out files that could be considered for deletion.")
    


if __name__ == "__main__":
    show_menu()