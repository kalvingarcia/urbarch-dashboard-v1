from kivymd.uix.screen import MDScreen
from widgets.forms.salvageform import SalvageForm

class Salvage(MDScreen):
    def __init__(self, **kwargs):
        super(Salvage, self).__init__(**kwargs)
        self.name = "salvage"

        self.__salvage_id = None
        self.__salvage_form = SalvageForm(on_submit = lambda: self._switch("home"), on_cancel = lambda: self._switch("home"))
        self.add_widget(self.__salvage_form)

    def set_id(self, id):
        self.__salvage_id = id

    def on_pre_enter(self):
        if self.__salvage_id:
            self.__salvage_form.prefill(self.__salvage_id)
            self.__salvage_id = None
        else:
            self.__salvage_form.default()