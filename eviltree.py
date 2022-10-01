#!/bin/python3
# -*- coding: utf-8 -*-
# Written by Panagiotis Chartas (t3l3machus)

import os, re, argparse
from stat import S_ISCHR, ST_MODE, S_ISBLK


''' Colors '''
LINK = '\033[1;38;5;37m'
BROKEN = '\033[48;5;234m\033[1;31m'
CHARSPEC = '\033[0;38;5;228m'
#CHARSPEC = '\033[48;5;234m\033[1;33m'
DENIED = '\033[38;5;222m'
DEBUG = '\033[0;38;5;214m'
GREEN = '\033[38;5;47m'
DIR = '\033[1;38;5;12m'
MATCH = '\033[1;38;5;201m' #220
RED = '\033[1;31m'
END = '\033[0m'
BOLD = '\033[1m'

# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser()

parser.add_argument("-r", "--root-path", action="store", help = "The root path to walk.", required = True)
parser.add_argument("-o", "--only-interesting", action="store_true", help = "List only those files that their content includes interesting keywords.")
parser.add_argument("-k", "--keywords", action="store", help = "Comma separated keywords to search for in files.")
parser.add_argument("-a", "--match-all", action="store_true", help = "By default, files are marked when at least one keyword is matched. Use this option to mark only files that match all given keywords.")
parser.add_argument("-L", "--level", action="store", help = "Descend only level directories deep.", type = int)
parser.add_argument("-i", "--ignore-case", action="store_true", help = "Enables case insensitive keyword search ** for non-binary files only **.")
parser.add_argument("-b", "--binary", action="store_true", help = "Search for keywords in binary files too. Regex is compiled, only case sensitive search is supported.")
parser.add_argument("-v", "--verbose", action="store_true", help = "Print information about which keyword(s) matched.")
parser.add_argument("-f", "--full-pathnames", action="store_true", help = "Print absolute file and directory paths.")
parser.add_argument("-n", "--non-ascii", action="store_true", help = "Draw the directories tree using common utf-8 characters (in case of \"UnicodeEncodeError: 'ascii' codec...\" along with -q).")
parser.add_argument("-d", "--directories-only", action="store_true", help = "List directories only.")
parser.add_argument("-l", "--follow-links", action="store_true", help = "Follows symbolic links if they point to directories, as if they were directories. Symbolic links that will result in recursion are avoided when detected.")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()


def exit_with_msg(msg):
	print(f'[{DEBUG}Debugger{END}] {msg}')
	exit(1)
	

# Init keywords list
default_keywords = ['passw', 'admin', 'token', 'user', 'secret', 'login']
keywords = []

if not args.keywords:
	keywords = default_keywords

elif args.keywords:
	for word in args.keywords.split(","):
		if len(word.strip()) > 0:
			keywords.append(word.strip()) 
			
	if not len(keywords):
		keywords = default_keywords

total_keywords = len(keywords)


# Define depth level
if isinstance(args.level, int):
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-L) must be greater than 0.') 

else:
	depth_level = 4096


# -------------- Functions -------------- #

def print_banner():
	
	print('\r')
	padding = '  '

	E = [[' ', '┌', '─', '┐'], [' ', '├┤',' '], [' ', '└','─','┘']]
	V = [[' ', '┬', ' ', ' ', '┬'], [' ', '└','┐','┌', '┘'], [' ', ' ','└','┘', ' ']]
	I =	[[' ', '┬'], [' ', '│',], [' ', '┴']]
	L = [[' ', '┬',' ',' '], [' ', '│',' ', ' '], [' ', '┴','─','┘']]
	T = [[' ', '┌','┬','┐'], [' ', ' ','│',' '], [' ', ' ','┴',' ']]
	R = [[' ', '┬','─','┐'], [' ', '├','┬','┘'], [' ', '┴','└','─']]

	banner = [E,V,I,L,T,R,E,E]
	final = []
	init_color = 43
	txt_color = init_color
	cl = 0

	for charset in range(0, 3):
		for pos in range(0, len(banner)):
			for i in range(0, len(banner[pos][charset])):
				clr = f'\033[38;5;{txt_color}m'
				char = f'{clr}{banner[pos][charset][i]}'
				final.append(char)
				cl += 1
				txt_color = txt_color + 36 if cl <= 3 else txt_color

			cl = 0

			txt_color = init_color
		init_color += 31

		if charset < 2: final.append('\n   ')

	print(f"   {''.join(final)}")
	print(f'{END}{padding}                   by t3l3machus\n')



def chill():
	pass


