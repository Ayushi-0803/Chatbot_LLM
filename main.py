import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from PIL import Image

load_dotenv()

st.set_page_config(
    page_title="Chat with Gemini Pro",
    page_icon="🧠",
    layout="centered",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')
vision_model = gen_ai.GenerativeModel('gemini-pro-vision')


def translate_role_for_streamlit(user_role):
    if user_role == 'model':
        return 'assistant'
    else:
        return user_role


if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

st.title("Gemini Pro - Chatbot")

# Add image upload functionality
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
image_prompt = st.text_input("Enter a prompt for the image (optional)")

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Process Image"):
        with st.spinner("Processing image..."):
            if image_prompt:
                response = vision_model.generate_content([image_prompt, image])
            else:
                response = vision_model.generate_content(image)

            st.session_state.chat_session.history.append(
                gen_ai.types.ContentResponse(parts=[gen_ai.types.Content(role="user", parts=["Uploaded an image"])]))
            st.session_state.chat_session.history.append(
                gen_ai.types.ContentResponse(parts=[gen_ai.types.Content(role="model", parts=[response.text])]))

# Display chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Text input for chat
user_prompt = st.chat_input("Ask Gemini Pro")
if user_prompt:
    st.chat_message("user").markdown(user_prompt)

    # Send user's message to Gemini Pro to get response
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Display Gemini Pro's Response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)