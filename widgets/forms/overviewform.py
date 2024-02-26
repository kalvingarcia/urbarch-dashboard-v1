from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from api.urbandb import UrbanDB
from .form import FormStructure, Form, TextInput, CheckboxInput, SearchForm, TableForm, DropdownInput

class OptionsForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        self.__forms = []

        super(OptionsForm, self).__init__(*args, **kwargs)

    def add_form(self, data = None):
        pass

class FinishesForm(SearchForm):
    pass

class ComponentForm(SearchForm):
    pass

class ReplacementForm(SearchForm):
    pass

class CareForm(SearchForm):
    pass

class TagForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

    def search_database(self, text):
        if text != "":
            return UrbanDB.search_tags(text)
        return []

    def create_tag(self):
        categories = [{
            "value": category["id"],
            "text": category["name"]
        } for category in UrbanDB.get_tag_categories()]
        tag_form = Form(
            TextInput(form_id = "name"),
            DropdownInput(form_id = "category_id", data = categories),
            orientation = "vertical",
            adaptive_height = True
        )

        def send_tag(data):
            UrbanDB.create_tag(data)

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
        data = [UrbanDB.get_tag(id)[0] for id in ids]
        print(data)
        for tag in data:
            self.append(tag["id"], tag["name"])