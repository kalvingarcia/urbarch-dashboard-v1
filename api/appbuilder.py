import os
import sys
import inspect
from importlib import import_module
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager

# This is how far back in the stack '_get_caller_location' must look
# _get_caller_location() -> __init__() -> __new__() -> ScreenMaker()
BACK_TRACE = 3

# This is the ScreenMaker class API, where the Kivy Screens are created for the screen manager.
# Ideally, the class finds the pages subdirectory in the same place as the caller's directory.
# Then the ScreenMaker creates the screen manager and each page
class AppBuilder:
    def __init__(self):
        self.manager = MDScreenManager()

        # looking for the pages directory
        directory = self._get_caller_location() + "/pages"
        page_files =[name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))] # getting all the page files

        def switch_page(page):
            self.manager.current = page

        # creating the screens for the pages
        for page_file in page_files:
            new_page = self._create_page(os.path.join(directory, page_file))
            if new_page is not None:
                setattr(new_page, "_switch", switch_page)
                self.manager.add_widget(new_page) # only adding the pages that don't error
        self.manager.current = "home"

    # This function is used to create the screen manager and return it
    # since that is all this class does
    def __new__(cls):
        instance = super().__new__(cls)
        instance.__init__()
        return instance.manager

    def _get_caller_location(self):
        # get the path leading to this call to find the pages directory consistently
        caller_location = inspect.stack()[BACK_TRACE].filename
        return caller_location[: -(len(os.path.basename(caller_location)) + 1)]

    def _create_page(self, page_file):
        page_path = page_file[: -len(os.path.basename(page_file))]

        # appending the path of the file to the system so we can import directly
        sys.path.append(page_path)

        # getting the module name
        page_module_name = os.path.splitext(os.path.basename(page_file))[0]
        page_module = import_module(page_module_name) # importing the module dynamically

        try:
            class_name = "".join([word.title() for word in page_module_name.split('-')])
            cls = getattr(page_module, class_name)
            return cls()
        except Exception as error:
            print(error)
            return None