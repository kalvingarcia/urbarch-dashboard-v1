import re
from kivy.clock import Clock
from kivymd.uix.tab import MDTabsPrimary, MDTabsItem, MDTabsItemText
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText, MDTextFieldLeadingIcon
from .form import FormStructure, Form, TextInput, SwitchInput, CheckboxInput, CheckGroup

class VariationFormTab(MDTabsItem):
    def __init__(self, tab_name, **kwargs):
        super(VariationFormTab, self).__init__(**kwargs)

        self.default_name = tab_name
        self.text = MDTabsItemText(text = tab_name)
        self.add_widget(self.text)

    # rename the tab
    def rename(self, new_name):
        if new_name == '':
            new_name = self.default_name
        self.text.text = new_name

        # this is the kivymd method for set_width
        # but they also "add_widget" which causes errors
        def set_width(*args):
            self.width = self.text.texture_size[0] + self.text.padding_x + 2

        if not self._tabs.allow_stretch and isinstance(self.text, MDTabsItemText):
            Clock.schedule_once(set_width) # i'm assuming it is scheduled to delay the width until after the textture updates

class VariationFormSlide(Form):
    def __init__(self, **kwargs):
        super(VariationFormSlide, self).__init__(**kwargs)
        self.orientation = "horizontal"

        self.add_widget(Form(
            TextInput(
                MDTextFieldHintText(text = "Variant Name"),
                MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"ADA\""),
                on_text_change = self.rename_tab,
                # size_hint_x = 0.6,
                form_id = "subname"
            ),
            TextInput(
                MDTextFieldHintText(text = "Variation Extension"),
                MDTextFieldHelperText(text = "Example: for \"UA0040-A\", it would be \"A\""),
                # size_hint_x = 0.4,
                form_id = "extension"
            ),
            TextInput(
                MDTextFieldLeadingIcon(icon = "currency-usd"),
                MDTextFieldHintText(text = "Variation Base Price"),
                MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"1095\""),
                form_id = "price"
            ),
            orientation = "vertical",
            size_hint_x = 0.5
        ))
        self.add_widget(Form(
            SwitchInput("Display", form_id = "display"),
            CheckGroup(
                "UL Listing",
                CheckboxInput("Dry Environments", value = "Dry", group = "UL"),
                CheckboxInput("Wet Environments", value = "Wet", group = "UL"),
                CheckboxInput("None", group = "UL")
            ),
            orientation = "vertical",
            size_hint_x = 0.5
        ))

    def rename_tab(self, text):
        if hasattr(self, "tab_item"):
            self.tab_item.rename(text)

from kivymd.uix.tab import MDTabsPrimary, MDTabsCarousel, MDTabsItem
from kivymd.uix.divider import MDDivider

class VariationForm(MDTabsPrimary, FormStructure):
    def __init__(self, **kwargs):
        super(VariationForm, self).__init__(form_id = "variations", **kwargs)

        self.allow_stretch = False
        self.label_only = True
        self.lock_swiping = True
        self.anim_diration = 0.1

        self.__variation_number = 0

        # creating the content structure
        self.__content = MDTabsCarousel(
            size_hint_y = None,
            height = '200dp'
        )
        self.add_widget(self.__content)

        # adding the default item tab
        self.add_tab()

    def prefill(self, variations):
        for variation in variations:
            print(variation)
            self.add_tab(variation)

    def submit(self):
        variations = []
        for slide in self.get_slides_list():
            variations.append(slide.submit()[1])
        return "variations", variations

    def add_tab(self, data = None):
        tab = VariationFormTab(f"Variantion {self.__variation_number}")
        self.add_widget(tab)
        slide = VariationFormSlide()
        self.__content.add_widget(slide)
        
        # if data is None then that means we aren't prefilling,
        # so the function was called by the form button
        if data is not None:
            slide.prefill(data)
        else:
            self._switch_tab(tab)

        # doing kivymd's work for them since they don't know how to code
        setattr(tab, "_tab_content", slide)
        setattr(slide, "tab_item", tab)
        # increment the count
        self.__variation_number += 1

    def remove_tab(self):
        tab = self.get_current_tab()
        if tab is not None:
            # figure out what the next active tab should be
            # next_tab = None
            # tab_list = self.get_tabs_list()
            # for i, t in enumerate(tab_list):
            #     if t is tab and i < len(tab_list) :
            #         next_tab = tab_list[i + 1]
            #     elif i >= len(tab_list):
            #         next_tab = tab_list[i - 1]

            # remove current tab
            self.__content.remove_widget(tab._tab_content)
            self.ids.container.remove_widget(tab)
            
            #set next_tab as active
            # if next_tab is not None:
            #     self._switch_tab(next_tab)