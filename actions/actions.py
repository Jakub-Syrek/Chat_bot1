import json
import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


import json
import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionListMenuItems(Action):

    def name(self) -> Text:
        return "action_list_menu_items"

    def ReadMenuJson(self):
        f = open('restaurant_info/menu.json')

        menu = json.load(f)
        menu_items = menu.get('items')

        display = 'Currently we have following items on the menu... :\n\n'

        for item in menu_items:
            meal = item.get('name')
            price = item.get('price')
            display = display + f'{meal} {price}\n'
        return display

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        display = self.ReadMenuJson()
        dispatcher.utter_message(text=display)

        return []




class ActionAskIfOpen(Action):

    def name(self) -> Text:
        return "action_check_open"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        day_of_week = ''
        hour = ''

        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'day_of_week':
                day_of_week = blob['value']

            if blob['entity'] == 'hour':
                hour = blob['value']

        f = open('restaurant_info/opening_hours.json')

        opened = json.load(f)

        opening_time_items = opened.get('items')

        hours = opening_time_items.get(day_of_week.capitalize())

        if hours is None:
            dispatcher.utter_message(text=f"Please rephrase {day_of_week}")
            return []

        if hour == '':
            dispatcher.utter_message(
                text=f"Bar is open from {hours.get('open')} to {hours.get('close')} on {day_of_week}"
            )
            return []

        if (int(hour) < 0) or (int(hour) > 24):
            dispatcher.utter_message(text=f"Please use numbers in range: 1-24")
            return []

        opening_hour = hours.get('open')
        close_hour = hours.get('close')

        if (int(hour) > int(opening_hour)) and (int(hour) < int(close_hour)):
            dispatcher.utter_message(text=f"Yes, bar is opened at {hour} on {day_of_week}")

        else:
            dispatcher.utter_message(text=f"No, bar won't be opened at {hour} on {day_of_week}")

        return []

class ActionShowOrder(Action):

    def name(self) -> Text:
        return "action_show_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        meals_string = tracker.get_slot('meals')
        meals = meals_string.split(',')

        with open('restaurant_info/menu.json') as menu_file:
            menu = json.load(menu_file)

        menu_items = menu.get('items')
        menu_meals = []
        approved_meals = []
        failed_meals = []

        for item in menu_items:
            menu_meals.append(item.get('name'))

        for meal in meals:
            contains_menu_meal = 0
            for menu_meal in menu_meals:
                if menu_meal in meal:
                    contains_menu_meal = 1
            if contains_menu_meal == 0:
                failed_meals.append(meal)
            else:
                approved_meals.append(meal)

        failed_meals_table = []
        for failed_meal in failed_meals:
            failed_meal_without_spaces = failed_meal.lstrip()
            failed_meals_table.append(failed_meal_without_spaces)
        failed_meals_for_user = ", "
        failed_meals_for_user = failed_meals_for_user.join(failed_meals_table)
        if failed_meals:
            dispatcher.utter_message(text=f"Sorry, but those meals aren't in the menu: {failed_meals_for_user}")
            return []

        general_cost = 0
        general_time = 0
        for meal in approved_meals:

            search_for_int = re.search(r'\d+', meal)

            if search_for_int is None:
                count = 1
            else:
                count = int(search_for_int.group())

            selected_meal = ''

            for menu_meal in menu_meals:
                if menu_meal in meal:
                    selected_meal = menu_meal
                    break


            extra_info_with_number = meal.replace(selected_meal, '')
            extra_info = ''.join([i for i in extra_info_with_number if not i.isdigit()]).lstrip()

            product_price = 0
            product_time = 0
            for item in menu_items:
                if item.get('name') is selected_meal:
                    product_price = item.get('price')
                    product_time = item.get('preparation_time')
                    break

            general_cost = general_cost + product_price * count
            general_time = general_time + product_time * count
            meal_info = f'{count}x {selected_meal}, Price: {product_price}x{count}={product_price * count}, Time for preparation: {product_time}x{count}={product_time * count}'

            if extra_info:
                meal_info_with_extra = meal_info + f' Extra info: {extra_info}'
            else:
                meal_info_with_extra = meal_info

            dispatcher.utter_message(text=meal_info_with_extra)

        dispatcher.utter_message(
            text=f'Total cost will be: {general_cost}, and meal will be ready in approximately: {general_time} hours')
        return []


class ActionSummarizeOrderDelivery(Action):

    def name(self) -> Text:
        return "action_summarize_order_delivery"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = tracker.get_slot('address')
        dispatcher.utter_message(text=f"Thank you, your order will be delivered to {address}")

        return []