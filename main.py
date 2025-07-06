
import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO

from urllib.parse import quote_plus 



st.set_page_config(page_title="Recommendation",page_icon="::Fire::",layout="wide")
#------------------------------------------------------------------------------------------------------------
st.markdown("<hr style='border-top: 3px solid blue;'>", unsafe_allow_html=True)
#--------------------------------------------
# ----------------------------------------------------------------


if "main_json_file" not in st.session_state:
     st.session_state.main_json_file = None
if "img_btn_clicked" not in st.session_state:
    st.session_state.img_btn_clicked = False
if "img_already_generated" not in st.session_state:
    st.session_state.img_already_generated = False
data_driv_df = pd.read_csv("banner_data.csv")
#Select * from data_deiv_df 
main_top_df = (
    data_driv_df.sort_values(by="Total clicks", ascending=False)
)


d_lef,d_rig = st.columns(2)
with d_lef:
 if st.subheader("Generate Data Driven Banners using AI"):
  st.subheader("Banner Theme")
  if st.button("Generate Tags Based on Previous Data"):
      
      tags_list = []
      tags_list.append(main_top_df["tags"].to_list())
      os.environ["GOOGLE_API_KEY"] = "AIzaSyBRis98QWTre57ghQ4xsHA9FLQzx8ZWODE"
      llm = ChatGoogleGenerativeAI(
                                    model="gemini-2.0-flash",
                                    temperature=0,
                                    max_tokens=None,
                                    timeout=None,
                                    max_retries=2,
                
                                )
      human_messaged_mixture = f"""
    This is the list of tags: {tags_list}

    Based on this, please analyze and generate meaningful structured tags. 

    Return the output strictly in the following format:

    {{
      "Tag Name": [],
      "Tag Property": [],
      "Tag Values": []
    }}

    Make sure the output is a valid JSON object and all arrays are aligned by index and in the Colors tags please give me the colors with percentage. and make sure the tag names has equal no of tags amd tag properties have equal no of properties and tag values has equal no of values like len(tag names) = len(tag properties) - len(tag values)
    """
                            
      prompt_for_tags_mixture = [
                    (
                        "system",
                        """Let's Assume you are the best tags analyzer and tags merger based on the high performance and now you want to give me the best tags out of 3 outperforming banner tags and based on that tags give me the more tags to improve the image and improve user engagement and may include the types like doodling and animated etccmand please give me the 60 tags for it and 60 tags should be very perfect  and the all tag names and tag properties and tag values will be equal"""
                    ),
                    (
                        "human",
                            human_messaged_mixture
                    )
                    ] 
      os.environ["GOOGLE_API_KEY"] = "AIzaSyBRis98QWTre57ghQ4xsHA9FLQzx8ZWODE"
      llm = ChatGoogleGenerativeAI(
                                model="gemini-2.0-flash",
                                temperature=0,
                                max_tokens=None,
                                timeout=None,
                                max_retries=2,
            
                            )
      resp_tag_mixture = llm.invoke(prompt_for_tags_mixture)
      main_tag_content = str(resp_tag_mixture.content)
      find_idx = main_tag_content.find("{")
      find_idx_l = main_tag_content.rfind("}")
      json_dat_for_tag_mix = main_tag_content[find_idx:find_idx_l+1]
    
      if "the_df_json" not in st.session_state:
          st.session_state["the_df_json"] = json_dat_for_tag_mix


# Validate that all lists have the same length
  generated_ban_image = None
    
  theme  = st.text_input("Enter your banner details")
  if theme:
     generated_ban_image = st.button("Generate")
  st.divider()
  st.subheader("Colorize Your Image With Text")
  input_text = st.text_input("Enter your text ")
  text_color_hex = st.color_picker("Pick a text color", "#EDE6D3")
  alignment = st.selectbox("Select Your Alingment",["Top","Middle","Bottom"])
  text_btn = st.button("generate the text image")

  if st.button("Reset"):
      st.session_state.img_btn_clicked = False
      st.session_state.img_already_generated = False
      st.session_state.text_image_generated = False
      st.session_state.v_tags_btn = False

      keys_to_clear = [
          "image_path",
          "json_c",
          "banner_image",
          "main_json_file"
      ]
      
      for key in keys_to_clear:
          if key in st.session_state:
              del st.session_state[key]

