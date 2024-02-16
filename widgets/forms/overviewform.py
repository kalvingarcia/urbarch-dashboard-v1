from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from kivymd.uix.textfield import MDTextFieldLeadingIcon
from kivymd.uix.divider import MDDivider
from api.urbandb import UrbanDB
from .form import FormStructure, Form, TextInput, CheckboxInput

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

class OptionsForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        self.__forms = []

        super(OptionsForm, self).__init__(*args, **kwargs)

    def add_form(self, data = None):
        pass

class SearchChip(FormStructure, MDChip):
    def __init__(self, id, *args, **kwargs):
        super(SearchChip, self).__init__(*args, **kwargs)

        self.form_id = "__search_chip"

        self.__id = id

    def submit(self):
        return self.form_id, self.__id

class SearchResult(MDLabel):
    def __init__(self, id, name, *args, on_press = None, **kwargs):
        super(SearchResult, self).__init__(*args, **kwargs)

        self.__id = id
        self.text = name
        self.__on_press = on_press

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.__on_press(self.__id, self.text)
            return True
        else:
            return super(SearchResult, self).on_touch_down(touch)

class SearchResults(MDBoxLayout):
    def __init__(self, *args, create_tag = None, **kwargs):
        super(SearchResults, self).__init__(*args, **kwargs)

        self.__search_results = MDBoxLayout()
        self.__submission = MDStackLayout()

        self.__create_tag = create_tag
        
        self.add_widget(MDScrollView(
            self.__search_results
        ))
        self.add_widget(self.__submission)

    def add_chip(self, id, text):
        self.__submission.add_widget(SearchChip(
            id,
            MDChipText(text = text)
        ))

    def submit(self):
        return self.__submission.children

    def fill(self, data):
        for entry in data:
            self.__search_results.add_widget(
                SearchResult(entry["id"], entry["name"], on_press = self.add_chip)
            )

            if self.__create_tag is not None:
                self.__search_results.add_widget(MDButton(
                    MDButtonText(text = "Create New Tag")
                ))

class SearchDialog(MDDialog):
    def __init__(self, *args, **kwargs):
        super(SearchDialog, self).__init__(*args, **kwargs)

class SearchForm(FormStructure, MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.__container = MDStackLayout()
        self.add_widget(self.__container)
        search_button = MDButton(MDButtonText(text = "Search"))
        search_button.bind(on_press = self.search)
        self.add_widget(search_button)

    def search_database(self):
        return []

    def search(self, *args):
        search_results = SearchResults()

        def fill_search_results(text):
            results = self.search_database(text)
            search_results.fill(results)

        add_results = MDButton(
            MDButtonText(text = "Complete")
        )
        add_results.bind(on_press = lambda *args: self.__container.children + search_results.submit())

        SearchDialog(
            MDDialogHeadlineText(text = "Search"),
            MDDialogContentContainer(
                TextInput(
                    MDTextFieldLeadingIcon(icon = "search"),
                    on_text_change = fill_search_results
                ),
                MDDivider(),
                search_results
            ),
            MDDialogButtonContainer(
                add_results
            )
        ).open()

    def __add_results(self, data):
        pass

    def prefill(self, chips):
        self.__add_results(chips)

    def submit(self):
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
        return UrbanDB.search_tags(text)

    def search(self, *args):
        search_results = SearchResults(create_tag = self.create_tag)

        def fill_search_results(text):
            results = self.search_database(text)
            search_results.fill(results)

        add_results = MDButton(
            MDButtonText(text = "Complete")
        )
        add_results.bind(on_press = lambda *args: self.__container.children + search_results.submit())

        SearchDialog(
            MDDialogHeadlineText(text = "Search"),
            MDDialogContentContainer(
                TextInput(
                    MDTextFieldLeadingIcon(icon = "search"),
                    on_text_change = fill_search_results
                ),
                MDDivider(),
                search_results
            ),
            MDDialogButtonContainer(
                add_results
            )
        ).open()

    def create_tag(self):
        tag_form = Form(
            TextInput(form_id = "id"),
            TextInput(form_id = "name"),
            TextInput(form_id = "group_id")
        )

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
        )