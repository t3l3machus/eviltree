# EvilTree
[![Python 3.x](https://img.shields.io/badge/python-3.x-yellow.svg)](https://www.python.org/) 
[![License](https://img.shields.io/badge/license-BSD-red.svg)](https://github.com/t3l3machus/eviltree/blob/main/LICENSE)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

A standalone python3 remake of the classic "tree" command with the additional feature of searching for user provided keywords/regex in files, highlighting those that contain matches. Created for two main reasons:
 - While searching for secrets in files of nested directory structures, being able to visualize which files contain user provided keywords/regex patterns and where those files are located in the hierarchy of folders, provides a significant advantage. 
 - "tree" is an amazing tool for analyzing directory structures. It's really handy to have a standalone alternative of the command for post-exploitation enumeration as it is not pre-installed on every linux distro and is kind of limited on Windows (compared to the UNIX version). 

## Usage Examples

**Example #1**: Running a regex that essentially matches strings similar to: `password = something` against `/var/www`

![image](https://user-images.githubusercontent.com/75489922/193536337-188b1f0d-46ad-4680-b068-a4f1772734da.png)
   
    
**Example #2**: Using comma separated keywords instead of regex:

![image](https://user-images.githubusercontent.com/75489922/193478656-a184ab55-0b3b-4f54-ada4-e658406503c1.png)  
**Disclaimer**: Only tested on Windows 10 Pro.

## Further Options & Usage Tips
Notable features:
- Regex `-x` search actually returns a unique list of all matched patterns in a file. Be careful when combining it with `-v` (--verbose), try to be specific and limit the length of chars to match.
 - You can search keywords/regex in binary files as well by providing option `-b`.
 - You can use this tool as the classic "tree" command if you do not provide keywords `-k` and regex `-x` values. This is useful in case you have gained a limited shell on a machine and want to have "tree" with colored output to look around.
 - There's a list variable `filetype_blacklist` in `eviltree.py` which can be used to exclude certain file extensions from content search. By default, it excludes the following: `gz, zip, tar, rar, 7z, bz2, xz, deb, img, iso, vmdk, dll, ovf, ova`.
 - A quite useful feature is the `-i` (--interesting-only) option. It instructs eviltree to list only files with matching keywords/regex content, significantly reducing the output length:  
 ![image](https://user-images.githubusercontent.com/75489922/193540467-7fa13d73-0893-491f-9b1b-89b34cae8ad7.png)

## Useful keywords/regex patterns
 - Regex to look for passwords: `-x ".{0,3}passw.{0,3}[=]{1}.{0,18}"`
 - Keywords to look for sensitive info: `-k passw,db_,admin,account,user,token`
