from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.tab import MDTabsPrimary, MDTabsItem, MDTabsItemText, MDTabsCarousel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.chip import MDChip, MDChipText, MDChipTrailingIcon
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText

# a form structure will be any class that contains form
# properties (in this case just being able to submit data)
class FormStructure:
    def __init__(self, *args, form_id = None, **kwargs):
        super(FormStructure, self).__init__(*args, **kwargs)
        self.form_id = form_id

    # This function is inherited and implemented by
    # this classes children
    def default(self):
        pass

    # This function is inherited and implemented by
    # this classes children
    def prefill(self):
        pass

    # This function is inherited and implemented by
    # this classes children
    def submit(self):
        pass

# this class will be used as a container to hold other
# form structures
class Form(FormStructure, MDBoxLayout):
    def __init__(self, *args, on_submit = None, spacing = '30dp', form_id = "__form", **kwargs):
        self._form_structures = {}

        super(Form, self).__init__(*args, spacing = spacing, form_id = form_id, **kwargs)

        self.__on_submit = on_submit

    def default(self):
        for form_structure in self._form_structures.values():
            form_structure.default()

    def prefill(self, data: dict):
        for key, value in data.items():
            if key in self._form_structures.keys():
                self._form_structures[key].prefill(value)

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
    def __init__(self, *args, default_text = "", on_submit = None, on_text_change = None, on_validate = None, **kwargs):
        super(TextInput, self).__init__(*args, **kwargs)

        self.__default_text = default_text
        self.__on_submit = on_submit
        self.__on_text_change = on_text_change
        self.__on_validate = on_validate
        self.write_tab = False

    def default(self):
        self.text = self.__default_text

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

# this class uses the MDTextField, but enhances the
# class by using the form structure and adding a
# text change hook
class NumberInput(FormStructure, MDTextField):
    def __init__(self, *args, default_text = 0, is_int = False, on_submit = None, on_text_change = None, on_validate = None, **kwargs):
        super(NumberInput, self).__init__(*args, **kwargs)

        self.__is_int = is_int
        self.__default_text = default_text
        self.__on_submit = on_submit
        self.__on_text_change = on_text_change
        self.__on_validate = on_validate
        self.write_tab = False

    def default(self):
        self.text = str(self.__default_text)

    def prefill(self, text):
        self.text = str(text)

    def submit(self):
        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, self.__default_text if self.text == '' else int(self.text) if self.__is_int else float(self.text)

    # This function follows this structure which i previously
    # used to capture the set_text for the MDTextField class
    # but that was a bandaid test, this is a little more rigid
    def set_text(self, instance, text: str):
        # This section of code is used to check and remove non-numerical characters
        new_text = ""
        for (index, c) in enumerate(text):
            if (c == '-' and index == 0) or c.isdigit() or (c == "." and not self.__is_int):
                new_text += c

        super(NumberInput, self).set_text(instance, new_text)
        if self.__on_text_change is not None:
            self.__on_text_change(new_text) # calling the text change hook

    def on_text_validate(self):
        super(NumberInput, self).on_text_validate()
        if self.__on_validate is not None:
            self.__on_validate(self.text)

# This class combines the MDLabel and MDCheckbox into
# one class for ease of use in forms
class CheckboxInput(FormStructure, MDBoxLayout):
    def __init__(self, *args, label = None, value = None, group = None, on_submit = None, active = False, **kwargs):
        super(CheckboxInput, self).__init__(*args, **kwargs)

        self.value = value if value is not None else self.form_id if self.form_id is not None else label

        self.__on_submit = on_submit

        self.__default_active = active

        self.__checkbox = MDCheckbox(group = group, active = active, pos_hint = {"center_y": 0.5})
        self.add_widget(self.__checkbox)
        if label:
            self.add_widget(MDLabel(text = label, adaptive_size = True, padding = "10dp"))
        
        self.spacing = "10dp"
        self.adaptive_height = True

    def default(self):
        self.__checkbox.active = self.__default_active

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

    def default(self):
        for checkbox in self.__group:
            checkbox.default()

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
    def __init__(self, *args, label = None, on_submit = None, active = False, **kwargs):
        super(SwitchInput, self).__init__(*args, **kwargs)

        self.__default_active = active

        self.__on_submit = on_submit

        if label:
            self.add_widget(MDLabel(text = label, pos_hint = {"center_y": 0.5}, adaptive_size = True, padding = "10dp"))
        self.__switch = MDSwitch(active = active, pos_hint = {"center_y": 0.5})
        self.add_widget(self.__switch)

        self.spacing = "10dp"
        self.adaptive_height = True

    def default(self):
        self.__switch.active = self.__default_active

    def prefill(self, active):
        self.__switch.active = active

    def submit(self):
        if self.__on_submit is not None:
            self.__on_submit()
        return self.form_id, self.__switch.active

