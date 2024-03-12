from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextFieldHintText
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from api.database import Database
from .form import FormStructure, Form, TextInput, CheckboxInput, SearchForm, TableForm, DropdownInput, TableEntry

class OptionsForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)

        self.form_id = "options"

        self.orientation = "vertical"
        self.adaptive_height = True

        add = MDButton(
            MDButtonText(text = "Add Option")
        )
        add.bind(on_press = lambda *args: self.add_form())

        self.__forms = MDBoxLayout(adaptive_height = True, orientation = "vertical",  pos_hint = {"top": 1})

        self.add_widget(MDBoxLayout(
            self.__forms,
            add,
            orientation = "vertical",
            adaptive_height = True,
            pos_hint = {"bottom": 1}
        ))

    def add_form(self, data = None):
        new_form = Form(
            TextInput(
                MDTextFieldHintText(text = "Option Name"),
                form_id = "option_name"
            ),
            TableForm(form_id = "option_content"),
            orientation = "vertical",
            adaptive_height = True
        )

        if data:
            new_form.prefill(data)
        self.__forms.add_widget(new_form)

    def prefill(self, data):
        for key, value in data.items():
            self.add_form({"option_name": key, "option_content": value})

    def submit(self):
        submission = {}
        for form in self.__forms.children:
            value = form.submit()[1]
            submission[value["option_name"]] = value["option_content"]
        return self.form_id, submission 

class FinishesForm(TableForm):
    def __init__(self, *args, **kwargs):
        super(FinishesForm, self).__init__(*args, **kwargs)

        self.form_id = "finishes"

    def add_entry(self, entry = None):
        finishes = [{"value": entry["id"], "text": entry["name"]} for entry in Database.get_metal_finishes_list()]
        table_entry = TableEntry(
            DropdownInput(form_id = "finish", data = finishes),
            TextInput(form_id = "difference"),
            CheckboxInput("", form_id = "default"),
            on_remove = self.remove_entry
        )

        if entry is not None:
            table_entry.prefill(entry)

        self._container.add_widget(table_entry)

class ReplacementForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(ReplacementForm, self).__init__(*args, **kwargs)

        self.form_id = "replacement_ids"
    
    def search_database(self, text):
        return Database.search_components(text)

    def prefill(self, ids):
        data = [Database.get_product(id)[0] for id in ids]
        for tag in data:
            self.append(tag["id"], tag["name"])

class TagForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

        self.form_id = "tags"

    def search_database(self, text):
        return Database.search_tags(text)

    def create_tag(self):
        categories = [{
            "value": category["id"],
            "text": category["name"]
        } for category in Database.get_tag_categories()]
        tag_form = Form(
            TextInput(form_id = "name"),
            DropdownInput(form_id = "category_id", data = categories),
            orientation = "vertical",
            adaptive_height = True
        )

        def send_tag(data):
            Database.create_tag(data)

        complete = MDButton(
            MDButtonText(text = "Add Tag")
        )
        complete.bind(on_press = lambda *args: send_tag(tag_form.submit()[1]))

        MDDialog(
            MDDialogHeadlineText(text = "New Tag"),
            MDDialogContentContainer(
                tag_form
            ),
            MDDialogButtonContainer(
                complete
            )
        ).open()

    def prefill(self, ids):
        data = [Database.get_tag(id)[0] for id in ids]
        for tag in data:
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