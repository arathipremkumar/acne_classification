from typing import Dict
import streamlit as st
import os
from PIL import Image
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import urllib.request
import ssl
import base64
import json
from io import BytesIO


@st.cache_data

def get_static_store() -> Dict:
    """This dictionary is initialized once and can be used to store the files uploaded"""
    return {}

def color_low_confidence(val):
    """
    Takes a scalar and returns a string with
    the css property `'background-color: red'` for
    values that match 'low confidence', and an
    empty string otherwise.
    """
    color = 'red' if val == 'low confidence' else ''
    return f'background-color: {color}'





def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context





def to_predict(result):
    allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.
    
    st.write()
    st.write()
        
    count=0 #Used in progress bar calculation
    corr=0 #corrupt files count
    progress_text = "Image(s) Processing..."
    prog_bar = st.progress(count, text=progress_text)
    

    if result:
        
        image_data_list = []    
        # Loop through the uploaded files and make predictions
        for uploaded_file in result:
            count+=1
            # Load the image from the file
            value = Image.open(uploaded_file)
            try:
                with Image.open(uploaded_file) as img:
                    img.verify()
            except(IOError, SyntaxError):
                corr+=1
                continue


            buffered = BytesIO()
            value.save(buffered, format="JPEG")
            
            image_data = {
                    'filename': uploaded_file.name,
                    'data': base64.b64encode(buffered.getvalue()).decode('utf-8')
                }
            image_data_list.append(image_data)

        # Convert the list of image data to a JSON object
        body = str.encode(json.dumps({'images': image_data_list}))
                     
            
           
        # Display the predictions in a table
    
    url = 'https://image-analytics-xbngf.westus2.inference.ml.azure.com/score'
    # Replace this with the primary/secondary key or AMLToken for the endpoint
    api_key = 'EAx3TR2mIebxacCnZJlBBcWNe0QGzcVR'
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'mobilenet-91-60-70-5' }
    df=pd.DataFrame()
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        # print(result)
        # print(type(result))
        data = json.loads(json.loads(result.decode("utf-8")))
        # print(type(data))
        
        
        # extract the results list from the dictionary
        #results = data["results"]
        # print(results)
        # create a dataframe from the results list
        df = pd.DataFrame(data, columns=["Image_name", "Predicted Severity level","Actual Severity level","Type_of_acne","Status"])
        print(df)
        # print(df.round(3))

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        # print(error.info())
        # print(error.read().decode("utf8", 'ignore'))
    prog_bar.empty() # removes progress bar after loading
    
    
    # df_count=df['predicted_class'].value_counts() #gets freq of each class
    # col=[] #dividing columns for each class card
    # col=st.columns(len(df_count)+1)
    
    # colno=0 #to keep index of column
    # for val,c in df_count.items():
    #     col[colno].metric(label=val,value=c)
    #     colno+=1
    # col[colno].metric(":blue[Total images]",value=count,help="Corrupt images = "+str(corr))
    #AgGrid(df)
    #st.dataframe(df.style.highlight_max(subset=['P1','P2','P3','P4'],axis=1),use_container_width=True)
    # st.dataframe(df.style.background_gradient(cmap="Greens", subset=['CNV','DME','DRUSEN','NORMAL'], axis=1, low=0.5, high=1)    ,use_container_width=True)
    st.dataframe(df)


#static_store = get_static_store()

def first():
    st.markdown("<h1 style='text-align: center; color: #3C6255;'>Acne Severity Detection</h1>",
                unsafe_allow_html=True)
    
    with st.columns(3)[1]:
        st.image(Image.open("acne.jpg").resize((300,200)))
    
    # st.image(Image.open("C:/Users/nikunj.bedia/testing_streamlit/acne/acne.jpg").resize((300,200)))
     
    
    result = st.file_uploader("Upload one or more images.", type=["PNG","JPEG","JPG"],key="real", accept_multiple_files=True)
    #static_store.clear()  # Hack to clear list if the user clears the cache and reloads the page
    #st.info("Upload one or more images.")
    
    if st.button('Submit'):
        to_predict(result)
    
first()

#https://colorhunt.co/palette/3c625561876ea6bb8deae7b1


