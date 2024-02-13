from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch

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
            except:
                print("Ignored")

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
    def __init__(self, *args, on_submit = None, on_text_change = None, **kwargs):
        super(TextInput, self).__init__(*args, **kwargs)

        self.__on_submit = on_submit
        self.__on_text_change = on_text_change

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

# This class combines the MDLabel and MDCheckbox into
# one class for ease of use in forms
class CheckboxInput(FormStructure, MDBoxLayout):
    def __init__(self, label_text, *args, value = None, group = None, on_submit = None, active = False, **kwargs):
        super(CheckboxInput, self).__init__(*args, **kwargs)

        self.value = value if value is not None else label_text

        self.__on_submit = on_submit

        self.__checkbox = MDCheckbox(group = group, active = active)
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
    def __init__(self, group_name, *args, on_submit = None, **kwargs):
        self.__group = []

        super(CheckGroup, self).__init__(*args, **kwargs)

        self.add_widget(MDLabel(text = group_name))

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