class DropDownLabel(MDLabel):
    def __init__(self, *args, **kwargs):
        super(DropDownLabel, self).__init__(*args, **kwargs)
        self.adaptive_width = True

class DropdownInput(FormStructure, MDDropDownItem):
    def __init__(self, *args, data = None, default_entry = 0, **kwargs):
        super(DropdownInput, self).__init__(*args, **kwargs)

        self.__data = data
        items = [{
            "text": entry["text"],
            "on_release": lambda value = entry["value"], text = entry["text"]: self.set(value, text)
        } for entry in self.__data]
        self.dropdown = MDDropdownMenu(caller = self, items = items)

        self._drop_down_text = DropDownLabel(padding = ["10dp"])
        self._drop_down_text.bind(text=self.update_text_item)

        self.__default_entry = default_entry
        self.set(self.__data[default_entry]["value"], self.__data[default_entry]["text"])

    def on_release(self):
        self.dropdown.open()

    def set(self, value, text):
        self.__value = value
        self._drop_down_text.text = text

    def default(self):
        self.set(self.__data[self.__default_entry]["value"], self.__data[self.__default_entry]["text"])

    def prefill(self, value):
        self.__value = value
        for entry in self.__data:
            if value == entry["value"]:
                self._drop_down_text.text = entry["text"]

    def submit(self):
        return self.form_id, self.__value

class TableEntry(Form):
    def __init__(self, *args, form_name = None, on_remove, **kwargs):
        super(TableEntry, self).__init__(*args, **kwargs)
        self.orientation = "horizontal"

        self.adaptive_height = True

        self.__remove_self = on_remove

        remove = MDIconButton(icon = "window-close")
        remove.bind(on_press = lambda *args: self.__remove_self(self))
        self.add_widget(remove)

class TableForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True

        self._container = MDBoxLayout(orientation = "vertical", adaptive_height = True, pos_hint = {"top": 1})
        button = MDButton(MDButtonText(text = "Add Option"))
        button.bind(on_press = lambda *args: self.add_entry())
        self.add_widget(MDBoxLayout(
            self._container,
            button,
            orientation = "vertical",
            adaptive_height = True,
            pos_hint = {"bottom": 1}
        ))

    def default(self):
        self._container.clear_widgets()

    def prefill(self, entries):
        for entry in entries:
            self.add_entry(entry)

    def submit(self):
        submission = []
        for entry in self._container.children:
            submission.append(entry.submit()[1])
        return self.form_id, submission

    def add_entry(self, entry = None):
        table_entry = TableEntry(
            TextInput(MDTextFieldHintText(text = "Display Name"), form_id = "display", role = "medium"),
            NumberInput(MDTextFieldHintText(text = "Price Difference"), form_id = "difference", role = "medium"),
            CheckboxInput(form_id = "default", size_hint_x = 0.2),
            on_remove = self.remove_entry
        )

        if entry is not None:
            table_entry.prefill(entry)

        self._container.add_widget(table_entry)

    def remove_entry(self, entry):
        self._container.remove_widget(entry)

