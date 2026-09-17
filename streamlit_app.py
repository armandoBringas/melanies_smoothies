# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

import requests 

# Write directly to the app
st.title(f":cup_with_straw: Customize Yout Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

# 1. Capture the customer's name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# 2. Fetch fruit options from Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# 3. Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# 4. Handle submission
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        # Include both ingredients and name_on_order in the INSERT query
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
        
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# New section to display smoothiefroot nutrition information
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response)
