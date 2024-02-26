from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText

# a form structure will be any class that contains form
# properties (in this case just being able to submit data)
class FormStructure:
    def __init__(self, *args, form_id = None, **kwargs):
        super(FormStructure, self).__init__(*args, **kwargs)
        self.form_id = form_id

    def prefill(self):
        pass

    # This function is inherited and implemented by
    # this classes children
    def submit(self):
        pass

# this class will be used as a container to hold other
# form structures
class Form(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, spacing = '30dp', **kwargs):
        self._form_structures = {}

        super(Form, self).__init__(*args, form_id = "__form", spacing = spacing, **kwargs)

        self.__on_submit = on_submit

    def prefill(self, data: dict):
        for key, value in data.items():
            try:
                self._form_structures[key].prefill(value)
            except Exception as e:
                print(str(e) + key + ": " + str(self._form_structures.keys()))

    def submit(self):
        submission = {}
        # go through the structure and call the submit
        # function to build the form submission dict
        for form_structure in self._form_structures.values():
            try:
                key, result = form_structure.submit()
                
                if key == "__form":
                    submission.update(result)
                else:
                    submission[key] = result
            except:
                raise Exception()
        # calling the on_submit callback and returning
        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, submission

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, FormStructure):
            if widget.form_id == "__form":
                self._form_structures.update(widget._form_structures)
            else:
                self._form_structures[widget.form_id] = widget
            return super(Form, self).add_widget(widget)

# this class uses the MDTextField, but enhances the
# class by using the form structure and adding a
# text change hook
class TextInput(FormStructure, MDTextField):
    def __init__(self, *args, on_submit = None, on_text_change = None, on_validate = None, **kwargs):
        super(TextInput, self).__init__(*args, **kwargs)

        self.__on_submit = on_submit
        self.__on_text_change = on_text_change
        self.__on_validate = on_validate
        self.write_tab = False

    def prefill(self, text):
        self.text = str(text)

    def submit(self):
        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, self.text

    # This function follows this structure which i previously
    # used to capture the set_text for the MDTextField class
    # but that was a bandaid test, this is a little more rigid
    # 
    # PREVIOUS CODE:
    # (This portion is just kivymd's function)
    # def set_text(*args):
    #     self.name.text = re.sub("\n", " ", text) if not self.name.multiline else text
    #     self.name.set_max_text_length()

    #     if self.name.text and self.name._get_has_error() or self.name._get_has_error():
    #         self.name.error = True
    #     elif self.name.text and not self.name._get_has_error():
    #         self.name.error = False

    #     # Start the appropriate texture animations when programmatically
    #     # pasting text into a text field.
    #     if len(self.name.text) != 0 and not self.name.focus:
    #         if self.name._hint_text_label:
    #             self.name._hint_text_label.font_size = theme_font_styles[self.name._hint_text_label.font_style]["small"]["font-size"]
    #             self.name._hint_text_label.texture_update()
    #             self.name.set_hint_text_font_size()

    #     if (not self.name.text and not self.name.focus) or (self.name.text and not self.name.focus):
    #         self.name.on_focus(instance, False)

    # set_text()
    # (Here is the part where I call the hook)
    # if hasattr(self, "tab_item"):
    #     self.tab_item.rename(self.name.text)
    def set_text(self, instance, text: str):
        super(TextInput, self).set_text(instance, text)
        if self.__on_text_change is not None:
            self.__on_text_change(text) # calling the text change hook

    def on_text_validate(self):
        super(TextInput, self).on_text_validate()
        if self.__on_validate is not None:
            self.__on_validate(self.text)

# This class combines the MDLabel and MDCheckbox into
# one class for ease of use in forms
class CheckboxInput(FormStructure, MDBoxLayout):
    def __init__(self, label_text, *args, value = None, group = None, on_submit = None, active = False, **kwargs):
        super(CheckboxInput, self).__init__(*args, **kwargs)

        self.value = value if value is not None else label_text

        self.__on_submit = on_submit

        self.__checkbox = MDCheckbox(group = group, active = active, pos_hint = {"center_y": 0.5})
        self.add_widget(self.__checkbox)
        self.add_widget(MDLabel(text = label_text, pos_hint = {"center_y": 0.5}))

    def prefill(self, active):
        self.__checkbox.active = active

    def submit(self):
        if self.__on_submit is not None:
            self.__on_submit()
        return self.value, self.__checkbox.active

# This class should be used to hold the checkboxes
# it automatically combines all active values into
# a list
class CheckGroup(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, **kwargs):
        self.__group = []

        super(CheckGroup, self).__init__(*args, **kwargs)

        self.orientation = "vertical"

        self.__on_submit = on_submit

    def prefill(self, active_values):
        for checkbox in self.__group:
            if checkbox.value in active_values:
                checkbox.prefill(True)

    def submit(self):
        active_values = []
        # go through the checkboxes in the group
        # and add them to the active value list
        for checkbox in self.__group:
            value, active = checkbox.submit()
            if active:
                active_values.append(value)

        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, active_values

    def add_widget(self, widget):
        if isinstance(widget, CheckboxInput):
            self.__group.append(widget)
            return super(CheckGroup, self).add_widget(widget)
        if isinstance(widget, MDLabel):
            return super(CheckGroup, self).add_widget(widget)

