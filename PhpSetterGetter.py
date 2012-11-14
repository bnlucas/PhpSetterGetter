import re

import sublime, sublime_plugin

# Cycle through all cursor positions and place the selected text into an
# array.
def getLastSelection(view):
	position = 0
	selected = []
	sels 	 = view.sel()
	for sel in sels:
		if sel.end() > position:
			position = sel.end()
			selected.append(view.substr(sel))

	return [position, selected]

# PhpSetterGetter base method. This was based off Enrique Ramirez's
# JavaSetterGetter @ https://github.com/enriquein/JavaSetterGetter
class PhpSetterGetterCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		# Pull last cursor position and a list of selected characters.
		selection	= getLastSelection(self.view)
		position	= selection[0]
		selected	= selection[1]

		properties	= []
		output		= []

		for line in selected:
			# If property has a defined value, split it off.
			pattern = re.compile("=")
			if pattern.search(line):
				line = line.split(" =");
				line = line[0]
			line = line.replace("\t", "").strip()
			if len(line) > 0 and line[0] != "@":
				segments = line.split()
				# If line doesn't contain a modifier, public, protected,
				# or private OR the property doesn't start with '$' the
				# line is not a class property.
				if len(segments) != 2 or segments[1][0] != "$":
					sublime.error_message("Please check that your properties "
						+ "are selected correctly. [modifier $property]")
					return
				properties.append(segments[1])

		for prop in properties:
			# Get lowercase and uppercase versions of the property name
			# for set/get setProperty($property) / getProperty()
			lowercase = prop.lstrip("$").rstrip(";")
			uppercase = lowercase[0].capitalize() + lowercase[1:len(lowercase)]

			# Method templates for set and get.
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

			# Get final cursor position after methods have been inserted
			# and select that block of text.
			final = getLastSelection(self.view)
			self.view.sel().clear()
			self.view.sel().add(sublime.Region(position, final[0]))
		finally:
			self.view.end_edit(edit)