# regex = '[\s\S]{0,3}' + r + '[\s\S]{0,3}'		
# re.search(regex, open('/opt/testlink.txt').read(), re.I)
	
	
def file_inspector(file_path, mode = 0):
	try:
		# Regular mode, search binary and non-binary, case insensitive for non-binary files
		if mode == 0:	
					
			try:
				_file = open(file_path, 'r')
				content = _file.read()
				binary = False
			
			except UnicodeDecodeError:
				_file = open(file_path, 'rb')
				content = _file.read()		
				binary = True
			
			except PermissionError:
				return 1
				
			except:
				#print(f'{GREEN}failed to read{file_path}{END}')
				return RED
				
			matched = []
				
			for w in keywords:
				w = re.escape(w)
				#w = '[\s\S]{0,3}' + w + '[\s\S]{0,3}'
				regex = re.compile(bytes(w.encode('utf-8'))) if binary else w
				
				if binary and args.binary:
					found = re.search(regex, content)
				elif not binary:
					found = re.search(regex, content, re.I) if args.ignore_case else re.search(regex, content)
				else:
					found = False
				

				if found:
					matched.append(w)
					
					if not args.match_all and not args.verbose:
						return MATCH

			if not args.match_all and len(matched):
				return [MATCH, f" {GREEN}[{', '.join(matched)}]{END}"]
			
			if args.match_all and len(matched) == total_keywords:
				return MATCH if not args.verbose else [MATCH, f" {GREEN}[{', '.join(keywords)}]{END}"]
				
			return ''
		
	except UnicodeDecodeError:
		return RED	



def fake2realpath(root_dir, target):
	
	back_count = target.count(".." + os.sep)
	
	if (re.search("\.\." + os.sep, target)) and (back_count <= (root_dir.count(os.sep) - 1)):
		dirlist = [d for d in root_dir.split(os.sep) if d.strip()]
		dirlist.insert(0, os.sep)

		try:
			realpath = ''

			for i in range(0, len(dirlist) - back_count ):
				realpath = realpath + (dirlist[i] + os.sep) if dirlist[i] != "/" else dirlist[i]

			realpath += target.split(".." + os.sep)[-1]
			return realpath
			
		except:
			return None
	
	elif not re.search(os.sep, target): # there is a case missing here --> testdir/
		return root_dir + target


	elif re.search("\." + os.sep, target) and not re.search("\.\." + os.sep, target):
		return root_dir + (target.replace("." + os.sep, ""))
	
	else:
		return target



def adjustUnicodeError():
	exit_with_msg('The system seems to have an uncommon default encoding. Restart eviltree with options -q and -n to bypass this issue.')


# ~ child = '├── ' if not args.non_ascii else '|-- '
# ~ child_last = '└── ' if not args.non_ascii else '|-- '
# ~ parent = '│   ' if not args.non_ascii else '|   '
child = (chr(9500) + (chr(9472) * 2) + ' ') if not args.non_ascii else '|-- '
child_last = (chr(9492) + (chr(9472) * 2) + ' ') if not args.non_ascii else '|-- '
parent = (chr(9474) + '   ') if not args.non_ascii else '|   '
total_dirs_processed = 0
total_files_processed = 0


