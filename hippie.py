import sublime
import sublime_plugin
import re


matching = []
last_choice = ''
orig_query = ''
lookup_index = 0
case_separator = re.compile(r'([A-Z])?([^A-Z]*)')

class HippieWordCompletionCommand(sublime_plugin.TextCommand):
	def run(self, edit, backward=False):
		global last_choice, lookup_index, matching, orig_query

		query_region = self.view.word(self.view.sel()[0])
		query = self.view.substr(sublime.Region(query_region.a, self.view.sel()[0].end()))

		if query != last_choice:
			orig_query = query
			lookup_index = 0 if backward else -1
			matching = []

			query_splitted_by_case = [item for t in case_separator.findall(query) for item in t if item]

			for word in words_from_cursor_to_end:
				if (word != query and word[0] == query[0] and 
					did_match(word, query, query_splitted_by_case)):
					matching.append(word)

			
			temp_list = []
			for word in words_from_begining_to_cursor:
				if (word != query and word[0] == query[0] and 
					did_match(word, query, query_splitted_by_case)):
					temp_list.append(word)
			matching.extend(reversed(temp_list))
	
			if not matching:
				for w_list in word_list_global.values():
					try: [matching.append(s) for s in w_list if s not in matching and s != query and 
							s[0] == query[0] and did_match(s, query, query_splitted_by_case)]
					except: pass
			if not matching:
				return

			if len(query) > 2: priortize_consecutive(query, matching)
			if len(query) > 1: priortize_combined(query, matching)
		else:
			 lookup_index += +1 if backward else -1
	
		try:
			last_choice = matching[lookup_index]
		except IndexError:
			temp = []
			orig_query_splitted_by_case = [item for t in case_separator.findall(orig_query) for item in t if item]
			for w_list in word_list_global.values(): # getting candidate words from other files
				try: [temp.append(s) for s in w_list if s not in matching and s != query and 
					s[0] == query[0] and  did_match(s, orig_query, orig_query_splitted_by_case)]
				except: pass
			if len(query) > 2: priortize_consecutive(query, temp)
			if len(query) > 1: priortize_combined(query, temp)
			matching.extend(temp)
		finally:
			try:
				last_choice = matching[lookup_index]
			except:
				lookup_index = -1
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
		global words_from_begining_to_cursor, words_from_cursor_to_end
		try:
			first_half  = view.substr(sublime.Region(0, view.sel()[0].begin()))
			second_half = view.substr(sublime.Region(view.sel()[0].begin(), view.size()))
			words_from_begining_to_cursor = list(dict.fromkeys(reversed(word_pattern.findall(first_half))))
			words_from_cursor_to_end = list(dict.fromkeys(word_pattern.findall(second_half)))

			word_list_global[view.file_name()] = words_from_begining_to_cursor.copy().extend(words_from_cursor_to_end)
		except:
			pass


def did_match(candidate_word: str, query: str, query_splitted_by_case: list)->bool:
	result = False
	if query in candidate_word:
		return True

	if len(query) > 1 and '_' in candidate_word:
		for char in query:
			if char in candidate_word:
				result = True
			else:
				result = False
				break
	else:
		for word_part in  query_splitted_by_case:
			if word_part in candidate_word:
				result = True
			else:
				result = False
				break
	
	return result

def priortize_consecutive(query:str, matches:list):
	available_slot = []
	for i in reversed(range(len(matches))):
		match = matches[i]
		if query in match:
			if len(available_slot) > 0:
				matches.remove(match)
				matches.insert(available_slot.pop(0), match)
				available_slot.append(i)
		else:
			available_slot.append(i)

def priortize_combined(query:str, matches:list):
	available_slot = []
	for i in reversed(range(len(matches))):
		match = matches[i]

		priortize = False
		match_part = match.split('_')
		if len(match_part) >= len(query):
			t_query = query
			for part in match_part:
				if part[0] in t_query:
					priortize = True
					t_query = t_query.replace(part[0], '', 1)
					if not t_query: break
				else:
					priortize = False
					break
		if priortize:
			if len(available_slot) > 0:
				matches.remove(match)
				matches.insert(available_slot.pop(0), match)
				available_slot.append(i)
		else:
			available_slot.append(i)
