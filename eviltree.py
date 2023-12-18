#!/usr/bin/python3
#
# Author: Panagiotis Chartas (t3l3machus)
# https://github.com/t3l3machus

import os, re, argparse
from pathlib import Path
from stat import S_ISCHR, ST_MODE, S_ISBLK, S_ISFIFO, S_ISSOCK
from platform import system as get_system_type
from sys import exit as _exit


def move_on():
	pass


# Enable colors if Windows 
WINDOWS = True if get_system_type() == 'Windows' else False
os.system('') if WINDOWS else move_on

''' Colors '''
LINK = '\033[1;38;5;37m'
BROKEN = '\033[48;5;234m\033[1;31m'
CHARSPEC = '\033[0;38;5;228m'
#CHARSPEC = '\033[48;5;234m\033[1;33m'
#PIPE = '\033[38;5;214m'
PIPE = '\033[48;5;234m\033[1;30m'
SOCKET = '\033[1;38;5;98m'
EXECUTABLE = '\033[1;38;5;43m'
DENIED = '\033[38;5;222m'
DEBUG = '\033[0;38;5;214m'
GREEN = '\033[38;5;47m'
DIR = '\033[1;38;5;12m'
MATCH = '\033[1;38;5;201m'
FAILED = '\033[1;31m'
END = '\033[0m'
BOLD = '\033[1m'

# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser(
	formatter_class = argparse.RawTextHelpFormatter,
	epilog = '''
	
Usage tips:

  - Regex -x search actually returns a unique list of all matched patterns in a file. Be careful when combining it with -v (--verbose), try to be specific and limit the length of chars to match.
  - You can use this tool as the classic "tree" command if you do not provide keywords -k and regex -x values. This is useful in case you have gained a limited shell on a machine and want to have "tree" with colored output to look around.

Useful keywords/regex patterns:

    Regex to look for passwords: -x ".{0,3}passw.{0,3}[=]{1}.{0,18}"
    Keywords to look for sensitive info: -k passw,db_,admin,account,user,token
 
'''
)

parser.add_argument("-r", "--root-path", action="store", help = "The root path to walk.", required = True)
parser.add_argument("-k", "--keywords", action="store", help = "Comma separated keywords to search for in files.")
parser.add_argument("-x", "--regex", action="store", help = "Regex pattern to search for in files. In combination with --verbose, this option returns all values that matched the given pattern for each file, you should use it with caution while setting character limits before and after your actual pattern.")
parser.add_argument("-a", "--match-all", action="store_true", help = "By default, files are highlighted when at least one keyword is matched. Use this option to highlight files that match all given keywords only. This option has no effect when used with regex.")
parser.add_argument("-L", "--level", action="store", help = "Descend only level directories deep.", type = int)
parser.add_argument("-c", "--case-sensitive", action="store_true", help = "Enables case sensitive keywords/regex search.")
parser.add_argument("-b", "--binary", action="store_true", help = "Search for keywords/regex in binary files too.")
parser.add_argument("-v", "--verbose", action="store_true", help = "Print information about which keyword(s) matched.")
parser.add_argument("-i", "--interesting-only", action="store_true", help = "List only files with matching keywords/regex content (significantly reduces output length).")
parser.add_argument("-f", "--full-pathnames", action="store_true", help = "Print absolute file and directory paths.")
parser.add_argument("-A", "--ascii", action="store_true", help = "Use ASCII instead of extended characters (use this in case of \"UnicodeEncodeError: 'ascii' codec...\" along with -q).")
parser.add_argument("-d", "--directories-only", action="store_true", help = "List directories only.")
parser.add_argument("-l", "--follow-links", action="store_true", help = "Follows symbolic links if they point to directories, as if they were directories. Symbolic links that will result in recursion are avoided when detected.")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()


def exit_with_msg(msg):
	print('[' + DEBUG + 'Debugger' + END + '] ' + msg)
	_exit(1)


# Init keyword(s)/regex list if any provided
if args.keywords and args.regex:
	exit_with_msg("You can't use keywords (-k) and regex (-x) at the same time.")

keywords = []

if args.keywords:
	for word in args.keywords.split(","):
		if len(word.strip()) > 0:
			keywords.append(word.strip()) 
			
	verify = [k for k in keywords if k.strip() != '']	
	
	if not len(verify):
		exit_with_msg("Illegal keyword(s) value(s).")


elif args.regex:
	keywords = [args.regex]

total_keywords = len(keywords)


