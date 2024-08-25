import os
import zipfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
import pandas as pd
from fpdf import FPDF
import win32timezone

class ChoiceDialog(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text="Where would you like to save the file?")
        self.add_widget(self.label)

        self.default_button = Button(text="Use Default Location (Documents)", on_press=self.use_default_location)
        self.custom_button = Button(text="Specify Location", on_press=self.specify_location)
        
        self.add_widget(self.default_button)
        self.add_widget(self.custom_button)

        self.callback = None
        self.popup = None

    def use_default_location(self, instance):
        if self.callback:
            self.callback(os.path.expanduser("~/Documents"))
        self.dismiss()

    def specify_location(self, instance):
        if self.callback:
            content = SaveDialog()
            content.popup = Popup(title="Save Payslip", content=content, size_hint=(0.8, 0.6))
            content.callback = self.callback
            content.popup.open()
        self.dismiss()

    def dismiss(self):
        if self.popup:
            self.popup.dismiss()

class SaveDialog(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.filechooser = FileChooserListView(filters=['*.pdf'])
        self.filechooser.path = os.path.expanduser("~/Documents")
        self.add_widget(self.filechooser)

        self.file_name_input = TextInput(hint_text="Enter file name", size_hint_y=None, height=40)
        self.add_widget(self.file_name_input)

        self.button_layout = BoxLayout(size_hint_y=None, height=50)
        self.save_button = Button(text="Save", on_press=self.save_file)
        self.cancel_button = Button(text="Cancel", on_press=self.cancel)
        self.button_layout.add_widget(self.save_button)
        self.button_layout.add_widget(self.cancel_button)
        self.add_widget(self.button_layout)

        self.callback = None
        self.popup = None

    def save_file(self, instance):
        file_name = self.file_name_input.text
        if file_name:
            selected_path = self.filechooser.path
            if not selected_path.endswith("/"):
                selected_path += "/"
            save_path = os.path.join(selected_path, file_name)
            if self.callback:
                self.callback(save_path)
        self.dismiss()

    def cancel(self, instance):
        self.dismiss()

    def dismiss(self):
        if self.popup:
            self.popup.dismiss()

class CompletionDialog(BoxLayout):
    def __init__(self, file_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.label = Label(text="Process Complete!")
        self.add_widget(self.label)

        self.file_path = file_path
        self.folder_path = os.path.dirname(file_path)  # Get the folder path

        self.link = Button(text=f"Open Folder ({file_path})", on_press=self.open_folder)
        self.add_widget(self.link)

        self.close_button = Button(text="Close", on_press=self.close)
        self.add_widget(self.close_button)

        self.popup = None

    def open_folder(self, instance):
        if os.path.isfile(self.file_path):
            os.startfile(os.path.dirname(self.file_path))

    def close(self, instance):
        self.dismiss()

    def dismiss(self):
        if self.popup:
            self.popup.dismiss()

class AboutDialog(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Add Favicon
        self.icon = Image(source='favicon.png', size_hint=(1, None), height=100)
        self.add_widget(self.icon)
        
        # Create a ScrollView for the content
        self.scrollview = ScrollView(size_hint=(1, 1))
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        # Add title
        self.title = Label(text="DolphinSoft", font_size='20sp', size_hint_y=None, height=40)
        self.content_layout.add_widget(self.title)
        
        # Add info
        self.info = Label(text=(
            "PayslipPro\n"
            "Version 1.0\n\n"
            "This application generates payslips from payroll data.\n\n"
            "Company Name: Dolphin Computer Solutions\n"
            "Contact: dolphincomputersolutions@outlook.com\n"
            "Website: https//usmandanazumi.onrender.com"
        ), size_hint_y=None, height=200)
        self.content_layout.add_widget(self.info)
        
        self.scrollview.add_widget(self.content_layout)
        self.add_widget(self.scrollview)

        self.close_button = Button(text="Close", size_hint_y=None, height=50, on_press=self.close)
        self.add_widget(self.close_button)

        self.popup = None

    def close(self, instance):
        self.dismiss()

    def dismiss(self):
        if self.popup:
            self.popup.dismiss()

class MenuBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 40
        self.padding = [10, 5, 10, 5]

        self.about_button = Button(text='About This App', on_press=self.show_about_dialog)
        self.add_widget(self.about_button)

    def show_about_dialog(self, instance):
        # Open about dialog
        content = AboutDialog()
        content.popup = Popup(title="About This App", content=content, size_hint=(0.8, 0.6))
        content.popup.open()

class PayslipGeneratorApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Add menu bar
        self.menu_bar = MenuBar()
        self.layout.add_widget(self.menu_bar)

        self.content_layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Upload Payroll Data")
        self.content_layout.add_widget(self.label)

        self.file_chooser = FileChooserListView(filters=['*.xlsx'])
        self.file_chooser.size_hint_y = None
        self.file_chooser.height = 300
        self.file_chooser.opacity = 0
        self.file_chooser.path = os.path.expanduser("~")

        self.content_layout.add_widget(self.file_chooser)

        self.upload_button = Button(text='Show File Chooser')
        self.upload_button.bind(on_press=self.show_file_chooser)
        self.content_layout.add_widget(self.upload_button)

        self.process_button = Button(text='Upload Excel File')
        self.process_button.bind(on_press=self.upload_file)
        self.process_button.disabled = True
        self.content_layout.add_widget(self.process_button)

        self.generate_button = Button(text='Generate Payslips')
        self.generate_button.bind(on_press=self.prompt_save_location)
        self.generate_button.disabled = True
        self.content_layout.add_widget(self.generate_button)

        self.progress_bar = ProgressBar()
        self.content_layout.add_widget(self.progress_bar)

        self.layout.add_widget(self.content_layout)

        return self.layout

    def show_file_chooser(self, instance):
        self.file_chooser.opacity = 1
        self.process_button.disabled = False

    def upload_file(self, instance):
        selected = self.file_chooser.selection
        if selected:
            self.file_path = selected[0]
            self.df = pd.read_excel(self.file_path)
            self.label.text = f"File loaded: {self.file_path}"
            self.generate_button.disabled = False
        self.file_chooser.opacity = 0

    def prompt_save_location(self, instance):
        # Open choice dialog
        content = ChoiceDialog()
        content.popup = Popup(title="Save Location", content=content, size_hint=(0.8, 0.4))
        content.callback = self.save_payslips
        content.popup.open()

    def save_payslips(self, save_path):
        total_rows = len(self.df.index)
        temp_dir = os.path.join(os.path.dirname(save_path), "temp_pdfs")
        os.makedirs(temp_dir, exist_ok=True)
        
        pdf_files = []

        for index, row in self.df.iterrows():
            employee_name = row['Name'].replace(" ", "_")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Payslip for {row['Name']}", ln=True, align='C')
            
            # Dynamically add cells for each header in the DataFrame
            for header in self.df.columns:
                if header != 'Name':  # Skip 'Name' since it is already used as the title
                    pdf.cell(200, 10, txt=f"{header}: {row[header]}", ln=True)
            
            pdf.cell(0, 10, txt="For support, contact: dolphincomputersolutions@outlook.com", ln=True, align='C')
            pdf.cell(0, 10, txt="Dolphin Computer Solutions", ln=True, align='C')

            file_name = f"{employee_name}.pdf"
            full_path = os.path.join(temp_dir, file_name)
            pdf.output(full_path)
            pdf_files.append(full_path)

        zip_file = os.path.join(os.path.dirname(save_path), "Payslips.zip")
        with zipfile.ZipFile(zip_file, 'w') as zf:
            for file in pdf_files:
                zf.write(file, os.path.basename(file))

        for file in pdf_files:
            os.remove(file)  # Remove the temporary PDF files

        self.progress_bar.value = 100
        self.label.text = "Payslips generated and zipped."

        content = CompletionDialog(file_path=zip_file)
        content.popup = Popup(title="Process Complete", content=content, size_hint=(0.8, 0.4))
        content.popup.open()

if __name__ == '__main__':
    PayslipGeneratorApp().run()
