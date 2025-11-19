import google.generativeai as genai
import gradio as gr
import sys

# --- 1. SETUP API KEY ---
# TODO: PASTE YOUR GEMINI API KEY INSIDE THE QUOTES BELOW
API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"

if API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE" or not API_KEY:
    print(" ERROR: API Key is missing.")
    print("Please open app.py and paste your Google Gemini API Key into the API_KEY variable at the top.")
    sys.exit(1)

try:
    genai.configure(api_key=API_KEY)
    
    # --- 2. CONFIGURE MODEL ---
    # We use 'gemini-flash-latest' as it is free and fast
    generation_config = {
      "temperature": 0.8, 
      "top_p": 1, 
      "top_k": 1, 
      "max_output_tokens": 10000, # Large limit for long stories
    }
    
    safety_settings = [
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    model = genai.GenerativeModel(model_name="gemini-flash-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

except Exception as e:
    print(f"Error configuring Gemini: {e}")
    sys.exit(1)


# --- 3. SYSTEM PROMPT ---
SYSTEM_PROMPT = """
आप एक 'कथा वाचक' (Katha Vachak) हैं जो बच्चों के लिए कहानियाँ सुनाते हैं। 
आपका काम उपयोगकर्ता के प्रॉम्प्ट के आधार पर एक रचनात्मक, सरल और मनोरंजक हिंदी कहानी (katha) बनाना है।

आपकी कहानियों में ये 4 चीज़ें ज़रूर होनी चाहिए:
1.  **लोक कथा (Folk Theme):** कहानी में भारतीय लोक कथाओं के तत्व होने चाहिए (जैसे बोलते हुए जानवर, बुद्धिमान ग्रामीण, राजा-रानी, या जादुई घटनाएं)।
2.  **कहावत/मुहावरा (Proverb/Idiom):** कहानी के प्रवाह में कम से कम एक प्रासंगिक हिंदी कहावत या मुहावरा (जैसे 'जैसा बोओगे वैसा काटोगे' या 'एकता में बल है') का प्रयोग करें और उसे **बोल्ड** करें।
3.  **नैतिक शिक्षा (Moral):** कहानी के अंत में एक स्पष्ट 'शिक्षा' (Moral) ज़रूर लिखें।
4.  **सरल भाषा (Simple Language):** भाषा सरल हिंदी में होनी चाहिए, जो बच्चों को आसानी से समझ आ सके।

प्रॉम्प्ट किसी भी भाषा में हो सकता है, लेकिन आपकी कहानी हमेशा हिंदी में ही होगी।
"""

# --- 4. GENERATION LOGIC ---
def generate_story(user_prompt: str):
    """
    Generates a Hindi story and its English translation.
    """
    if not user_prompt:
        return "Please enter a topic.", "कृपया कोई विषय लिखें।"

    # 1. Generate Hindi Story
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\n---\n\nUSER PROMPT: \"{user_prompt}\"\n\nSTORY (in Hindi):"
        convo = model.start_chat(history=[])
        convo.send_message(full_prompt)
        hindi_story = convo.last.text
    except Exception as e:
        return f"Error generating story: {str(e)}", "Error."

    # 2. Generate English Translation
    try:
        translate_prompt = f"Translate the following Hindi story into simple English for a child to understand:\n\n{hindi_story}"
        convo.send_message(translate_prompt) # Continue the same chat context
        english_translation = convo.last.text
    except Exception as e:
        english_translation = f"Error generating translation: {str(e)}"

    return hindi_story, english_translation

# --- 5. USER INTERFACE (GRADIO) ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange", secondary_hue="blue"), title="Hindi Katha Generator") as demo:
    gr.Markdown(
        """
        # 🖋️ Creative Writing Assistant for Hindi (हिंदी कहानी सहायक)
        **AI-Powered Storytelling with Folk Themes and Proverbs**
        
        Enter a simple idea (e.g., "Two friends and a bear"). The AI will generate a culturally rich Hindi story with a moral.
        """
    )
    
    with gr.Row():
        prompt_input = gr.Textbox(
            label="Enter your story idea (अपनी कहानी का विचार लिखें)", 
            placeholder="e.g., 'एक शेर और खरगोश की कहानी' or 'A story about a magical tree'",
            lines=2
        )
    
    generate_btn = gr.Button("कहानी बनाएँ (Generate Story)", variant="primary")
    
    with gr.Row():
        hindi_output = gr.Textbox(
            label="आपकी कहानी (Your Story in Hindi)", 
            lines=25, 
            interactive=False,
            show_copy_button=True
        )
        english_output = gr.Textbox(
            label="English Translation (अंग्रेजी अनुवाद)", 
            lines=25, 
            interactive=False,
            show_copy_button=True
        )

    generate_btn.click(
        fn=generate_story, 
        inputs=[prompt_input], 
        outputs=[hindi_output, english_output]
    )
    
    gr.Examples(
        examples=[
            "एक घमंडी हाथी और एक छोटी चींटी",
            "जादुई नदी की कहानी",
            "A clever fox and a foolish crow",
            "दो दोस्त और एक भालू"
        ],
        inputs=prompt_input
    )

# --- 6. LAUNCH ---
if __name__ == "__main__":
    print("Starting app...")
    demo.launch(share=True)
