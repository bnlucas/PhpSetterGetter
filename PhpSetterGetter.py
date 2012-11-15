import re

import sublime, sublime_plugin

# Cycle through all cursor positions and place the selected text into an
# array.
def getSelections(view):
	position = 0
	selected = []
	for sel in view.sel():
		if sel.end() > position:
			position = sel.end()
			line     = view.substr(sel)
			if "\r\n" in line:
				selected.extend(line.split("\r\n"))
			elif "\n" in line:
				selected.extend(line.split("\n"))
			else:
				selected.append(line)

	return {"position": position, "selections": selected}

# PhpSetterGetter base method. This was based off Enrique Ramirez's
# JavaSetterGetter @ https://github.com/enriquein/JavaSetterGetter
class PhpSetterGetterCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		# Pull last cursor position and a list of selected characters.
		selections	= getSelections(self.view)
		position	= selections['position']
		selected	= selections['selections']

		properties	= []
		output		= []

		for line in selected:
			# If property has a defined value, split it off.
			if "=" in line:
				line = line.split("=")[0]
			line = line.replace("\t", "").strip()
			if len(line) > 0 and line[0] != "@":
				segments = line.split()
				# If line doesn't contain a modifier, public, protected,
				# or private OR the property doesn't start with '$' the
				# line is not a class property.
				if len(segments) != 2 or segments[1][0] != "$":
					sublime.error_message("Please check that your properties "
						+ "are selected correctly.")
					return
				properties.append(segments[1])

		for prop in properties:
			# Get lowercase and uppercase versions of the property name
			# for set/get setProperty($property) / getProperty()
			lowercase = prop.lstrip("$").rstrip(";")
			uppercase = lowercase[0].capitalize() + lowercase[1:]

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
			# Begin edit.
			edit = self.view.begin_edit("php_setter_getter")
			insert = self.view.insert(edit, position, "\n".join(output))

			# Clear text selections in editor and selected generated
			# set/get methods.
			self.view.sel().clear()
			self.view.sel().add(sublime.Region(position, (position + insert)))
		finally:
			# End edit.
			self.view.end_edit(edit)