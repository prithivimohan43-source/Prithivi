import streamlit as st
import requests
import os
from dotenv import load_dotenv
from PIL import Image

# -------------------------------
# Load Environment Variables
# -------------------------------
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    st.error("❌ Hugging Face API key not found. Add HF_API_KEY to your .env file.")
    st.stop()

MODEL_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="StyleSense",
    page_icon="👗",
    layout="wide"
)

# -------------------------------
# Custom CSS Styling
# -------------------------------
st.markdown("""
<style>
.main {background-color: #f9f5f0;}
h1 {color: #3a3a3a;}
.stButton>button {
    background-color: #000;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LLM FUNCTION (FIXED)
# -------------------------------
def generate_response(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 400,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(MODEL_URL, headers=HEADERS, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[0].get("generated_text", "No response generated.")
            else:
                return str(data)
        else:
            return f"❌ API Error {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return "⏳ Request timed out. Try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# -------------------------------
# Session State Initialization
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = []

if "wishlist" not in st.session_state:
    st.session_state.wishlist = []

# -------------------------------
# Sidebar - User Profile
# -------------------------------
st.sidebar.title("👤 Your Style Profile")

name = st.sidebar.text_input("Name")
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Non-binary"])
body_type = st.sidebar.selectbox("Body Type", ["Slim", "Athletic", "Curvy", "Plus Size"])
skin_tone = st.sidebar.selectbox("Skin Tone", ["Fair", "Medium", "Dark"])
preferred_style = st.sidebar.multiselect(
    "Preferred Styles",
    ["Casual", "Formal", "Streetwear", "Minimal", "Bohemian", "Luxury", "Sporty"]
)
weather = st.sidebar.selectbox("Current Weather", ["Sunny", "Rainy", "Winter", "Humid", "Windy"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Color Palette Suggestion")

if st.sidebar.button("Suggest Colors"):
    if not preferred_style:
        st.sidebar.warning("Select at least one preferred style.")
    else:
        color_prompt = f"""
        Suggest a modern color palette (with HEX codes) 
        for a {skin_tone} skin tone person 
        who prefers {preferred_style} fashion style.
        """
        st.sidebar.write(generate_response(color_prompt))

# -------------------------------
# Main Title
# -------------------------------
st.title("👗 StyleSense")
st.subheader("Your AI-Powered Personal Fashion Stylist")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✨ Outfit Generator",
    "💬 AI Stylist Chat",
    "📷 Upload Outfit",
    "👚 Wardrobe",
    "❤️ Wishlist"
])

# -------------------------------
# TAB 1: Outfit Generator
# -------------------------------
with tab1:
    occasion = st.selectbox(
        "Select Occasion",
        ["Party", "Office", "Date", "Wedding", "Travel", "Gym", "Casual Hangout"]
    )

    if st.button("Generate Outfit Recommendation"):
        if not name:
            st.warning("Please enter your name in sidebar.")
        else:
            prompt = f"""
            Act as a professional fashion stylist.
            Create a detailed outfit recommendation for:

            Name: {name}
            Gender: {gender}
            Body Type: {body_type}
            Skin Tone: {skin_tone}
            Preferred Style: {preferred_style}
            Weather: {weather}
            Occasion: {occasion}

            Include:
            - Clothing items
            - Footwear
            - Accessories
            - Layering advice
            - Styling tips
            """

            st.write(generate_response(prompt))

# -------------------------------
# TAB 2: AI Stylist Chat
# -------------------------------
with tab2:
    user_input = st.text_input("Ask your stylist anything...")

    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(("You", user_input))

            prompt = f"""
            You are an AI fashion stylist.

            User Profile:
            Gender: {gender}
            Body Type: {body_type}
            Skin Tone: {skin_tone}
            Style: {preferred_style}

            Question: {user_input}
            """

            ai_response = generate_response(prompt)
            st.session_state.chat_history.append(("StyleSense AI", ai_response))

    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {message}")

# -------------------------------
# TAB 3: Upload Outfit
# -------------------------------
with tab3:
    uploaded_file = st.file_uploader("Upload your outfit image", type=["jpg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Outfit", use_column_width=True)

        if st.button("Analyze Outfit"):
            st.info("Note: This model cannot see images. Add a description below.")

            description = st.text_area("Describe your outfit:")

            if description:
                analysis_prompt = f"""
                Analyze this outfit description:

                {description}

                Suggest:
                - Improvements
                - Matching accessories
                - Better color combinations
                - Occasion suitability
                """
                st.write(generate_response(analysis_prompt))

# -------------------------------
# TAB 4: Wardrobe
# -------------------------------
with tab4:
    new_item = st.text_input("Add Clothing Item")

    if st.button("Add to Wardrobe"):
        if new_item.strip():
            st.session_state.wardrobe.append(new_item.strip())
            st.success("Added successfully!")

    if st.session_state.wardrobe:
        st.write("### Your Wardrobe")
        for item in st.session_state.wardrobe:
            st.write("•", item)

# -------------------------------
# TAB 5: Wishlist
# -------------------------------
with tab5:
    wish_item = st.text_input("Add to Wishlist")

    if st.button("Add Item"):
        if wish_item.strip():
            st.session_state.wishlist.append(wish_item.strip())
            st.success("Added to wishlist!")

    if st.session_state.wishlist:
        st.write("### Wishlist")
        for item in st.session_state.wishlist:
            st.write("❤️", item)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("© 2026 StyleSense | Powered by Llama 3.1 8B")