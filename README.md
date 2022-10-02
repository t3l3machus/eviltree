# EvilTree
A python3 remake of the classic "tree" command with the additional feature of searching for keywords or regex patterns in files, highlighting those that contain matches, created for two main reasons:
 - When searcing for secrets in files of unknown systems / directory structures, it's insanely usefull to know not only which files contain certain keywords (e.g., password) but also where those files are located in a hierarchy of files and folders. That way, it's easy to distinguish files that are juicy from common OS files that contain hot keywords (like password) in comments or out of context references.
 - "tree" is an amazing tool for analyzing directory structures, not pre-installed in every linux distro and kind of limited in Windows (compared to the UNIX version). It's really handy to have a standalone alternative of the command for post-exploitation enumeration or analysing directory structures and quickly finding relationships between files.

Works on both Linux and Windows.
