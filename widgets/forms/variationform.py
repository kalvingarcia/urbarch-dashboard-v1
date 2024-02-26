import re
from kivy.clock import Clock
from kivymd.uix.tab import MDTabsPrimary, MDTabsItem, MDTabsItemText
from kivymd.uix.textfield import MDTextFieldHintText, MDTextFieldHelperText, MDTextFieldLeadingIcon
from kivymd.uix.scrollview import MDScrollView
from .form import FormStructure, Form, TextInput, SwitchInput, CheckboxInput, CheckGroup
from .overviewform import TagForm
from api.makr import screen_unit

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
            Clock.schedule_once(set_width) # i'm assuming it is scheduled to delay the width until after the texture updates

class VariationFormSlide(FormStructure, MDScrollView):
    def __init__(self, variation_number, *args, **kwargs):
        super(VariationFormSlide, self).__init__(*args, **kwargs)

        self.__form = Form(
            Form(
                TextInput(
                    MDTextFieldHintText(text = "Variant Name"),
                    MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"ADA\""),
                    on_text_change = self.rename_tab,
                    form_id = "subname",
                    size_hint_y = None
                ),
                TextInput(
                    MDTextFieldHintText(text = "Variation Extension"),
                    MDTextFieldHelperText(text = "Example: for \"UA0040-A\", it would be \"A\""),
                    form_id = "extension",
                    size_hint_y = None
                ),
                TextInput(
                    MDTextFieldLeadingIcon(icon = "currency-usd"),
                    MDTextFieldHintText(text = "Variation Base Price"),
                    MDTextFieldHelperText(text = "Example: for \"Loft Light [ADA]\", it would be \"1095\""),
                    form_id = "price",
                    size_hint_y = None
                ),
                CheckGroup(
                    CheckboxInput("Dry Environments", value = "Dry", group = f"UL_{variation_number}", adaptive_height = True),
                    CheckboxInput("Wet Environments", value = "Wet", group = f"UL_{variation_number}",  adaptive_height = True),
                    CheckboxInput("None", group = f"UL_{variation_number}", active = True,  adaptive_height = True),
                    form_id = "overview",
                    size_hint_y = None,
                    adaptive_height = True
                ),
                SwitchInput("Display", form_id = "display"),
                orientation = "vertical",
                size_hint_x = 0.5,
                adaptive_height = True
            ),
            Form(
                TagForm(form_id = "tags"),
                orientation = "vertical",
                size_hint_x = 0.5,
                adaptive_height = True
            ),
            orientation = "horizontal",
            adaptive_height = True,
            padding = ['20dp'],
        )
        self.add_widget(self.__form)

    def prefill(self, data):
        self.__form.prefill(data)

    def submit(self):
        return "__variation", self.__form.submit()[1]

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
            height = 90 * screen_unit()[1]
        )
        self.add_widget(self.__content)

        # adding the default item tab
        self.add_tab()

    def prefill(self, variations):
        for variation in variations:
            self.add_tab(variation)

    def submit(self):
        variations = []
        for slide in self.get_slides_list():
            variations.append(slide.submit()[1])
        return "variations", variations

    def add_tab(self, data = None):
        tab = VariationFormTab(f"Variantion {self.__variation_number}")
        self.add_widget(tab)
        slide = VariationFormSlide(self.__variation_number)
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