# Does the same as CheckboxInput but for MDSwitch
# This class enhances MDSwitch to allow ease of
# submitting data
class SwitchInput(FormStructure, MDBoxLayout):
    def __init__(self, label_text, *args, on_submit = None, active = False, **kwargs):
        super(SwitchInput, self).__init__(*args, **kwargs)

        self.__on_submit = on_submit

        self.add_widget(MDLabel(text = label_text, pos_hint = {"center_y": 0.5}))
        self.__switch = MDSwitch(active = active)
        self.add_widget(self.__switch)

    def prefill(self, active):
        self.__switch.active = active

    def submit(self):
        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, self.__switch.active

class DropdownInput(FormStructure, MDDropDownItem):
    def __init__(self, *args, data = None, default_entry = 0, **kwargs):
        super(DropdownInput, self).__init__(*args, **kwargs)

        self.font_style = "H1"

        self.__data = data
        items = [{
            "text": entry["text"],
            "on_release": lambda value = entry["value"], text = entry["text"]: self.set(value, text)
        } for entry in self.__data]
        self.dropdown = MDDropdownMenu(caller = self, items = items, position = "bottom")
        self._container = MDDropDownItemText()
        self.add_widget(self._container)

        self.set(self.__data[default_entry]["value"], self.__data[default_entry]["text"])

    def on_release(self):
        self.dropdown.open()

    def set(self, value, text):
        self.__value = value
        self._container.text = text

    def prefill(self, value):
        self.__value = value
        for entry in self.__data:
            if value == entry["value"]:
                self._container.text = entry["text"]

    def submit(self):
        return self.form_id, self.__value


class TableEntry(Form):
    def __init__(self, *args, form_name = None, on_remove, **kwargs):
        super(TableEntry, self).__init__(*args, **kwargs)
        self.orientation = "horizontal"

        self.size_hint_y = None
        self.height = "100dp"

        self.__remove_self = on_remove

        remove = MDIconButton(icon = "window-close")
        remove.bind(on_press = lambda *args: self.__remove_self(self))
        self.add_widget(remove)

class TableForm(FormStructure, MDScrollView):
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)

        self.size_hint_y = None
        self.height = "400dp"

        self.__container = MDBoxLayout(orientation = "vertical", adaptive_height = True, pos_hint = {"top": 1})
        button = MDButton(MDButtonText(text = "Add"))
        button.bind(on_press = lambda *args: self.add_entry())
        self.add_widget(MDBoxLayout(
            self.__container,
            button,
            orientation = "vertical",
            adaptive_height = True,
            pos_hint = {"bottom": 1}
        ))

    def prefill(self, entries):
        for entry in entries:
            self.add_entry(entry)

    def submit(self):
        submission = []
        for entry in self.__container.children:
            submission.append(entry.submit()[1])
        return form_id, submission

    def add_entry(self, entry = None):
        table_entry = TableEntry(
            TextInput(form_id = "display"),
            TextInput(form_id = "difference"),
            CheckboxInput("", form_id = "default"),
            on_remove = self.remove_entry
        )

        if entry is not None:
            table_entry.prefill(entry)

        self.__container.add_widget(table_entry)

    def remove_entry(self, entry):
        self.__container.remove_widget(entry)

# This class is a form extended MDChip used to create chips for the search form
class SearchChip(FormStructure, MDChip):
    def __init__(self, id, *args, **kwargs):
        super(SearchChip, self).__init__(*args, **kwargs)

        self.form_id = "__search_chip"

        self.__id = id

    def submit(self):
        return self.form_id, self.__id

class SearchResults(MDDropdownMenu):
    def __init__(self, *args, on_press = None, create_tag = None, **kwargs):
        super(SearchResults, self).__init__(*args, **kwargs)

        self.__on_press = on_press
        self.__create_tag = create_tag

        self.position = "bottom"

    def fill(self, data):
        data = [{
            "text": entry["name"],
            "on_release": lambda id = entry["id"], text = entry["name"]: self.__on_press(id, text)
        } for entry in data]
        if self.__create_tag is not None:
            data.append({
                "leading_icon": "plus",
                "text": "Create Tag",
                "on_release": self.__create_tag
            })
        self.on_items(self, data)
        self.open()

# This class is the form that houses all of the
# other pieces to create a dialog that allows search
class SearchForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.search_box = TextInput(on_validate = self.search)
        search_button = MDButton(MDButtonText(text = "Search"))
        search_button.bind(on_press = self.search)
        search_bar = MDBoxLayout(self.search_box, search_button)
        self.add_widget(search_bar)
        self.results = SearchResults(
            caller = self.search_box,
            on_press = self.append,
            create_tag = self.create_tag if hasattr(self, "create_tag") else None
        )

        self._container = MDStackLayout(adaptive_height = True)
        self.add_widget(self._container)

        self.orientation = "vertical"
        self.adaptive_height = True

    def append(self, id, text):
        if id not in [child.submit()[1] for child in self._container.children]:
            self._container.add_widget(SearchChip(id, MDChipText(text = text)))

    def search_database(self):
        return []

    def search(self, *args):
        self.results.fill(self.search_database(self.search_box.text))

        def append(*args):
            for chip in search_results.submit():
                self._container.add_widget(chip)
            dialog.dismiss()

    def submit(self):
        return self.form_id, [child.submit()[1] for child in self._container.children]



