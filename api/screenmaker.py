import os
import sys
import inspect
from importlib import import_module
from kivymd.uix.screenmanager import MDScreenManager as ScreenManager

def get_caller_loc():
    # get the path leading to this call to find the pages directory consistently
    caller_location = inspect.stack()[2].filename
    return caller_location[: -(len(os.path.basename(caller_location)) + 1)]

class ScreenMaker:
    '''
    '''
    def __init__(self):
        self.manager = ScreenManager()

        # looking for the pages directory
        directory = get_caller_loc() + "/pages"
        page_files =[name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))] # getting all the page files

        # creating the screens for the pages
        for page_file in page_files:
            new_page = self.create_page(os.path.join(directory, page_file))
            if new_page is not None:
                self.manager.add_widget(new_page) # only adding the pages that don't error
        self.manager.current = "home"

    def create_page(self, page_file):
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
        except Exception as e:
            print(f"[{bold_bright_red}ERROR{default}  ] [            ] {e}")
            print(f"[{bold_bright_red}ERROR{default}  ] [ScreenMaker ] The module {page_module_name} did not contain a proper page class.")