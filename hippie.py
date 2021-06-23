import sublime
import sublime_plugin
import re


matching = []
last_choice = ''
seed_search_word = ''
lookup_index = 0
case_separator = re.compile(r'([A-Z])?([^A-Z]*)')

class HippieWordCompletionCommand(sublime_plugin.TextCommand):
	def run(self, edit, backward=False):
		global last_choice, lookup_index, matching, seed_search_word

		search_word_region = self.view.word(self.view.sel()[0])
		search_word = self.view.substr(sublime.Region(search_word_region.a, self.view.sel()[0].end()))

		if search_word != last_choice:
			seed_search_word = search_word
			lookup_index = 0 if backward else -1
			matching = []

			case_separated_s_word = [item for t in case_separator.findall(search_word) for item in t if item]

			for word in word_list_s:
				if (word != search_word and word[0] == search_word[0] and 
					did_match(word, search_word, case_separated_s_word)):
					matching.append(word)

			temp_list = []
			for word in word_list_f:
				if (word != search_word and word[0] == search_word[0] and 
					did_match(word, search_word, case_separated_s_word)):
					temp_list.append(word)
			matching.extend(reversed(temp_list))
		
			if not matching:
				for w_list in word_list_global.values():
					try: [matching.append(s) for s in w_list if s not in matching and s != search_word and 
							s[0] == search_word[0] and did_match(s, search_word, case_separated_s_word)]
					except: pass
			if not matching:
				return
		else:
			 lookup_index += +1 if backward else -1
	
		try:
			last_choice = matching[lookup_index]
		except IndexError:
			# lookup_index = 0
			case_separated_s_word = [item for t in case_separator.findall(seed_search_word) for item in t if item]

			for w_list in word_list_global.values(): # getting candidate words from other
				try: [matching.append(s) for s in w_list if s not in matching and s != search_word and 
					s[0] == search_word[0] and  did_match(s, seed_search_word, case_separated_s_word)]
				except: pass
		finally:
			try:
				last_choice = matching[lookup_index]
			except:
				lookup_index = 0
				last_choice = matching[lookup_index]

		for caret in self.view.sel():
			self.view.replace(edit, sublime.Region(self.view.word(caret).a, caret.end()), last_choice)

word_list_global = {}
word_pattern = re.compile(r'(\w+)', re.S)
class Listener(sublime_plugin.EventListener):
	def on_init(self, views):
		global word_list_global
		for view in views:
			contents = view.substr(sublime.Region(0, view.size()))
			word_list_global[view.file_name()] = list(dict.fromkeys(word_pattern.findall(contents)))

	def on_modified_async(self, view):
		global word_list_f, word_list_s
		try:
			first_half  = view.substr(sublime.Region(0, view.sel()[0].begin()))
			second_half = view.substr(sublime.Region(view.sel()[0].begin(), view.size()))
			word_list_f = list(dict.fromkeys(reversed(word_pattern.findall(first_half))))
			word_list_s = list(dict.fromkeys(word_pattern.findall(second_half)))

			word_list_global[view.file_name()] = word_list_f.copy().extend(word_list_s)
		except:
			pass


def did_match(candidate_word: str, search_word: str, case_separated_s_word: list)->bool:
	result = False
	if search_word in candidate_word:
		return True

	if len(search_word) > 1 and '_' in candidate_word:
		# priortize matching first letters in combined_word
		# priortize = False
		# for part in candidate_word.split('_'):
		# 	if part[0] in search_word:
		# 		priortize = True
		# 	else:
		# 		priortize = False
		# 		break
		# if priortize:
		# 	matching.insert(0, candidate_word)
		# 	return False

		for char in search_word:
			if char in candidate_word:
				result = True
			else:
				result = False
				break
	else:
		for word_part in  case_separated_s_word:
			if word_part in candidate_word:
				result = True
			else:
				result = False
				break
	
	return result
