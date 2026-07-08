These files are best used when accessed via the command line when navigating through folders.

The aim is to bulk rename files and folders to a specific pattern.

### Examples:
* A file with the name 'mockup-Schema.png' would be renamed to 'Mockup-Schema.png'.
* A folder with the name 'new database backup' would be renamed to 'New-Database-Backup'.
* A file with the name '2026-07-03 reports and Summaries' would be renamed to '2026-07-03-Reports-and-Summaries'.

---

> **The Folder-Traversal-Script is a powerful script and should be used with caution.**

There are many instances when the file name shouldn't be changed. 

### Examples of folders/files to avoid:
1. **System folders or OS-managed directories** (e.g. Windows, Program Files, System32, AppData)
2. **Application installation folders** (anything under Program Files or managed by installers)
3. **Hidden or dot folders used by tools** (e.g. .git, .vscode, .idea, .docker)
4. **Configuration directories and files used by software** (.config files, env files, settings folders)
5. **Database files and folders** (especially live DB data directories)
6. **Version control repositories** (entire git repos should not be bulk-renamed)
7. **Build and dependency folders** (node_modules, target, bin, obj, dist)
8. **Cloud sync folders with strict naming rules** (OneDrive, Google Drive internal structure folders)
9. **Backup and restore system folders** (Windows Backup, Time Machine backups, restore points)
10. **Encrypted or security-managed folders** (BitLocker, VeraCrypt, password vault storage)
11. **Media library index folders** (Plex, iTunes/Music libraries, photo catalogs)
12. **Log directories actively written by services** (to avoid breaking logging pipelines)