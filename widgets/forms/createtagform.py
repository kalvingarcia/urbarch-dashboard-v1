from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogContentContainer, MDDialogButtonContainer
from widgets.forms.form import FormStructure, Form, TextInput, DropdownInput
from api.database import Database

class CreateTagForm(MDDialog, FormStructure):
    def __init__(self, *args, on_submit = None, **kwargs):
        super(CreateTagForm, self).__init__(*args, **kwargs)

        self.__old_tag_id = None
        self.__on_submit = on_submit

        categories = [{
            "value": category["id"],
            "text": category["name"]
        } for category in Database.get_tag_category_list()]

        self.__form = Form(
            TextInput(
                MDTextFieldHintText(text = "Tag Name"),
                MDTextFieldHelperText(text = "This is the name displayed in tag lists."),
                form_id = "name"),
            DropdownInput(form_id = "category_id", data = categories),
            orientation = "vertical",
            adaptive_height = True
        )

        cancel = MDIconButton(icon = "window-close")
        cancel.bind(on_press = lambda *args: self.dismiss())

        complete = MDIconButton(icon = "check", style = "filled")
        complete.bind(on_press = lambda *args: self.submit())

        self.add_widget(MDDialogHeadlineText(text = "Tag Information"))
        self.add_widget(MDDialogContentContainer(
            self.__form
        ))
        self.add_widget(MDDialogButtonContainer(
            MDLabel(text = " "),
            cancel,
            complete
        ))

    def default(self):
        self.__form.default()
        self.open()

    def prefill(self, id):
        self.__old_tag_id = id
        self.__form.prefill(Database.get_tag(id))
        self.open()

    def submit(self):
        if self.__old_tag_id:
            Database.update_tag(self.__old_tag_id, self.__form.submit()[1])
        else:
            print(self.__form.submit()[1])
            Database.create_tag(self.__form.submit()[1])
        self.__old_tag_id = None
        if self.__on_submit:
            self.__on_submit()
        self.dismiss()