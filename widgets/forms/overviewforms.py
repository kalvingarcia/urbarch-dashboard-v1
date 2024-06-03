from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from api.database import Database
from widgets.forms.createtagform import CreateTagForm
from .form import FormStructure, Form, TextInput, NumberInput, CheckboxInput, SearchForm, TableForm, DropdownInput, TableEntry

class OptionsForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)

        self.form_id = "options"

        self.orientation = "vertical"
        self.adaptive_height = True

        add = MDIconButton(icon = "plus", style = "filled")
        add.bind(on_press = lambda *args: self.add_form())

        self.__forms = MDBoxLayout(adaptive_height = True, orientation = "vertical",  pos_hint = {"top": 1}, spacing = "10dp")

        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                MDLabel(text = "Options", adaptive_size = True, pos_hint = {"center_y": 0.5}, font_style = "Headline", role = "small"),
                add,
                adaptive_height = True,
                spacing = "10dp"
            ),
            self.__forms,
            orientation = "vertical",
            adaptive_height = True,
            pos_hint = {"bottom": 1},
            spacing = "20dp"
        ))

    def add_form(self, data = None):
        remove = MDIconButton(icon = "window-close")

        new_form = Form(
            Form(
                Form(
                    TextInput(
                        MDTextFieldHintText(text = "Option Name"),
                        form_id = "option_name",
                        role = "medium"
                    ),
                    remove,
                    adaptive_height = True,
                    spacing = "10dp"
                ),
                Form(
                    CheckboxInput(
                        label = "Linked",
                        form_id = "link",
                        size_hint_x = 0.25
                    ),
                    TextInput(
                        MDTextFieldHintText(text = "Link Name"),
                        form_id = "link_name",
                        role = "small"
                    ),
                    adaptive_height = True,
                    spacing = "5dp"
                ),
                orientation = "vertical",
                adaptive_height = True,
                spacing = "5dp"
            ),
            TableForm(form_id = "option_content"),
            orientation = "vertical",
            adaptive_height = True
        )

        remove.bind(on_release = lambda *args: self.__forms.remove_widget(new_form))

        if data:
            new_form.prefill(data)
        self.__forms.add_widget(new_form)

    def prefill(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                print(value['link'])
                self.add_form({"option_name": key, "link": value["link"], "link_name": value["link_name"], "option_content": value["content"]})
            else:
                self.add_form({"option_name": key,  "option_content": value})
    
    def submit(self):
        submission = {}
        for form in self.__forms.children:
            value = form.submit()[1]
            submission[value["option_name"]] = {"link": value["link"], "link_name": value["link_name"], "content": value["option_content"]}
        return self.form_id, submission 

class FinishesForm(TableForm):
    def __init__(self, *args, **kwargs):
        super(FinishesForm, self).__init__(*args, **kwargs)

        self.form_id = "finishes"

    def add_entry(self, entry = None):
        finishes = [{"value": entry["id"], "text": entry["name"]} for entry in Database.get_metal_finishes_list()]
        table_entry = TableEntry(
            DropdownInput(form_id = "finish", data = finishes),
            NumberInput(MDTextFieldHintText(text = "Price Difference"), form_id = "difference", role = "medium"),
            CheckboxInput(form_id = "default", size_hint_x = 0.2),
            on_remove = self.remove_entry
        )

        if entry is not None:
            table_entry.prefill(entry)

        self._container.add_widget(table_entry)

class ReplacementForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(ReplacementForm, self).__init__(*args, **kwargs)

        self.form_id = "replacements"
    
    def search_database(self, text):
        return Database.get_replacement_list(text)

    def prefill(self, replacements):
        replacements = [Database.get_replacement(replacement["id"], replacement["extension"]) for replacement in replacements]
        for replacement in replacements:
            self.append({"id": replacement["id"]["id"], "extension": replacement["id"]["extension"]}, replacement["name"])

    def submit(self):
        return self.form_id, [child.submit()[1] for child in self._container.children]

class TagForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

        self.form_id = "tags"

    def search_database(self, text):
        return Database.get_tag_list(text)

    def create_tag(self):
        CreateTagForm().open()

    def prefill(self, tags):
        tags = [Database.get_tag(tag) for tag in tags]
        for tag in tags:
            self.append(tag["id"], tag["name"])

class ProductVariationForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(ProductVariationForm, self).__init__(*args, **kwargs)

        self.form_id = "__form"

    def search_database(self, text):
        return Database.search_products(text)

    def prefill(self, data):
        data = [Database.get_product(id)[0] for id in ids]
        for tag in data:
            self.append(tag["id"], tag["name"])