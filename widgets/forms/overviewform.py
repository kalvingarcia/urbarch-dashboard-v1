from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from .form import FormStructure

class TableEntry(MDBoxLayout):
    pass

class TableForm(FormStructure, MDScrollView):
    def __init__(self, *args, **kwargs):
        super(TableForm, self).__init__(*args, **kwargs)

        self.__container = MDBoxLayout(orientation = "vertical")

    def prefill(self, entries):
        pass

    def submit(self):
        pass

    def add_entry(self, entry):
        pass

    def remove_entry(self, entry):
        pass

class FinishesForm(TableForm):
    pass

class OptionsForm(FormStructure):
    pass

class SearchForm(FormStructure, MDBoxLayout):
    pass

class ComponentForm(SearchForm):
    pass

class ReplacementForm(SearchForm):
    pass

class CareForm(SearchForm):
    pass

class TagForm(SearchForm):
    pass