# This class is a form extended MDChip used to create chips for the search form
class SearchChip(FormStructure, MDChip):
    def __init__(self, id, *args, on_remove, **kwargs):
        super(SearchChip, self).__init__(*args, **kwargs)

        self.type = "input"
        self.form_id = "__search_chip"

        self.__remove_self = on_remove

        self.__id = id

    def on_release(self, *args):
        self.__remove_self(self)

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
            "text": f"{entry["name"]} [{entry["subname"]}]" if "subname" in entry.keys() else entry["name"],
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

        self.search_box = TextInput(MDTextFieldHintText(text = "Search"), on_validate = self.search)
        search_button = MDIconButton(icon = "magnify", pos_hint = {"center_y": 0.5})
        search_button.bind(on_press = self.search)
        search_bar = MDBoxLayout(self.search_box, search_button, adaptive_height = True, spacing = "10dp")
        self.add_widget(search_bar)
        self.results = SearchResults(
            caller = self.search_box,
            on_press = self.append,
            create_tag = self.create_tag if hasattr(self, "create_tag") else None,
            size_hint_x = None,
            width = self.search_box.width
        )

        self._container = MDStackLayout(adaptive_height = True)
        self.add_widget(self._container)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = "10dp"

    def remove_chip(self, chip):
        self._container.remove_widget(chip)

    def append(self, id, text):
        if id not in [child.submit()[1] for child in self._container.children]:
            icon = MDChipTrailingIcon(icon = "window-close")
            chip = SearchChip(
                id,
                MDChipText(text = text),
                icon,
                on_remove = self.remove_chip
            )
            icon.bind(on_press = lambda *args: self.remove_chip(chip))
            self._container.add_widget(chip)

    def search_database(self):
        return []

    def search(self, *args):
        self.results.fill(self.search_database(self.search_box.text))

    def default(self):
        self._container.clear_widgets()

    def submit(self):
        return self.form_id, [child.submit()[1] for child in self._container.children]

class TabFormItem(MDTabsItem):
    def __init__(self, *args, text = None, **kwargs):
        super(TabFormItem, self).__init__(*args, **kwargs)

        self.default_text = text
        self.text = MDTabsItemText(text = self.default_text)
        self.add_widget(self.text)

    def rename(self, text):
        if text == '':
            text = self.default_text
        self.text.text = text

        # this is the kivymd method for set_width
        # but they also "add_widget" which causes errors
        def set_width(*args):
            self.width = self.text.texture_size[0] + self.text.padding_x + 2

        # i'm assuming it is scheduled to delay the width until after the texture updates
        if not self._tabs.allow_stretch and isinstance(self.text, MDTabsItemText):
            Clock.schedule_once(set_width)

    def update_color(self):
        self.md_bg_color = self.theme_cls.surfaceBrightColor if self.active else self.theme_cls.surfaceColor

class TabForm(MDTabsPrimary, FormStructure):
    def __init__(self, *args, slide = None, **kwargs):
        super(TabForm, self).__init__(*args, **kwargs)

        self.allow_stretch = False
        self.label_only = True
        self.lock_swiping = True
        self.anim_diration = 0.1

        self.__slide = slide

        # creating the content structure
        self.__content = MDTabsCarousel(
            size_hint_y = None,
        )

        Window.bind(on_resize = self._on_window_resize)

    def _on_window_resize(self, window, width, height):
        self.__content.height = height - (1600 - 800)

    def on_tab_switch(self, tab, content):
        if isinstance(tab, TabFormItem):
            if self.target:
                self.target.tab_item.update_color()
            tab.update_color()

    def __clear(self):
        self.ids.container.clear_widgets()
        self.__content.clear_widgets()
        
        if not self._tabs_carousel:
            self.add_widget(self.__content)

    def default(self):
        self.__clear()
        # adding the default item tab
        self.add_tab()

    def prefill(self, forms):
        self.__clear()
        for form in forms:
            self.add_tab(form)

    def submit(self):
        forms = []
        for slide in self.get_slides_list():
            forms.append(slide.submit()[1])
        return self.form_id, forms

    def add_tab(self, data = None):        
        slide = self.__slide()
        self.__content.add_widget(slide)

        tab = TabFormItem(text = slide.default_name)
        self.add_widget(tab)
        
        # doing kivymd's work for them since they don't know how to code
        setattr(tab, "_tab_content", slide)
        setattr(slide, "tab_item", tab)

        # if data is None then that means we aren't prefilling,
        # so the function was called by the form button
        if data is not None:
            slide.prefill(data)
        self._switch_tab(tab)

    def remove_tab(self):
        tab = self.get_current_tab()
        if tab is not None:
            self.__content.remove_widget(tab._tab_content)
            self.ids.container.remove_widget(tab)
            return True
        return False

    def duplicate_tab(self):
        tab = self.get_current_tab()
        if tab is not None:
            self.add_tab(tab._tab_content.submit()[1])

