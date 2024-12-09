# Import python packages
import streamlit as st
import requests
import pandas as pd

#from snowflake.snowpark.context import get_active_session
#Connection required for streamlit app
cnx = st.connection("snowflake")
session = cnx.session()

from snowflake.snowpark.functions import col


# Write directly to the app
st.title("Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you'd like in your custom smoothie.
    """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be", name_on_order)


#session = get_active_session()
#my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON')).collect()
my_dataframe = session.table("smoothies.public.fruit_options").select("FRUIT_NAME", "SEARCH_ON")

#Convert snowflake dataframe to a pandas dataframe
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()  # temp, remove as required

#ingredients_list = st.multiselect(
#    "Choose up to 5 ingredients",
#    my_dataframe,
#    max_selection=5
#)

# Extract fruit names from the collected data
#fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]
# Extract fruit names from the Pandas DataFrame
fruit_options = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_options,
    max_selections=5
)


if ingredients_list:
    st.write("You selected:", ingredients_list)
    st.text(ingredients_list)
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        #smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on
        #st.text(smoothiefroot_response.json())

        
        
        st.subheader(fruit_chosen + ' Nutritional Information')
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    
    # Convert the list to a string with a comma and space separator
    # ingredients_string = ", ".join(ingredients_list)

    # Display the string
    #st.write("Your selected ingredients are:", ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', ' """ + name_on_order + """ ')"""

    st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
