import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import re
import cv2
import sqlite3
from PIL import Image
from streamlit_option_menu import option_menu

def extract(uploaded_file):
    reader=easyocr.Reader(lang_list=['en'],gpu=False)
    if uploaded_file is not None:
        img = cv2.imdecode(np.fromstring(uploaded_file.read(),np.uint8),1)
        result_1 = reader.readtext(img,detail=0,paragraph=True)
        result_2 = reader.readtext(img,detail=0,paragraph=False)
        name = result_2[0]
        des = result_2[1]
        mob = []
        for i in result_2:
            if re.findall(r'\d+-\d+-\d+',i):
                mob.append(i)
        for i in result_2:
            if re.findall(r'[a-zA-Z]+@[a-zA-Z0-9]+.[a-zA-Z]+',i):
                mail = i
                break
            else:
                mail = 'Not found'
        for i in result_2:
            if re.findall(r'[wW]+.[a-zA-Z0-9]+.[a-zA-Z]+',i):
                web = i
                break
            else:
                web = 'Not found'
        for i in result_1:
            if len(i) > 30:
                add = i
        org = result_1[-1]
        if len(mob) == 1:
            mob1=mob[0]
            mob2 = 'Not Available'
        elif len(mob) == 2:
            mob1 = mob[0]
            mob2 = mob[1]


        info = {'name':name, 'designation':des,'primary_contact':mob1,'secondary_contact':mob2,'webpage':web,'email_id':mail,
                'address':add,'organization':org}
        res= pd.DataFrame(info,index=['Details'])
        res['name'] = res['name'].str.title()
        res['designation'] = res['designation'].str.title()
        res['organization'] = res['organization'].str.title()
        return res
def push_data(df):
    conn = sqlite3.connect('business_cards.db')
    query = '''CREATE TABLE IF NOT EXISTS business_card (
               name TEXT,
               designation TEXT,
               primary_contact TEXT,
               secondary_contact TEXT,
               webpage TEXT,
               email_id TEXT,
               address TEXT,
               organization TEXT
               )'''
    conn.execute(query)
    df.to_sql('business_card', conn, if_exists='append', index=False)
    conn.close()
    #st.success('Business card information successfully pushed to Database', icon="✅")
def view():
    conn = sqlite3.connect('business_cards.db')
    query = 'SELECT * FROM business_card'
    result = conn.execute(query)
    df = pd.DataFrame(result, columns=['name','designation','primary_contact','secondary_contact','webpage','email_id','address','organization'])
    st.write(df)

def update_data():
  conn = sqlite3.connect('business_cards.db')
  mycursor = conn.cursor()

  query = "SELECT name FROM business_card"
  mycursor.execute(query)
  result = mycursor.fetchall()
  business_cards = [row[0] for row in result]
  selected_card_name = st.selectbox("Select a business card to update", business_cards)

  # Get the current information for the selected business card
  mycursor.execute("SELECT * FROM business_card WHERE name=?", (selected_card_name,))
  result = mycursor.fetchone()

  # Display the current information for the selected business card
  st.write("Name :", result[0] )
  st.write("Designation :", result[1])
  st.write("Primary Contact :", result[2])
  st.write("Secondary Contact :", result[3])
  st.write("Webpage :", result[4])
  st.write("Email :", result[5])
  st.write("Address :", result[6])
  st.write("Organization :", result[7])

  st.write('Enter the details need to be updated')
  # Get new information for the business card
  name = st.text_input("Name", result[0])
  designation = st.text_input("Designation", result[1])
  primary_contact = st.text_input("Primary Contact", result[2])
  secondary_contact = st.text_input("Secondary Contact", result[3])
  webpage = st.text_input("Webpage", result[4])
  email_id = st.text_input("Email", result[5])
  address = st.text_input("Address", result[6])
  organization = st.text_input("Organization", result[7])

  # Create a button to update the business card
  if st.button("Update Business Card"):
      mycursor.execute("UPDATE business_card SET name=?, designation=?, primary_contact=?, "
       "secondary_contact=?, webpage=?, email_id=?, address=?, organization=?"
       "WHERE name=?", (name,designation,primary_contact,secondary_contact,webpage,email_id,address,organization,selected_card_name))
      st.write('Updated')
      conn.commit()
      st.success("Business card information updated in database.")


