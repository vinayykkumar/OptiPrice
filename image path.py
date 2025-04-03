# Function to Set Background Image
def set_background(local_image_path):
    with open(local_image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url("data:image/png;base64,{base64_str}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set Background Image (Replace with your image file)
set_background(r"C:\Users\THRINADH\OneDrive\Desktop\infosys\streamlit\background.png")