with d_rig:
  main_jsoon = None 
  st.subheader("Preview")
  st.text("Based on the Previous Dataset:")
  with st.expander("Expand for Previous Data"):
    st.dataframe(main_top_df.head(3))
  if "the_df_json" in st.session_state:
         main_jsoon = json.loads(st.session_state["the_df_json"])
         tag_names = main_jsoon.get("Tag Name", [])
         tag_properties = main_jsoon.get("Tag Property", [])
         tag_values = main_jsoon.get("Tag Values", [])
  else:
       st.badge("Not Genrated The Tags")
  if main_jsoon:
   if len(tag_names) == len(tag_properties) == len(tag_values):
    main_tag_mixture_df = pd.DataFrame({
        "Tag Name": tag_names,
        "Tag Property": tag_properties,
        "Tag Values": tag_values
    })
 
    with st.expander("Click for Analyzed tags based on previous Outperforming Banners"):
        st.dataframe(main_tag_mixture_df)
   else:
    st.error(
        f""" 
   Please ensure the AI response returns equal-length lists for all fields.
   """
    )
  else:
       st.warning("Not generated")

      
       
  if generated_ban_image:
    
   st.session_state.img_btn_clicked = True
   if st.session_state.img_btn_clicked and not st.session_state.img_already_generated:
    main_json_file = st.session_state.main_json_file
    json_c = None

    human_message = "this is the title and make sure if the people there please render the people completely with accuracy of eyes and legs and hands placements and symmentry and objects logic in placement is also important the eyes will look like relastic  the theme is " + theme

    prompt = [
      (
          "system",
          f"""You are a professional promotional banner designer for financial services.and now ensure the following the only logo prompt . Utilize clean lines and geometric forms to enhance clarity and readability. Ensure the lighting is bright for vibrancy, giving the logo a contemporary feel. The overall mood should convey trust and reliability, appealing to a finance-oriented audience. Reference styles from modern minimalist design to maintain simplicity and effectiveness.these are the tags now based on the tags {st.session_state.the_df_json} create a nice promotional banner prompt with no text included and no logos included in it and the ouput reference is given. and make sure please give me the some space to right top to place logo 
  "Create a luxurious gold loan promotional banner featuring elegant traditional Indian gold jewelry (heavy necklaces, bangles, rings, earrings) artistically displayed on rich burgundy velvet fabric. Professional confident Indian family - well-dressed parents in their 40s wearing modern formal attire, smiling warmly in upscale modern living room with soft natural lighting. Warm golden color palette with deep burgundy, cream and gold accents, high contrast design. Bold premium serif font headline "INSTANT GOLD LOANS" with supporting text "Get Cash in 30 Minutes - Secure & Fast". Modern bank logo positioned in top-right corner, medium size. High contrast bright gold CTA button "APPLY NOW" placed at bottom center. Photorealistic commercial photography style, asymmetrical balanced composition, medium whitespace, soft dramatic shadows, 4K resolution, professional studio lighting quality, sophisticated luxury aesthetic, cultural authenticity, trustworthy corporate branding elements. Don't add any text".so give me the output base on tags and wil pass the main theme what to generate and make sure following the tags and the output(prompt) will look like above refernce make sure give me the symmentrics of peron and clasrit and 4k and include the accuracy will be high of specifc persons face and living things and having  proposition of man and woman and ensure please include the diference between man and woman because it is combining. and make sure don't overlap the two persons and ensure accuracy in persons hand placement on the objects also and some picures are getting like one man has three hands so please mention it and don't show any objects mockups add the fingers also like 5 it is not rendering and man should wear only the shirt atire don't use any sexual images """
      ),
      (
          "human",
          human_message
      )
    ]

    os.environ["GOOGLE_API_KEY"] = "AIzaSyBRis98QWTre57ghQ4xsHA9FLQzx8ZWODE"
    llm = ChatGoogleGenerativeAI(
                                model="gemini-2.0-flash",
                                temperature=0,
                                max_tokens=None,
                                timeout=None,
                                max_retries=2,
            
                            )


    ai_response = llm.invoke(prompt)
            
    json_c = ai_response.content
    st.session_state['json_c'] = json_c
    with st.expander("Click Here to View The Generated Prompt"):
       st.success("Generated The image Prompt")
       st.text_area("Generated Prompt:", json_c, height=200)
    st.divider()
    if 'json_c' in st.session_state:
        randomgen = np.random.randint(1, 100000)
        promptt = st.session_state.get("json_c")
        
        try:
            with st.spinner("Generating image..."):
                resp = requests.get(
                    f"https://nihalgazi-optimflux.hf.space/?prompt={promptt}&width=1280&height=720&seed={randomgen}",
                    timeout=30
                )
                resp.raise_for_status()  # Raises an HTTPError for bad responses
                
                # Check if response contains image data
                if resp.headers.get('content-type', '').startswith('image/'):
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                        tmpfile.write(resp.content)
                        file_name = tmpfile.name
                    
                    # Verify the image can be opened
                    try:
                        test_image = Image.open(file_name)
                        test_image.verify()  # Verify it's a valid image
                        st.session_state.image_path = file_name
                        st.session_state.img_already_generated = True
                    except Exception as img_error:
                        st.error(f"Generated file is not a valid image: {str(img_error)}")
                        if os.path.exists(file_name):
                            os.unlink(file_name)
                else:
                    st.error("API did not return image data. Response content type: " + resp.headers.get('content-type', 'unknown'))
                    st.text("Response content preview:")
                    st.text(resp.text[:500])
                    
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling image generation API: {resp.content}")
        except Exception as e:
            st.error(f"Unexpected error during image generation: {resp.content}")


      
    if "image_path" in st.session_state and st.session_state.image_path:
          if "banner_image" not in st.session_state:
            image = Image.open(st.session_state["image_path"])
            target_size = (1280, 720)
            image = ImageOps.pad(image, target_size, color=(0, 0, 0), centering=(0.5, 0.5))
            st.session_state["banner_image"] = image.copy()
          else:
            image = st.session_state["banner_image"].copy()

          st.image(image, caption="Generated Promotional Banner")
    
  
    


    
    st.divider()

  if text_btn and input_text and text_color_hex and alignment:
      if "image_path" in st.session_state and st.session_state["image_path"]:
            image = Image.open(st.session_state["image_path"])
            main_image = image
            image = ImageOps.pad(image, (1280, 720), color=(0, 0, 0), centering=(0.5, 0.5))
            from PIL import Image, ImageDraw, ImageFont
           
            
            image_editable = ImageDraw.Draw(image)

            text_path = 'Playfair_Display/static/PlayfairDisplay-Bold.ttf'
            img_width,img_height = image.size
            text_ratio = 0.15
            text_size = int(text_ratio * img_height)


            text_font = ImageFont.truetype(text_path,text_size)

            bbox = image_editable.textbbox((0, 0), input_text, font=text_font)

            text_width = bbox[2] - bbox[0] 
            text_height = bbox[3] - bbox[1]

            x = (img_width - text_width) // 2

            if alignment == "Top":
              y = int(0.10 * img_height)  # 5% from top
            elif alignment == "Middle":
              y = (img_height - text_height) // 2
            else:  # "Bottom"
              y = int(img_height - text_height - 0.10 * img_height)  # 5% from bottom



            text_color_rgb = tuple(int(text_color_hex[i:i+2], 16) for i in (1, 3, 5))
      
            image_editable.text((x, y), input_text, text_color_rgb, font=text_font)
            logo_path = "Bajaj_Finserv.png"
            image_width,image_height = image.size
            with open(logo_path,"rb") as file:
               logo = BytesIO(file.read())
            logo_img = Image.open(logo).convert("RGBA")
            aspect_ratio = (logo_img.height / logo_img.width)
            logo_new_width = 150
            logo_new_height = int(logo_new_width * aspect_ratio)
            logo_img = logo_img.resize((logo_new_width,logo_new_height),Image.Resampling.LANCZOS)
            padding_x =20
            padding_y =20
            position = (image_width - logo_img.width - padding_x,padding_y)
            image.paste(logo_img,position,mask= logo_img)
            st.image(main_image,caption="Generated Based On Previous Tags")
            st.image(image,caption="Colorized the Generated Bannner")
            st.session_state.text_image_generated = True
st.markdown("<hr style='border-top: 3px solid green;'>", unsafe_allow_html=True)