# Define depth level
if isinstance(args.level, int):
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-L) must be greater than 0.') 

else:
	depth_level = 4096


process_files = True if (args.keywords or args.regex) else False
print_fnames = True if not args.directories_only else False

# Filetypes to avoid searching for keywords/regex:
filetype_blacklist = ['gz', 'zip', 'tar', 'rar', '7z', 'bz2', 'xz', 'deb', 'img', 'iso', 'vmdk', 'dll', 'ovf', 'ova']

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
				clr = '\033[38;5;' + str(txt_color) + 'm'
				char = clr + banner[pos][charset][i]
				final.append(char)
				cl += 1
				txt_color = txt_color + 36 if cl <= 3 else txt_color

			cl = 0

			txt_color = init_color
		init_color += 31

		if charset < 2: final.append('\n   ')

	print('   ' + ''.join(final))
	print(END + padding +'                   by t3l3machus\n')



def load_file(file_path, mode):
	f = open(file_path, mode)
	content = f.read()
	f.close()
	return content	



def decoder(l):
	
	decoded = []
	
	for item in l:
		if isinstance(item, bytes):
			decoded.append(item.decode('utf-8', 'ignore'))
		else:
			decoded.append(item)
			
	return decoded

	

def file_inspector(file_path, mode = 0):
	
	try:
			
		''' Load file content accordingly '''		
		try:
			content = load_file(file_path, 'r')
			binary = False
		
		except UnicodeDecodeError:
			content = load_file(file_path, 'rb')	
			binary = True
		
		except PermissionError:
			return 1

		except MemoryError:
			return 2

		except KeyboardInterrupt:
			return 999
			#exit_with_msg('Keyboard interrupt.')

		except:
			return FAILED
		
		''' Search content '''
			
		matched = []
			
		for w in keywords:

			''' Set regex '''
			if args.keywords:
				w = re.escape(w)
			
			if binary:
				regex = re.compile(bytes(w.encode('utf-8'))) if args.case_sensitive else re.compile(bytes(w.encode('utf-8')), re.IGNORECASE)
			else:
				regex = w
			
			''' Search file contents '''
			if binary and args.binary:	
				found = re.search(regex, content) if args.keywords else re.findall(regex, content)
				
			elif not binary:
				if args.keywords:
					found = re.search(regex, content) if args.case_sensitive else re.search(regex, content, re.IGNORECASE)
				elif args.regex:
					found = re.findall(regex, content)
				
			else:
				found = False
							
			''' Handle matches '''
			if found:
				if args.keywords:
					matched.append(w)
				elif args.regex:
					for match in found:
						matched.append(match)
				
				if args.keywords and not args.match_all and not args.verbose:
					return MATCH
		
		if args.binary:
			matched = decoder(matched)
				
		if not args.match_all and args.keywords and len(matched):
			return [MATCH, " " + GREEN + "[" + ', '.join(matched) + "]" + END]

		if args.match_all and args.keywords and len(matched) == total_keywords:
			return MATCH if not args.verbose else [MATCH, " " + GREEN + "[" + ', '.join(matched) + "]" + END]

		if args.regex:
			
			if not args.verbose and matched:
				return MATCH
				
			elif args.verbose and matched:
				unique = list(set(matched))
				return [MATCH, " " + GREEN + "[" + ', '.join(unique) + "]" + END]
		
		return ''
		
	except:
		return FAILED		



def fake2realpath(path, target):
	
	sep_count = target.count(".." + os.sep)
	regex_chk_1 = "^" + re.escape(".." + os.sep)
	regex1_chk_2 = "^" + re.escape("." + os.sep)
	regex1_chk_3 = "^" + re.escape(os.sep)
	
	if (re.search(regex_chk_1, target)) and (sep_count <= (path.count(os.sep) - 1)):
		dirlist = [d for d in path.split(os.sep) if d.strip()]
		dirlist.insert(0, os.sep)

		try:
			realpath = ''

			for i in range(0, len(dirlist) - sep_count ):
				realpath = realpath + (dirlist[i] + os.sep) if dirlist[i] != "/" else dirlist[i]

			realpath += target.split(".." + os.sep)[-1]
			return str(Path(realpath).resolve())
			
		except:
			return None

	elif re.search(regex1_chk_2, target):
		return str(Path((path + (target.replace("." + os.sep, "")))).resolve())
	
	elif not re.search(regex1_chk_3, target):
		return str(Path(path + target).resolve())
	
	else:
		return str(Path(target).resolve())



