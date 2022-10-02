# EvilTree
A python3 remake of the classic "tree" command with the additional feature of searching for keywords or regex patterns in files, highlighting those that contain matches, created for two main reasons:
 - When searcing for secrets in files of unknown systems / directory structures, it's important usefull to know not only which files contain certain keywords (e.g., password) but also where those files are located in a hierarchy of files and folders. That way, it's easy to distinguish files that are juicy from files that contain hot keywords (like password) in comments or out of context references.
 - "tree" is an amazing tool for analyzing directory structures, not pre-installed in every linux distro and kind of limited in Windows (compared to the UNIX version). It's really handy to have a standalone alternative of the command for post-exploitation enumeration or analysing directory structures and quickly finding relationships between files.

## Installation & Usage Examples
The script has no dependencies. Just `chmod +x` and run.  
Here's an example of running a regex that would essentially match strings similar to `password = something`:

![image](https://user-images.githubusercontent.com/75489922/193478410-f69879a5-7c5c-4cd3-80f0-ece8f514e100.png)
  
    
An example of using comma separated keywords instead of regex:
![image](https://user-images.githubusercontent.com/75489922/193478656-a184ab55-0b3b-4f54-ada4-e658406503c1.png)