def download():
  conn = sqlite3.connect('business_cards.db')
  mycursor = conn.cursor()

  query = "SELECT * FROM business_card"
  mycursor.execute(query)
  result = mycursor.fetchall()
  df = pd.DataFrame(result)
  return df


if __name__ =='__main__':
  st.set_page_config(layout="wide")
  col1, col2, col3 = st.columns([1, 8, 1])
  with col2:
    #st.title(':#69D6D0[Extracting Business Card Data with OCR]')
    new_title = '<p style="font-family:sans-serif; color:#69D6D0; font-size: 42px;">Extracting Business Card Data with OCR</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.write('')
    st.write('')
    selected = option_menu(None, ["Home", "Upload & Extract", "view", "Update_data","Download"],
                           icons=['house', "database-fill-add", "eye", 'database-fill-up', 'database-fill-down'],
                           menu_icon="cast", default_index=0, orientation="horizontal",
                           styles={
                               "icon": {"color": "white", "font-size": "25px"},
                               "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px",
                                            "--hover-color": "#69D6D0"},
                           "nav-link-selected": {"background-color": "#69D6D0"}}
                           )

    if selected == 'Home':
      new = '<p style="font-family:sans-serif; color:#69D6D0; font-size: 38px;">OCR</p>'
      st.markdown(new, unsafe_allow_html=True)
      st.write('')
      st.write('OCR is a technology that enables you to convert different types of documents, such as scanned paper documents, PDF files, or images captured by a digital camera into editable and searchable data.')
      st.write('')
      new1 = '<p style="font-family:sans-serif; color:#69D6D0; font-size: 35px;">EasyOCR</p>'
      st.markdown(new1, unsafe_allow_html=True)
      st.write('EasyOCR is actually a python package that holds PyTorch as a backend handler. It detects the text from images but in my reference, while using it I found that it is the most straightforward way to detect text from images also when high end deep learning library(PyTorch) is supporting it in the backend which makes it accuracy more credible. EasyOCR supports 42+ languages for detection purposes.')
      col1, col2, col3 = st.columns([1,4,1])
      with col2:
          st.write('')
          image = Image.open('easyocr_framework.jpeg')
          st.image(image, caption= 'Source : Github')

      name = '<p style="font-family:sans-serif; color:#69D6D0; font-size: 35px;">About & Contact</p>'
      st.markdown(name, unsafe_allow_html=True)
      st.write('I am Rakesh S L, a data science enthusiast')
      st.write('Please reach out me @')
      st.write('Phone number : +91-9035584074')
      st.write('Email id : rakeshslrocky@gmail.com')
      st.write("##")
      st.write('Follow me on')
      Facebook = "https://www.facebook.com/rakesh.slrocky/"
      LinkedIn = "https://www.linkedin.com/in/rakesh-sl-0a5a4b123/"
      Instagram = "https://www.instagram.com/rocky.slr/"
      Github = "https://github.com/RakeshSLRocky"

      col4, col5, col6, col7 = st.columns([0.04, 0.04, 0.04, 0.16])
      with col4:
          if st.button('Github'):
              webbrowser.open_new_tab(Github)
      with col5:
          if st.button('LinkedIn'):
              webbrowser.open_new_tab(LinkedIn)

      with col6:
          if st.button('Facebook'):
              webbrowser.open_new_tab(Facebook)
      with col7:
          if st.button('Instagram'):
              webbrowser.open_new_tab(Instagram)

    if selected == "Upload & Extract":
      uploaded_file = st.file_uploader("Upload the business card here to extact and push data to database...\n", type=['png', 'jpeg', 'jpg'])
      if uploaded_file is not None:
        df = extract(uploaded_file)
        push_data(df)
        col1, col2, col3 =st.columns([1,3,1])
        with col2:
          image = Image.open(uploaded_file)
          st.image(image, use_column_width='always')
          st.success('Business card information successfully pushed to Database', icon="✅")
        st.table(data=df)
    
    if selected == "view":
      view()

    if selected == "Update_data":
      update_data()

    if selected == "Download":
      down1 = download()
      down1.reset_index(drop=True, inplace=True)
      st.table(down1)
      csv_2 = down1.to_csv()
      st.download_button(label="Download data as CSV", data=csv_2,
                               file_name='business_card_info.csv', mime='text/csv')



