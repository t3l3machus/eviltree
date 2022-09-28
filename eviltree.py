#!/bin/python3
#
# Written by Panagiotis Chartas (t3l3machus)

import os, re, argparse
from sys import exit

''' Colors '''
DEBUG = '\033[0;38;5;214m'
GREEN = '\033[38;5;47m'
DIR = '\033[1;38;5;12m'
MATCH = '\033[1;38;5;220m'
RED = '\033[1;31m'
END = '\033[0m'



# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser(
	formatter_class=argparse.RawTextHelpFormatter,
	epilog='''
	
Usage examples:

'''
)

parser.add_argument("-r", "--root-path", action="store", help = "The root path to walk.", required = True)
parser.add_argument("-o", "--only-interesting", action="store_true", help = "List only those files that their content includes interesting keywords.")
parser.add_argument("-k", "--keywords", action="store", help = "Comma separated keywords to search for in files.")
parser.add_argument("-a", "--match-all", action="store_true", help = "By default, files are marked when at least one keyword is matched. Use this option to mark only files that match all given keywords.")
parser.add_argument("-l", "--level", action="store", help = "Descend only level directories deep", type = int)
parser.add_argument("-v", "--verbose", action="store_true", help = "Print information about which keyword(s) matched.")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()


def exit_with_msg(msg):
	print(f'[{DEBUG}Debug{END}] {msg}')
	exit(1)
	

# Init keywords list
default_keywords = ['passw', 'admin', 'token', 'user', 'secret']
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
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-l) must be greater than 0.') 

else:
	depth_level = 4096

# -------------- General Functions -------------- #

def print_banner():

	padding = '  '

	E = [[' ', '┌', '─', '┐'], [' ', '├┤',' '], [' ', '└','─','┘']]
	V = [[' ', '┬', ' ', ' ', '┬'], [' ', '└','┐','┌', '┘'], [' ', ' ','└','┘', ' ']]
	I =	[[' ', '┬'], [' ', '│',], [' ', '┴']]
	L = [[' ', '┬',' ',' '], [' ', '│',' ', ' '], [' ', '┴','─','┘']]
	T = [[' ', '┌','┬','┐'], [' ', ' ','│',' '], [' ', ' ','┴',' ']]
	R = [[' ', '┬','─','┐'], [' ', '├','┬','┘'], [' ', '┴','└','─']]

	banner = [E,V,I,L,T,R,E,E]
	final = []
	print('\r')
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
		


def file_inspector(file_path):
	
	try:
		with open(file_path, 'r') as _file:
			
			content = _file.read()
			matched = []
			
			for w in keywords:
				if re.search(w, content):
					matched.append(w)
					
					if not args.match_all and not args.verbose:
						return MATCH
			
			if not args.match_all and len(matched):
				return [MATCH, f" {GREEN}[{', '.join(matched)}]{END}"]
			
			if args.match_all and len(matched) == total_keywords:
				return MATCH if not args.verbose else [MATCH, f" {GREEN}[{', '.join(keywords)}]{END}"]
			
		return ''
		
	except UnicodeDecodeError:
		color = RED	



def eviltree(root_dir, intent = 0, depth = '', depth_level = depth_level):
			
	try:
		root_dirs = next(os.walk(root_dir))[1]
		root_files = next(os.walk(root_dir))[2]
		total_dirs = len(root_dirs)
		total_files = len(root_files)
		
		for i in range(0, total_files):
			
			details = file_inspector(f'{root_dir}{root_files[i]}')
			
			if isinstance(details, list):
				color = details[0]
				verbose = details[1]
			else:
				color = details
				verbose = ''
			
			if not args.only_interesting:
				print(f'{depth}├─── {color}{root_files[i]}{END}{verbose}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}└─── {color}{root_files[i]}{END}{verbose}')
				
			elif args.only_interesting and color:
				print(f'{depth}├─── {color}{root_files[i]}{END}{verbose}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}└─── {color}{root_files[i]}{END}{verbose}')


		for i in range(0, total_dirs):
			
			print(f'{depth}├─── {DIR}{root_dirs[i]}{END}') if i < total_dirs - 1 else print(f'{depth}└─── {DIR}{root_dirs[i]}{END}')
			joined_path = root_dir + root_dirs[i] + os.sep
			sub_dirs = next(os.walk(joined_path))[1]
			
			
			if len(sub_dirs) and (intent + 1) < depth_level:
				tmp = depth
				depth = depth + '│      ' if i < (total_dirs - 1) else depth + '       '
				eviltree(joined_path, intent + 1, depth)
				depth = tmp
		

	except Exception as e:
		print(e)



def main():
		
	print_banner() if not args.quiet else chill()

	root_dir = args.root_path if args.root_path[-1] == os.sep else args.root_path + os.sep
	print(f'\r{DIR}{root_dir}{END}')
	
	eviltree(root_dir)
	print('\r')



if __name__ == '__main__':
	main()


