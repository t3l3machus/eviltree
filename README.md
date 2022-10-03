# EvilTree
A python3 remake of the classic "tree" command with the additional feature of searching for user provided keywords/regex in files, highlighting those that contain matches. Created for two main reasons:
 - When searcing for secrets in files of unknown systems / directory structures, being able to visualize which files contain certain keywords/patterns (e.g., password) but also where those files are located in a hierarchy of files and folders, provides a significant advantage. That way, it's easy to distinguish files that are juicy from files that contain hot keywords (like password) in comments or out of context references.
 - "tree" is an amazing tool for analyzing directory structures, not pre-installed in every linux distro and kind of limited in Windows (compared to the UNIX version). It's really handy to have a standalone alternative of the command for post-exploitation enumeration or analysing directory structures and quickly finding relationships between files.

## Installation & Usage Examples
The script has no dependencies. Just `chmod +x` and run.  
**Example #1**: Here's an example of running a regex that would essentially match strings similar to:  
`password = something`

![image](https://user-images.githubusercontent.com/75489922/193536337-188b1f0d-46ad-4680-b068-a4f1772734da.png)
   
    
**Example #2**: Using comma separated keywords instead of regex:

![image](https://user-images.githubusercontent.com/75489922/193478656-a184ab55-0b3b-4f54-ada4-e658406503c1.png)  
**Disclaimer**: Only tested on Windows 10 Pro.

## Further Options & Usage Tips
Notable features:
- Regex `-x` search actually returns all matched patterns in a file. Be careful when combining it with `-v` (--verbose), if you don't limit the length of chars to match correctly, you'll be flooded with matched ouput.
 - You can search keywords/regex in binary files as well by providing option `-b`.
 - You can use this tool as the classic "tree" command if you do not provide keywords `-k` and regex `-x` values. This is useful in case you have gained a limited shell on a machine and want to have "tree" with colored output to look around.
 - There's a list variable `filetype_blacklist` in `eviltree.py` which can be used to exclude certain file extensions from content search. By default, it excludes the following: `gz, zip, tar, rar, 7z, bz2, xz, deb, img, iso, vmdk, dll, ovf, ova`.
 - A quite useful feature is the `-i` (--interesting-only) option. It instructs eviltree to list only files with matching keywords/regex content, significantly reducing the output length:  
 ![image](https://user-images.githubusercontent.com/75489922/193540467-7fa13d73-0893-491f-9b1b-89b34cae8ad7.png)

## Useful keywords/regex patterns
 - Regex to look for passwords: `-x ".{0,3}passw.{0,3}[=]{1}.{0,18}"`
 - Keywords to look for sensitive info: `-k passw,db_,admin,account,user,token`
