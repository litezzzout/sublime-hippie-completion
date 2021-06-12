import sublime
import sublime_plugin
import re


matching = []
last_choice = ''
seed_search_word = ''
lookup_index = 0
class HippieWordCompletionCommand(sublime_plugin.TextCommand):
	def run(self, edit, backward=False):
		global last_choice
		global lookup_index
		global matching
		global seed_search_word

		search_word_region = self.view.word(self.view.sel()[0])
		search_word_text = self.view.substr(search_word_region)

		if search_word_text != last_choice:
			seed_search_word = search_word_text
			lookup_index = 0
			matching = []

			search_word_parts = re.findall('([A-Z])?([^A-Z]*)', search_word_text)
			search_word_parts = [item for t in search_word_parts for item in t if item]
			# print(search_word_parts)
			
			# [matching.append(s) for s in reversed(word_list) if s not in matching and s != search_word_text and s[0] == search_word_text[0] and did_match(s, search_word_text, search_word_parts]
			for word in reversed(word_list):
				if word not in matching and word != search_word_text and word[0] == search_word_text[0] and did_match(word, search_word_text, search_word_parts):
					matching.append(word)

			if not matching:
				for w_list in word_list_global.values():
					[matching.append(s) for s in w_list if s not in matching and s != search_word_text and s[0] == search_word_text[0] and did_match(s, search_word_text, search_word_parts)]

			if not matching:
				return

		else:
			 lookup_index += -1 if backward else +1

			
		try:
			last_choice = matching[lookup_index]
		except IndexError:
			# lookup_index = 0
			search_word_parts = re.findall('([A-Z])?([^A-Z]*)', seed_search_word)
			search_word_parts = [item for t in search_word_parts for item in t if item]

			for w_list in word_list_global.values():
				[matching.append(s) for s in w_list if s not in matching and s != search_word_text and s[0] == search_word_text[0] and  did_match(s, seed_search_word, search_word_parts)]
		finally:
			try:
				last_choice = matching[lookup_index]
			except:
				lookup_index = 0
				last_choice = matching[lookup_index]

		for caret in self.view.sel():
			self.view.replace(edit, self.view.word(caret), last_choice)

		# self.view.replace(edit, search_word_region, last_choice)


word_list_global = {}
word_pattern = re.compile(r'(\w+)', re.S)
class Listner(sublime_plugin.EventListener):
	def on_init(self, views):
		global word_list_global
		# [print(a.file_name()) for a in views]
		for view in views:
			contents = view.substr(sublime.Region(0, view.size()))
			word_list_global[view.file_name()] = word_pattern.findall(contents)

		# print(word_list_global)
		

	def on_modified_async(self, view):
		global word_list
		try:
			first_half  = view.substr(sublime.Region(0, view.sel()[0].begin()))
			second_half = view.substr(sublime.Region(view.sel()[0].begin(), view.size()))
			word_list = word_pattern.findall(second_half)
			word_list.extend(word_pattern.findall(first_half))
			word_list_global[view.file_name()] = word_list
			# print(word_list)
		except:
			pass


def did_match(word: str, search_word_text: str, search_word_parts: list)->bool:
	result = False
	if len(search_word_text) > 1 and '_' in word:
		for char in search_word_text:
			if char in word:
				result = True
			else:
				result = False
				break
	else:
		for word_part in  search_word_parts:
			if word_part in word:
				result = True
			else:
				result = False
				break
	
	return result