def eviltree(root_dir, intent = 0, depth = '', depth_level = depth_level):

	try:
		global total_dirs_processed, total_files_processed		
		root_dirs = next(os.walk(root_dir))[1]
		root_files = next(os.walk(root_dir))[2]
		total_dirs = len(root_dirs)
		total_files = len(root_files)
		symlinks = []
		recursive = []
		print(f'\r{DIR}{root_dir}{END}') if not intent else chill()


		''' Handle symlinks '''
		for d in root_dirs:
			if os.path.islink(f'{root_dir}{d}'):
				symlinks.append(d)
		
		
		''' Process files '''
		root_files.sort()
		
		if not args.directories_only:
			
			for i in range(0, total_files):
				total_files_processed += 1
				file_path = f'{root_dir}{root_files[i]}'
				is_link = True if os.path.islink(file_path) else False
				
				try:
					is_char_special = True if S_ISCHR((os.lstat(file_path)[ST_MODE])) else False
				except:
					is_char_special = False
				# ~ print(f'cs {is_char_special} {file_path}')
				try:
					is_block_special = True if S_ISBLK(os.stat(file_path)[ST_MODE]) else False
				except:
					is_block_special = False
				# ~ print(f'bs {is_block_special} {file_path}')
				''' Verify target path if file is a symlink '''		
				if is_link:
					symlink_target = target = os.readlink(file_path) if is_link else None
					#target = (root_dir[0:-1] + target) if (re.search("\.\." + os.sep, target)) and (target.count(".." + os.sep) == (root_dir.count(os.sep) - 1)) else target # for symlink targets that include ../ in their path
					target = fake2realpath(root_dir, target) #if (re.search("\.\." + os.sep, target)) else target # for symlink targets that include ../ in their path
					is_dir = True if os.path.isdir(str(target)) else False
					is_broken = True if (not os.path.exists(str(target)) or is_dir) else False
					
					try:
						target_is_char_special = True if S_ISCHR((os.lstat(target)[ST_MODE])) else False
					except:
						target_is_char_special = False
						
					try:
						target_is_block_special = True if S_ISBLK(os.stat(file_path).st_mode) else False
					except:
						target_is_block_special = False
					
				else:
					is_broken = None

				''' Submit file for content inspection if it's not a broken symlink / character special / block special '''
				if (not is_link and not is_char_special and not is_block_special) or (is_link and not is_broken and not target_is_char_special and not target_is_block_special):
					details = file_inspector(file_path) if not is_link else file_inspector(target)
					
					if isinstance(details, list):
						color, verbose, errormsg = details[0], details[1], ''
					
					elif details == 1:
						color, verbose, errormsg = details, '', f' {DENIED}[permission denied]{END}'
						
					else:
						color, verbose, errormsg = details, '', ''
				
				else:
					color, verbose, errormsg = '', '', ''
					
				
				''' Color mark file accordingly in relation to its type and content inspection results '''
				if is_link:				
					linkcolor = BROKEN if is_broken else LINK
					color = CHARSPEC if target_is_block_special or target_is_char_special else color
					filename = f'{linkcolor}{root_files[i]}{END} -> {color}{symlink_target}{errormsg}' if not args.full_pathnames else f'{linkcolor}{root_dir}{root_files[i]}{END} -> {color}{symlink_target}{errormsg}'
				
				elif is_char_special or is_block_special:
					filename = f'{CHARSPEC}{root_files[i]}' if not args.full_pathnames else f'{CHARSPEC}{root_dir}{root_files[i]}'
					
				else:
					filename = f'{color}{root_files[i]}' if not args.full_pathnames else f'{color}{root_dir}{root_files[i]}'
				
				''' Print file branch '''
				if not args.only_interesting:
					print(f'{depth}{child}{color}{filename}{END}{verbose}{errormsg}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}{child_last}{color}{filename}{END}{verbose}{errormsg}')
					
				elif args.only_interesting and ((color and color == MATCH) and not errormsg):
					print(f'{depth}{child}{color}{filename}{END}{verbose}{errormsg}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}{child_last}{color}{filename}{END}{verbose}{errormsg}')


		''' Process dirs '''
		root_dirs.sort()
		
		for i in range(0, total_dirs):
			
			total_dirs_processed += 1
			joined_path = root_dir + root_dirs[i]
			is_recursive = False
			directory = root_dirs[i] if not args.full_pathnames else (joined_path + os.sep)
			
			''' Access permissions check '''
			try:
				sub_dirs = len(next(os.walk(joined_path))[1])
				sub_files = len(next(os.walk(joined_path))[2])
				errormsg = ''
			
			except StopIteration:
				sub_dirs, sub_files = 0, 0
				errormsg = f' [error accessing dir]'
						
				# ~ print(f'[error accessing dir]')
			
			''' Check if symlink and if target leads to recursion '''
			if root_dirs[i] in symlinks:
				symlink_target = target = os.readlink(joined_path)
				#target = (root_dir + target) if (re.search("\.\." + os.sep, target)) and (target.count(".." + os.sep) == (root_dir.count(os.sep) - 1)) else target # for symlink targets that include ../ in their path
				target = fake2realpath(root_dir, target) #if (re.search("\.\." + os.sep, target)) else target # for symlink targets that include ../ in their path			
				is_recursive = ' [recursive, not followed]' if target == root_dir[0:-1] else ''
				
				if len(is_recursive):
					recursive.append(joined_path)
					
				print(f'{depth}{child}{LINK}{directory}{END} -> {DIR}{symlink_target}{END}{is_recursive}{errormsg}') if i < total_dirs - 1 else print(f'{depth}{child_last}{LINK}{directory}{END} -> {DIR}{symlink_target}{END}{is_recursive}{errormsg}')
				
			else:
				print(f'{depth}{child}{DIR}{directory}{END}{errormsg}') if i < total_dirs - 1 else print(f'{depth}{child_last}{DIR}{directory}{END}{errormsg}')
			gfdgfd

			
			if (not args.follow_links and root_dirs[i] not in symlinks) or (args.follow_links and not is_recursive):
				if (sub_dirs or sub_files) and (intent + 1) < depth_level:
					tmp = depth
					depth = depth + parent if i < (total_dirs - 1) else depth + '    '
					eviltree(joined_path + os.sep, intent + 1, depth)
					depth = tmp
			

	except StopIteration:
		print(f'\r{DIR}{root_dir}{END} [error accessing dir]')
		
	except UnicodeEncodeError:
		adjustUnicodeError()
		
	except Exception as e:
		exit_with_msg(f'Something went wrong. Consider creating an issue about this in the original repo (https://github.com/t3l3machus/eviltree)\n{BOLD}Error Details{END}: {e}')



def main():
	
	try:
		print_banner() if not args.quiet else chill()
		
	except UnicodeEncodeError:
		adjustUnicodeError()
	
	root_dir = args.root_path if args.root_path[-1] == os.sep else args.root_path + os.sep	
	
	if os.path.exists(root_dir):
		eviltree(root_dir)
		print(f'\n{total_dirs_processed} directories, {total_files_processed} files')
		
	else:
		exit_with_msg('Directory does not exist.')
			


if __name__ == '__main__':
	main()
