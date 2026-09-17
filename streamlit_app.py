# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests 

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 1. Capture the customer's name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# 2. Fetch fruit options from Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

# 3. Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# 4. Process selection and API calls
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Find the SEARCH_ON value corresponding to the chosen fruit name
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Added f-string prefix 'f' to interpolate the search_on value
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on.lower()}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # 5. Handle submission (after ingredients_string is built)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')"""
        
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
