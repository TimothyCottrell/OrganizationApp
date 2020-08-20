# Timothy Cotrell
# Version 1.0.2
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

            if label_day == self.today:
                for i in self.storage.keys():
                    temp = date.fromisoformat(i)
                    if temp < label_day:
                        self.storage.put(label_day.isoformat(), text=list(self.storage.get(temp.isoformat()).values())[0])
                        self.storage.delete(i)
                    
            if self.storage.exists(label_day.isoformat()):
                tasks.text = list(self.storage.get(label_day.isoformat()).values())[0]

            self.top_half_layout.add_widget(labels_days_of_the_week)
            self.top_half_layout.add_widget(tasks)
            
        # creates the main text box that the user can use to add tasks 
        self.main_text_input = TextInput()
        bottom_half_layout.add_widget(self.main_text_input)

        # creates the add and remove buttons at the bottom of the app. Puts those buttons in a layout 
        # and adds the layout to the bottom half layout
        add_button = Button(text="add")
        move_button = Button(text="move")
        remove_button = Button(text="remove")
        buttons = BoxLayout()
        add_button.bind(on_press=self.on_add_button_press)
        move_button.bind(on_press=self.on_move_button_press)
        remove_button.bind(on_press=self.on_remove_button_press)
        buttons.add_widget(add_button)
        buttons.add_widget(move_button)
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
                calendar_buttons = Button(text=str(i - first_day_of_the_month.weekday() + 1))
                current_day = date(self.today.year, self.today.month, i - first_day_of_the_month.weekday() + 1)
                calendar_buttons.ids = {current_day.isoformat():i - first_day_of_the_month.weekday() + 1}
                page_two_layout.add_widget(calendar_buttons)
                calendar_buttons.bind(on_press=self.on_calendar_button_press)
            else:
                break
        # self.refresh()

        return main_layout

    def update_rect(self, instance, value):
        """This function fits the color to the background"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_calendar_button_press(self, instance):
        """Pulls up a popup that is veyr similar to the first page that shares a text box with"""
        # creates all the widgets for the popup window
        calendar_day_popup_layout = BoxLayout(orientation="vertical")
        calendar_day_popup_layout_top = BoxLayout(orientation="vertical")
        calendar_day_popup_layout_bottom = BoxLayout(orientation="vertical")
        calendar_day_popup_button_layout = BoxLayout(orientation="horizontal")
        self.button_day = date(self.today.year, self.today.month, sum(instance.ids.values()))

        self.calendar_text_input = TextInput()
        self.calendar_day_tasks = Label(text='')
        calendar_add_button = Button(text='add')
        calendar_add_button.bind(on_press=self.calendar_popup_add_on_press)
        calendar_remove_button = Button(text='remove')
        calendar_remove_button.ids = {list(instance.ids.keys())[0]:sum(instance.ids.values())}
        calendar_remove_button.bind(on_press=self.remove_task_button_on_press)
        calendar_move_button = Button(text='move')
        calendar_move_button.bind(on_press=self.move_task_button_on_press)

        calendar_day_popup_layout_top.add_widget(self.calendar_day_tasks)
        calendar_day_popup_layout_bottom.add_widget(self.calendar_text_input)
        calendar_day_popup_button_layout.add_widget(calendar_add_button)
        calendar_day_popup_button_layout.add_widget(calendar_move_button)
        calendar_day_popup_button_layout.add_widget(calendar_remove_button)
        calendar_day_popup_layout_bottom.add_widget(calendar_day_popup_button_layout)

        # if the day that is choosen is today or the next 6 days then keep the tasks the same as on the first page
        if self.button_day.toordinal() >= self.today.toordinal() and self.button_day.toordinal() - 6 <= self.today.toordinal():
            diffrence = self.button_day.toordinal() - (self.today.toordinal() - 1)
            num = (((-(diffrence) * 2) + 12) + (self.today.weekday() * 2)) % 14
            try:
                self.calendar_day_tasks.text = list(self.storage.get(self.button_day.isoformat()).values())[0]
            except KeyError:
                print('Had a KeyError: No task for this day')
        calendar_day_popup_layout.add_widget(calendar_day_popup_layout_top)
        calendar_day_popup_layout.add_widget(calendar_day_popup_layout_bottom)
        calendar_popup = Popup(title=f"{self.button_day.strftime('%A')} the {instance.text}th", content=calendar_day_popup_layout)
        calendar_popup.open()

    def calendar_popup_add_on_press(self, instance):
        """Allows the user to add addicitonal tasks on the second page, also allows you to add tasks that arnt in this week"""
        if self.calendar_day_tasks.text == '':
            self.calendar_day_tasks.text = f'{self.calendar_day_tasks.text}• {self.calendar_text_input.text}'
        else:
            self.calendar_day_tasks.text = f'{self.calendar_day_tasks.text}\n• {self.calendar_text_input.text}'
        if self.button_day.toordinal() >= self.today.toordinal() and self.button_day.toordinal() - 7 <= self.today.toordinal():
            self.storage.put(self.button_day.isoformat(), tasks=self.calendar_day_tasks.text)
        self.refresh()
    
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
        if self.today.weekday() == sum(instance.ids.values()):
            day = date.fromordinal(self.today.toordinal())
        elif self.today.weekday() > sum(instance.ids.values()):
            day = date.fromordinal(self.today.toordinal() + (7 - abs(sum(instance.ids.values()) - self.today.weekday())))
        else:
            day = date.fromordinal(self.today.toordinal() + (sum(instance.ids.values()) - self.today.weekday()))
        try:
            if list(self.storage.get(day.isoformat()).values())[0] != '':
                self.storage.put(day.isoformat(), text = f"{list(self.storage.get(day.isoformat()).values())[0]}\n• {self.main_text_input.text}")
            else:
                self.storage.put(day.isoformat(), text = f"• {self.main_text_input.text}")
        except KeyError:
            self.storage.put(day.isoformat(), text = f"• {self.main_text_input.text}")
        self.refresh()
        self.add_popup.dismiss()
    
    # when the remove button is pressed a popup window will show all o fhte days of the week so the user
    # can choose a day to remove a task from
    # The popup buttons are given a ids attribute (0-6) baced on the day of the week
    def on_remove_button_press(self, instance):
        """When the remove button is pressed then it will bring up a popup window with buttons to choose 
        witch day of the week you want a task to be removed from"""
        remove_popup_layout = BoxLayout(orientation="vertical")
        self.remove_popup = Popup(title='What day would you like to remove a task from', content=remove_popup_layout)
        for i in range(7):
            remove_popup_buttons = Button(text=self.days_of_the_week_typed_out[i])
            current_day = date(self.today.year, self.today.month, self.today.day + i - self.today.weekday() + 7 if self.today.day + i - self.today.weekday() != self.today.day else self.today.day)
            remove_popup_buttons.ids = {current_day.isoformat():self.list_of_tasks[i]}
            remove_popup_buttons.bind(on_press=self.remove_task_button_on_press)
            remove_popup_buttons.bind(on_press=self.remove_popup.dismiss)
            remove_popup_layout.add_widget(remove_popup_buttons)
        self.remove_popup.open()

    # when the remove task button is pressed the text inside of the label with the name of the week that 
    # is the same as the button will be removed
    def remove_task_button_on_press(self, instance):
        """When the task button from the remove popup is pressed then the task from that day of the week 
        will be removed"""
        remove_tasks_popup_layout = BoxLayout(orientation="vertical")
        try:
            for i in list(self.storage.get(list(instance.ids.keys())[0]).values())[0].splitlines():
                remove_task_popup_button = Button(text=i)
                remove_task_popup_button.ids = {list(instance.ids.keys())[0]:i}
                remove_task_popup_button.bind(on_press=self.remove_task_popup_popup)
                remove_tasks_popup_layout.add_widget(remove_task_popup_button)
        except KeyError:
            print('Couldn\'t find key in storage : remove_task_button_on_press')
        self.remove_popup_popup = Popup(title='What task from this day would you like to remove', content=remove_tasks_popup_layout)
        self.remove_popup_popup.open()

    def remove_task_popup_popup(self, instance):
        before_string = list(self.storage.get(list(instance.ids.keys())[0]).values())[0]
        tasks = before_string.splitlines()
        tasks.remove(instance.text)
        after_string = '\n'.join(tasks)
        self.storage.delete(list(instance.ids.keys())[0])
        self.storage.put(list(instance.ids.keys())[0], text=after_string)

        button_day = date.fromisoformat(list(instance.ids.keys())[0])
        num = (((-((button_day.toordinal() + 2)- self.today.toordinal()) * 2) + 12) + (self.today.weekday() * 2)) % 14
        self.refresh()

        self.remove_popup_popup.dismiss()

    def on_move_button_press(self, instance):
        move_popup_layout = BoxLayout(orientation="vertical")
        for i in range(7):
            move_popup_buttons = Button(text=self.days_of_the_week_typed_out[i])
            if i < self.today.weekday():
                day = self.today.day + i - self.today.weekday() + 7
            elif i > self.today.weekday():
                day = self.today.day + i - self.today.weekday()
            else:
                day = self.today.day
            current_day = date(self.today.year, self.today.month, day)
            move_popup_buttons.ids = {current_day.isoformat():i}
            move_popup_buttons.bind(on_press=self.move_task_button_on_press)
            move_popup_layout.add_widget(move_popup_buttons)
        self.move_popup = Popup(title='What day do you want to move a task from?', content=move_popup_layout)
        self.move_popup.open()

    def move_task_button_on_press(self, instance):
        move_tasks_popup_layout = BoxLayout(orientation="vertical")
        try:
            for i in list(self.storage.get(list(instance.ids.keys())[0]).values())[0].splitlines():
                move_task_popup_button = Button(text=i)
                move_task_popup_button.ids = {list(instance.ids.keys())[0]:i}
                move_task_popup_button.bind(on_press=self.move_task_popup_popup)
                move_tasks_popup_layout.add_widget(move_task_popup_button)
        except KeyError:
            print('Key Not found: move_task_button_on_press method')
        self.move_task_list = Popup(title='What task from this day would you like to move?', content=move_tasks_popup_layout)
        self.move_task_list.open()
        self.move_popup.dismiss()

    def move_task_popup_popup(self, instance):
        move_popup_popup_layout = BoxLayout(orientation="vertical")
        for i in range(7):
            move_popup_buttons = Button(text=self.days_of_the_week_typed_out[i])
            if i < self.today.weekday():
                button_day = date(self.today.year, self.today.month, self.today.day + i - self.today.weekday() + 7)
            else:
                button_day = date(self.today.year, self.today.month, self.today.day + i - self.today.weekday())
            num = date.fromordinal(button_day.toordinal()).isoformat()
            move_popup_buttons.ids = {instance.text:num}
            move_popup_buttons.bind(on_press=self.move_task_function)
            move_popup_popup_layout.add_widget(move_popup_buttons)

        before_string = list(self.storage.get(list(instance.ids.keys())[0]).values())[0]
        tasks = before_string.splitlines()
        tasks.remove(instance.text)
        after_string = '\n'.join(tasks)
        self.storage.delete(list(instance.ids.keys())[0])
        self.storage.put(list(instance.ids.keys())[0], text=after_string)

        button_day = date.fromisoformat(list(instance.ids.keys())[0])
        num = (((-((button_day.toordinal() + 2)- self.today.toordinal()) * 2) + 12) + (self.today.weekday() * 2)) % 14
        self.refresh()

        self.move_popup_popup = Popup(title='What day do you want to move this task too?', content=move_popup_popup_layout)
        self.move_popup_popup.open()
        self.move_task_list.dismiss()

    def move_task_function(self, instance):
        try:
            if self.storage.get(list(instance.ids.values())[0]) != '':
                self.storage.put(list(instance.ids.values())[0], text = f"{list(self.storage.get(list(instance.ids.values())[0]).values())[0]}\n{list(instance.ids.keys())[0]}")
            else:
                self.storage.put(list(instance.ids.values())[0], text = f"{list(instance.ids.keys())[0]}")
        except KeyError:
            self.storage.put(list(instance.ids.values())[0], text = f"{list(instance.ids.keys())[0]}")
        self.refresh()
        self.move_popup_popup.dismiss()

    def refresh(self):
        for i in range(7):
            num = ((-(i * 2) + 12) + (self.today.weekday() * 2)) % 14
            inverse_num = int((12 - num) / 2)
            try:
                # print(self.top_half_layout.__getattribute__('children')[num].text, ':', list(self.storage.get(date.fromordinal(self.today.toordinal() + inverse_num).isoformat()).values())[0], ':', num, ':', inverse_num)
                # print(self.top_half_layout.__getattribute__('children')[num - 1].text, ':', date.fromordinal(self.today.toordinal() + inverse_num).isoformat())
                # print('-' * 20)
                if self.top_half_layout.__getattribute__('children')[num].text != list(self.storage.get(date.fromordinal(self.today.toordinal() + inverse_num).isoformat()).values())[0]:
                    self.top_half_layout.__getattribute__('children')[num].text = list(self.storage.get(date.fromordinal(self.today.toordinal() + inverse_num).isoformat()).values())[0]
            except KeyError:
                pass
                # print('No Key for this day : refresh method :', date.fromordinal(self.today.toordinal() + inverse_num))
if __name__ == "__main__":
    app = OrganizationApp()
    app.run()