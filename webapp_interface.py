import streamlit as st
import tensorflow as tf
import numpy as np
from keras.models import load_model
from util import set_background
####loging page
#set background
set_background("C:\Doctor-checking-brain-testing-result-with-robotics-on-virtual-interface-on-laboratory-background-innovative-technology-in-science-and-medicine-concept-©-Ipopba.jpg")
#set the title
st.title("Welcome to Cancer Classifier: Empowering Health Through AI")
def creds_entered():
    if st.session_state["user"].strip() == 'Doctor' and st.session_state["passwd"].strip()=='doc@1234':
        st.session_state["authentificated"]=True
    else:
        st.session_state['authentificated']=False
        st.error("Invalid username/Password :face_with_raised_eyebrow:")

def authentificate_user():
    if "authentificated" not in st.session_state:
        st.text_input(label='**Username:**',value='',key="user",on_change=creds_entered)
        st.text_input(label='**Password:**',value='',key="passwd",type="password",on_change=creds_entered)
        return False
    else:
        if st.session_state["authentificated"]:
            return True
        else:
            st.text_input(label='**Username:**',value='',key="user",on_change=creds_entered)
            st.text_input(label='**Password:**',value='',key="passwd",type="password",on_change=creds_entered)
            return False
if authentificate_user():

    #set background
    set_background("C:\istockphoto-1325872227-612x612.jpg")

    #load modele
    model=load_model("C:\CNN_finalmodel.h5")
    #set header
    st.header('Please upload an image to classify!:eyes:☑')
    #upload file
    img=st.file_uploader("", type=["jpeg","jpg","png"])

    #classes
    data_cat=['breast_tumor', 'glioma_brain_tumor', 'meningioma_brain_tumor', 'no_tumor', 'pituitry_brain_tumor', 'skin_tumor']
    img_height=180
    img_width=180
    image_load=tf.keras.utils.load_img(img,color_mode="rgb",target_size=(180,180))
    image_array=tf.keras.utils.array_to_img(image_load)
    image_bat=tf.expand_dims(image_array,0)

    predictions=model.predict(image_bat)
    confidence=np.max(predictions) * 100

    st.image(img,width=500)

    # Display class in bold on one line
    st.markdown("**The class is:** {}".format(data_cat[np.argmax(predictions)]))

    # Display accuracy in bold on the next line with a line break
    st.markdown("**with accuracy of:** {:.2f}%\n".format(confidence))

    st.header('THANKS FOR YOUR INVITATION 😊')