def adjustUnicodeError():
	exit_with_msg('The system seems to have an uncommon default encoding. Restart eviltree with options -q and -A to resolve this issue.')


# ~ child = '├── ' if not args.ascii else '|-- '
# ~ child_last = '└── ' if not args.ascii else '|-- '
# ~ parent = '│   ' if not args.ascii else '|   '
child = (chr(9500) + (chr(9472) * 2) + ' ') if not args.ascii else '|-- '
child_last = (chr(9492) + (chr(9472) * 2) + ' ') if not args.ascii else '\-- '
parent = (chr(9474) + '   ') if not args.ascii else '|   '
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
		print('\r' + DIR + root_dir + END) if not intent else move_on()


		''' Handle symlinks '''
		for d in root_dirs:
			if os.path.islink(root_dir + d):
				symlinks.append(d)
		
		
		''' Process files '''
		root_files.sort()
		
		for i in range(0, total_files):
			
			total_files_processed += 1
			file_path = root_dir + root_files[i]
			is_link = True if os.path.islink(file_path) else False
					
			if not WINDOWS:
				
				try:
					is_char_special = True if S_ISCHR((os.lstat(file_path)[ST_MODE])) else False
				except:
					is_char_special = False
				
				try:
					is_block_special = True if S_ISBLK(os.stat(file_path)[ST_MODE]) else False
				except:
					is_block_special = False

				try:
					is_pipe = True if S_ISFIFO(os.stat(file_path).st_mode) else False
				except:
					is_pipe = False

				try:
					is_socket = True if S_ISSOCK(os.stat(file_path).st_mode) else False
				except:
					is_socket = False

				try:
					is_executable = True if (os.access(file_path, os.X_OK) and not is_char_special and not is_block_special and not is_pipe and not is_socket) else False
				except:
					is_executable = False
					
			else:
				is_executable, is_socket, is_pipe, is_block_special, is_char_special = False, False, False, False, False

			
			''' Verify target path if file is a symlink '''		
			if is_link:
									
				symlink_target = target = os.readlink(file_path) if is_link else None
				target = fake2realpath(root_dir, target)
				is_dir = True if os.path.isdir(str(target)) else False
				is_broken = True if (not os.path.exists(str(target)) or is_dir) else False
				
				if not WINDOWS:
					
					try:
						target_is_char_special = True if S_ISCHR((os.lstat(target)[ST_MODE])) else False
					except:
						target_is_char_special = False
						
					try:
						target_is_block_special = True if S_ISBLK(os.stat(target).st_mode) else False
					except:
						target_is_block_special = False

					try:
						target_is_pipe = True if S_ISFIFO(os.stat(target).st_mode) else False
					except:
						target_is_pipe = False

					try:
						target_is_socket = True if S_ISSOCK(os.stat(target).st_mode) else False
					except:
						target_is_socket = False

					try:
						target_is_executable = True if (os.access(target, os.X_OK) and not target_is_char_special and not target_is_block_special and not target_is_pipe and not target_is_socket) else False
					except:
						target_is_executable = False
				
				else:
					target_is_executable, target_is_socket, target_is_pipe, target_is_block_special, target_is_char_special = False, False, False, False, False
				
			else:
				is_broken = None

			''' Submit file for content inspection if it's not a broken symlink / character special / block special / pipe / socket'''
			if process_files:
				
				# Check if file extension in blacklist
				fname = root_files[i] if not is_link else target
				file_ext = fname.rsplit(".", 1)[-1].lower()
				blacklisted = True if file_ext in filetype_blacklist else False  
				
				if (not is_link and not is_char_special and not is_block_special and not is_pipe and not is_socket and not blacklisted) or (is_link and not is_broken and not target_is_char_special and not target_is_block_special and not target_is_pipe and not target_is_socket and not blacklisted):
					details = file_inspector(file_path) if not is_link else file_inspector(target)
					
					if isinstance(details, list):
						color, verbose, errormsg = details[0], details[1], ''
					
					elif details == 1:
						color, verbose, errormsg = details, '', ' ' + DENIED + '[permission denied]' + END

					elif details == 2:
						color, verbose, errormsg = details, '', ' ' + DENIED + '[memory error]' + END
					
					elif details == 999:
						exit_with_msg('Keyboard interrupt.')
						
					else:
						color, verbose, errormsg = details, '', ''
				
				else:
					color, verbose, errormsg = '', '', ''
				
			else:
				color, verbose, errormsg = '', '', ''	
				
							
			''' Color mark and print file accordingly in relation to its type and content inspection results '''
			if print_fnames:

				color = str(color)
				
				if is_link:				
					linkcolor = BROKEN if is_broken else LINK
					color = CHARSPEC if target_is_block_special or target_is_char_special else color
					color = PIPE if target_is_pipe else color
					color = SOCKET if target_is_socket else color
					color = EXECUTABLE if (target_is_executable and color not in [MATCH, FAILED]) else color
					filename = (linkcolor + root_files[i] + END + ' -> ' + color + symlink_target + errormsg) if not args.full_pathnames else (linkcolor + root_dir + root_files[i] + END + ' -> ' + color + symlink_target + errormsg)
				
				elif is_char_special or is_block_special:
					filename = (CHARSPEC + root_files[i]) if not args.full_pathnames else (CHARSPEC + root_dir + root_files[i])

				elif is_pipe:
					filename = (PIPE + root_files[i]) if not args.full_pathnames else (PIPE + root_dir + root_files[i])

				elif is_socket:
					filename = (SOCKET + root_files[i]) if not args.full_pathnames else (SOCKET + root_dir + root_files[i])

				elif is_executable:
					if color not in [MATCH, FAILED]:
						filename = (EXECUTABLE + root_files[i]) if not args.full_pathnames else (EXECUTABLE + root_dir + root_files[i])
					else:
						filename = (color + root_files[i]) if not args.full_pathnames else (color + root_dir + root_files[i])
				else:
					
					filename = (color + root_files[i]) if not args.full_pathnames else (color + root_dir + root_files[i])

				''' Print file branch '''
				if not args.interesting_only:
					print(depth + child + color + filename + END + verbose + errormsg) if (i < (total_files + total_dirs) - 1) else print(depth + child_last + color + filename + END + verbose + errormsg)
					
				elif args.interesting_only and ((color and color == MATCH) and not errormsg):
					print(depth + child + color + filename + END + verbose + errormsg) if (i < (total_files + total_dirs) - 1) else print(depth + child_last + color + filename + END + verbose + errormsg)



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
				errormsg = ' [error accessing dir]'
						
			
			''' Check if symlink and if target leads to recursion '''
			if root_dirs[i] in symlinks:
				symlink_target = target = os.readlink(joined_path)
				target = fake2realpath(root_dir, target)			
				is_recursive = ' [recursive, not followed]' if target == root_dir[0:-1] else ''
				
				if len(is_recursive):
					recursive.append(joined_path)
					
				print(depth + child + LINK + directory + END + ' -> ' + DIR + symlink_target + END + is_recursive + errormsg) if i < total_dirs - 1 else print(depth + child_last + LINK + directory + END + ' -> ' + DIR + symlink_target + END + is_recursive + errormsg)
				
			else:
				print(depth + child + DIR + directory + END + errormsg) if i < total_dirs - 1 else print(depth + child_last + DIR + directory + END + errormsg)

			''' Iterate next dir '''
			if (not args.follow_links and root_dirs[i] not in symlinks) or (args.follow_links and not is_recursive):
				if (sub_dirs or sub_files) and (intent + 1) < depth_level:
					tmp = depth
					depth = depth + parent if i < (total_dirs - 1) else depth + '    '
					eviltree(joined_path + os.sep, intent + 1, depth)
					depth = tmp
			

	except StopIteration:
		print('\r' + DIR + root_dir + END + ' [Permission Denied]')
		#print('\r' + DIR + root_dir + END + ' [error accessing dir]')
		
	except UnicodeEncodeError:
		adjustUnicodeError()

	except KeyboardInterrupt:
		exit_with_msg('Keyboard interrupt.')

	except PermissionError:
		print('\r' + DIR + root_dir + END + ' [Permission Denied]')
	
	except Exception as e:
		exit_with_msg('Something went wrong. Consider creating an issue about this in the original repo (https://github.com/t3l3machus/eviltree)\n' + BOLD + 'Error Details' + END +': ' + str(e))



def main():
	
	try:
		print_banner() if not args.quiet else move_on()
		
	except UnicodeEncodeError:
		adjustUnicodeError()
	
	root_dir = args.root_path if args.root_path[-1] == os.sep else args.root_path + os.sep	
	
	if os.path.exists(root_dir):
		eviltree(root_dir)
		print('\n' + str(total_dirs_processed) + ' directories, ' + str(total_files_processed) + ' files')
		
	else:
		exit_with_msg('Directory does not exist.')
			


if __name__ == '__main__':
	main()
