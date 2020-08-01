# Timothy Cotrell
# Version 1.0.1
import kivy
import inspect
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.gridlayout import GridLayout
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from datetime import date
from kivy.core.text import Label as CoreLabel
from kivy.uix.popup import Popup
from kivy.utils import *
from kivy.graphics import *
from kivy.storage.jsonstore import JsonStore

class OrganizationApp(App):
    def build(self):
        self.icon = 'TimImage.png'
        self.title = 'Tims Organization App'
        self.today = date.today() # Checks the day of the week and stores it as a date object
        days_of_the_week = ['M','T','W','Th','F','Sa','Su']
        days_in_each_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.days_of_the_week_typed_out = [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.list_of_tasks = [
            'todays_tasks', 'day_two_tasks', 'day_three_tasks', 'day_four_tasks', 'day_five_tasks', 
            'day_six_tasks', 'day_seven_tasks']
        self.storage = JsonStore('Tasks.json')
        self.storage.clear()
        
        # Creates a main layout and two smaller layouts to go into it (top and bottom half)
        main_layout = PageLayout(border=50)
        page_one_layout = BoxLayout(orientation="vertical")
        page_two_layout = GridLayout(cols=7, rows=8)
        self.top_half_layout = GridLayout(cols=2, rows=7)
        bottom_half_layout = BoxLayout(orientation="vertical")
        page_one_layout.add_widget(self.top_half_layout)
        page_one_layout.add_widget(bottom_half_layout)
        main_layout.add_widget(page_one_layout)
        main_layout.add_widget(page_two_layout)

        # binds the second page too a color
        # page_one_layout.bind(pos=self.update_rect, size=self.update_rect)
        page_two_layout.bind(pos=self.update_rect, size=self.update_rect)
        with page_one_layout.canvas:
            Color(1, 0, 0, 1) #red
            self.rect = Rectangle(size=page_one_layout.size, pos=page_one_layout.pos)

        # ids will be a number between 0 and 7, todays_tasks will always be 0 and day_sevens_tasks will 
        # always be 7 creates a Label for all of the days of the week, then creates an empty label to put 
        # next to the Labels of the week
        for i in range(7):
            label_day = date.fromordinal(self.today.toordinal() + i)
            labels_days_of_the_week = Label(text=f'{days_of_the_week[(self.today.weekday() + i) % 7]} {int(label_day.strftime("%d"))}', 
            size_hint_x=None, width=80)
            tasks = Label(markup=True)
            tasks.ids = {self.list_of_tasks[i]:i}
            self.top_half_layout.add_widget(labels_days_of_the_week)
            self.top_half_layout.add_widget(tasks)
            
        # creates the main text box that the user can use to add tasks 
        self.main_text_input = TextInput()
        bottom_half_layout.add_widget(self.main_text_input)

        # creates the add and remove buttons at the bottom of the app. Puts those buttons in a layout 
        # and adds the layout to the bottom half layout
        add_button = Button(text="add")
        remove_button = Button(text="remove")
        buttons = BoxLayout()
        buttons.add_widget(add_button)
        add_button.bind(on_press=self.on_add_button_press)
        remove_button.bind(on_press=self.on_remove_button_press)
        buttons.add_widget(remove_button)
        bottom_half_layout.add_widget(buttons)

        # creates the second page of the app
        first_day_of_the_month = date(self.today.year, self.today.month, 1)
        MonthName = Label(text=self.today.strftime('%B'))
        page_two_layout.add_widget(MonthName)
        for i in range(6):
            page_two_layout.add_widget(Label())
        for i in range(7):
            page_two_layout.add_widget(Label(text=days_of_the_week[i]))
        for i in range(42):
            if i < first_day_of_the_month.weekday():
                page_two_layout.add_widget(Label()) #adds empty labels so the first of the month starts in the correct col
            elif i - first_day_of_the_month.weekday() <= days_in_each_month[self.today.month] - 1:
                calender_buttons = Button(text=str(i - first_day_of_the_month.weekday() + 1))
                calender_buttons.ids = {'day of the month':i - 1}
                page_two_layout.add_widget(calender_buttons)
                calender_buttons.bind(on_press=self.on_calender_button_press)
            else:
                break

        return main_layout

    def update_rect(self, instance, value):
        """This function fits the color to the background"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_calender_button_press(self, instance):
        """Pulls up a popup that is veyr similar to the first page that shares a text box with"""
        # creates all the widgets for the popup window
        calender_day_popup_layout = BoxLayout(orientation="vertical")
        calender_day_popup_layout_top = BoxLayout(orientation="vertical")
        calender_day_popup_layout_bottom = BoxLayout(orientation="vertical")
        calender_day_popup_button_layout = BoxLayout(orientation="horizontal")
        self.button_day = date(self.today.year, self.today.month, sum(instance.ids.values()))

        self.calender_text_input = TextInput()
        self.calender_day_tasks = Label(text='')
        calender_add_button = Button(text='add')
        calender_add_button.bind(on_press=self.calender_popup_add_on_press)
        calender_remove_button = Button(text='remove')
        calender_remove_button.bind(on_press=self.calender_popup_remove_on_press)

        calender_day_popup_layout_top.add_widget(self.calender_day_tasks)
        calender_day_popup_layout_bottom.add_widget(self.calender_text_input)
        calender_day_popup_button_layout.add_widget(calender_add_button)
        calender_day_popup_button_layout.add_widget(calender_remove_button)
        calender_day_popup_layout_bottom.add_widget(calender_day_popup_button_layout)

        # if the day that is choosen is today or the next 6 days then keep the tasks the same as on the first page
        if self.button_day.toordinal() >= self.today.toordinal() and self.button_day.toordinal() - 6 <= self.today.toordinal():
            diffrence = self.button_day.toordinal() - (self.today.toordinal() - 1)
            num = (((-(diffrence) * 2) + 12) + (self.today.weekday() * 2)) % 14
            # self.calender_day_tasks.text = self.top_half_layout.__getattribute__('children')[num].text
            try:
                self.calender_day_tasks.text = list(self.storage.get(self.button_day.strftime('%c')).values())[0]
            except KeyError:
                print('Had a KeyError')
        calender_day_popup_layout.add_widget(calender_day_popup_layout_top)
        calender_day_popup_layout.add_widget(calender_day_popup_layout_bottom)
        calender_popup = Popup(title=f"{self.button_day.strftime('%A')} the {instance.text}th", content=calender_day_popup_layout)
        calender_popup.open()

    def calender_popup_add_on_press(self, instance):
        """Allows the user to add addicitonal tasks on the second page, also allows you to add tasks that arnt in this week"""
        if self.calender_day_tasks.text == '':
            self.calender_day_tasks.text = f'{self.calender_day_tasks.text}• {self.calender_text_input.text}'
        else:
            self.calender_day_tasks.text = f'{self.calender_day_tasks.text}\n• {self.calender_text_input.text}'
        if self.button_day.toordinal() >= self.today.toordinal() and self.button_day.toordinal() - 7 <= self.today.toordinal():
            diffrence = self.button_day.toordinal() - (self.today.toordinal() - 1)
            num = (((-(diffrence) * 2) + 12) + (self.today.weekday() * 2)) % 14
            self.top_half_layout.__getattribute__('children')[num].text = self.calender_day_tasks.text
        self.storage.put(self.button_day.strftime('%c'), text=self.calender_day_tasks.text)
    
    def calender_popup_remove_on_press(self, instance):
        """removes all the tasks from a day"""
        self.calender_day_tasks.text = ''

    
    # when the add button is pressed a popup window will show all of the days of the week so the user 
    # can choose a day to add the task too The popup buttons are given a ids attribute (0-6) baced on the 
    # day of the week
    def on_add_button_press(self, instance):
        """When the add buttons is pressed it will bring up a window with 7 buttons for each day of the 
        week, each button will add
        the text from the main text input to that day of the week"""
        add_popup_layout = BoxLayout(orientation="vertical")
        for i in range(7):
            add_popup_buttons = Button(text=self.days_of_the_week_typed_out[i])
            add_popup_buttons.ids = {self.list_of_tasks[i]:i}
            add_popup_buttons.bind(on_press=self.add_task_button_on_press)
            add_popup_layout.add_widget(add_popup_buttons)
        self.add_popup = Popup(title='What day do you want to add this task too?', content=add_popup_layout)
        self.add_popup.open()
    
    # when the add task button is pressed the text inside the main text box will be placed in the correct 
    # label
    def add_task_button_on_press(self, instance):
        """When a task button from the add button popup is pressed its will add the task from the text 
        input to that day of the week"""
        num = (((-(sum(instance.ids.values())) * 2) + 12) + (self.today.weekday() * 2)) % 14
        if self.top_half_layout.__getattribute__('children')[num].text != '':
            self.top_half_layout.__getattribute__('children')[num].text = f"{self.top_half_layout.__getattribute__('children')[num].text}\n• {self.main_text_input.text}"
        else:
            self.top_half_layout.__getattribute__('children')[num].text = f"• {self.main_text_input.text}"
        self.storage.put(date.fromordinal(self.today.toordinal() + sum(instance.ids.values()) - self.today.weekday()).strftime('%c'),
        text=self.top_half_layout.__getattribute__('children')[num].text)
        self.add_popup.dismiss()
    
    # when the remove button is pressed a popup window will show all o fhte days of the week so the user
    # can choose a day to remove a task from
    # The popup buttons are given a ids attribute (0-6) baced on the day of the week
    def on_remove_button_press(self, instance):
        """When the remove button is pressed then it will bring up a popup window with buttons to choose 
        witch day of the week you want a task to be removed from"""
        remove_popup_layout = BoxLayout(orientation="vertical")
        for i in range(7):
            remove_popup_buttons = Button(text=self.days_of_the_week_typed_out[i])
            remove_popup_buttons.ids = {self.list_of_tasks[i]:i}
            remove_popup_buttons.bind(on_press=self.remove_task_button_on_press)
            remove_popup_layout.add_widget(remove_popup_buttons)
        self.remove_popup = Popup(title='What day would you like to remove a task from', content=remove_popup_layout)
        self.remove_popup.open()

    # when the remove task button is pressed the text inside of the label with the name of the week that 
    # is the same as the button will be removed
    def remove_task_button_on_press(self, instance):
        """When the task button from the remove popup is pressed then the task from that day of the week 
        will be removed"""
        self.top_half_layout.__getattribute__('children')[(((-(sum(instance.ids.values()))
        * 2) + 12) + (self.today.weekday() * 2)) % 14].text = ''
        try:
            self.storage.delete(date.fromordinal(self.today.toordinal() + sum(instance.ids.values()) - self.today.weekday()).strftime('%c'))
        except KeyError:
            pass
        self.remove_popup.dismiss()
            
if __name__ == "__main__":
    app = OrganizationApp()
    app.run()