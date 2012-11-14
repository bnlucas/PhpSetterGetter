import re

import sublime, sublime_plugin

class PhpSetterGetterCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		position	= 0
		selected	= []
		properties	= []
		output		= []

		sels = self.view.sel()
		for sel in sels:
			if sel.end > position:
				position = sel.end()
				selected.append(self.view.substr(sel))

		for line in selected:
			pattern = re.compile("=")
			if pattern.search(line):
				line = line.split(" =");
				line = line[0]
			line = line.replace("\t", "").strip()
			if len(line) > 0 and line[0] != "@":
				segments = line.split()
				if len(segments) != 2 or segments[1][0] != "$":
					sublime.error_message("Please check that your properties "
						+ "are selected correctly. [modifier $property]")
					return
				properties.append(segments[1])

		for prop in properties:
			lowercase = prop.lstrip("$").rstrip(";")
			uppercase = lowercase[0].capitalize() + lowercase[1:len(lowercase)]
			template = """
	public function set{0}(${1}) {{
		$this->{1} = ${1};
		return $this;
	}}

	public function get{0}() {{
		return $this->{1};
	}}"""
			output.append(template.format(uppercase, lowercase))

		try:
			edit = self.view.begin_edit("php_setter_getter")
			self.view.insert(edit, position, "\n".join(output))
			last = 0
			sels = self.view.sel()
			for sel in sels:
				if sel.end > last:
					last = sel.end()
			print(last)
			self.view.sel().clear()
			self.view.sel().add(sublime.Region(position, last))
		finally:
			self.view.end_edit(edit)