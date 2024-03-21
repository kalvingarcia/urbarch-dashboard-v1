from kivymd.uix.screen import MDScreen
from widgets.forms.customform import CustomForm

class Custom(MDScreen):
    def __init__(self, **kwargs):
        super(Custom, self).__init__(**kwargs)
        self.name = "custom"

        self.__custom_id = None
        self.__custom_form = CustomForm(on_submit = lambda: self._switch("home"), on_cancel = lambda: self._switch("home"))
        self.add_widget(self.__custom_form)

    def set_id(self, id):
        self.__custom_id = id

    def on_pre_enter(self):
        if self.__custom_id:
            self.__custom_form.prefill(self.__custom_id)
            self.__custom_id = None
        else:
            self.__custom_form.default()