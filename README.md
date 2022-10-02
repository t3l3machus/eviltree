# EvilTree
A python3 remake of the classic "tree" command with the additional feature of searching for keywords or regex in files and highlighting those that match, created for two main reasons:
 - tree is an amazing tool for analyzing directory structures, not pre-installed in every linux distro.
 - When searcing for secrets in files of unknown systems / directory structures, it's insanely usefull to know not only which files contain certain keywords (e.g., password) but also where those files are located in a hierarchy of files and folders. That way, it's very easy to distinguish files that are juicy from e.g., common OS files that contain hot keywords (like password) in comments or out o context references.
