from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dropdown import MDDropdownMenu
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.metrics import dp
from datetime import date, datetime
from calendar import monthcalendar, month_name

class CalendarTab(MDBoxLayout, MDTabsBase):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.selected_date = parent.selected_date
        self.text = "CALENDAR"
        self.title = "Calendar"
        self.orientation = 'vertical'
        self.add_calendar_grid()
    
    def add_calendar_grid(self):
        self.clear_widgets()
        
        # Navigation buttons
        nav_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5),
            padding=[dp(5), 0]
        )
        prev_month_btn = MDIconButton(
            icon="chevron-left",
            on_release=lambda x: self.change_month(-1)
        )
        next_month_btn = MDIconButton(
            icon="chevron-right",
            on_release=lambda x: self.change_month(1)
        )
        nav_layout.add_widget(prev_month_btn)
        nav_layout.add_widget(MDLabel(
            text=self.selected_date.strftime("%B %Y"),
            halign="center"
        ))
        nav_layout.add_widget(next_month_btn)
        self.add_widget(nav_layout)
        
        self.calendar_grid = MDGridLayout(
            cols=7,
            spacing=dp(5),
            padding=[dp(5), dp(5)],
            size_hint_y=None,
            height=dp(300)
        )
        days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for day in days_of_week:
            self.calendar_grid.add_widget(MDLabel(text=day, halign="center"))
        
        for week in monthcalendar(self.selected_date.year, self.selected_date.month):
            for day in week:
                if day == 0:
                    self.calendar_grid.add_widget(MDLabel(text="", halign="center"))
                else:
                    self.calendar_grid.add_widget(MDFlatButton(text=str(day), on_release=self.on_day_select))
        
        self.add_widget(self.calendar_grid)
    
    def change_month(self, delta):
        month = self.selected_date.month + delta
        year = self.selected_date.year
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1
        self.selected_date = self.selected_date.replace(year=year, month=month)
        self.add_calendar_grid()
    
    def on_day_select(self, instance):
        day = int(instance.text)
        self.selected_date = self.selected_date.replace(day=day)
        self.parent.selected_date = self.selected_date
        self.parent.date_label.text = self.selected_date.strftime("%B %d, %Y")

class YearTab(MDBoxLayout, MDTabsBase):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.selected_date = parent.selected_date
        self.text = "YEAR"
        self.title = "Year"
        self.orientation = 'vertical'
        self.add_year_grid()
    
    def add_year_grid(self):
        self.clear_widgets()
        
        self.year_grid = MDGridLayout(
            cols=3,
            spacing=dp(5),
            padding=[dp(5), dp(5)],
            size_hint_y=None,
            height=dp(300)
        )
        current_year = self.selected_date.year
        for year in range(current_year - 10, current_year + 11):
            self.year_grid.add_widget(MDFlatButton(text=str(year), on_release=self.on_year_select))
        
        self.add_widget(self.year_grid)
    
    def on_year_select(self, instance):
        year = int(instance.text)
        self.selected_date = self.selected_date.replace(year=year)
        self.parent.selected_date = self.selected_date
        self.parent.date_label.text = self.selected_date.strftime("%B %d, %Y")
        self.show_month_dropdown()
    
    def show_month_dropdown(self):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": month_name[i],
                "on_release": lambda x=month_name[i]: self.on_month_select(x)
            } for i in range(1, 13)
        ]
        self.month_menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            width_mult=4
        )
        self.month_menu.open()
    
    def on_month_select(self, month_name):
        month = list(month_name).index(month_name) + 1
        self.selected_date = self.selected_date.replace(month=month)
        self.parent.selected_date = self.selected_date
        self.parent.date_label.text = self.selected_date.strftime("%B %d, %Y")
        self.month_menu.dismiss()
