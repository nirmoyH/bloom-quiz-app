from flask import Flask, render_template, request
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
import html
import json

app = Flask(__name__)
genai.configure(api_key="AIzaSyBUWDBj6Ac1o7IAMBDM4Ibe7zeiRG4whTw")  # Replace with your actual API key

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = ""
    embed_url = ""
    questions_data = None
    error_message = ""
    raw_response = ""

    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_id_match = re.search(r"v=([a-zA-Z0-9_-]+)", video_url)
        if video_id_match:
            video_id = video_id_match.group(1)
            embed_url = f"https://www.youtube.com/embed/{video_id}"

            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([entry['text'] for entry in transcript_list])
            except Exception as e:
                error_message = f"🚫 Failed to fetch transcript: {html.escape(str(e))}"
                return render_template("index.html", video_url=video_url, embed_url=embed_url,
                                       questions=None, error=error_message)

            # Generate questions from transcript
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            prompt = f"""
            You are a Bloom's Taxonomy quiz expert.

            Based on the following transcript from a YouTube video, generate 60 multiple-choice questions grouped into 6 Bloom's levels:
            - 10 Remembering
            - 10 Understanding
            - 10 Applying
            - 10 Analyzing
            - 10 Evaluating
            - 10 Creating

            Transcript:
            \"\"\"{transcript_text}\"\"\"

            Each question must have:
            - "question": Question text
            - "options": List of 4 options (a, b, c, d)
            - "answer": Correct option letter (a, b, c, or d)

            Return ONLY valid JSON in this structure:
            {{
              "0": [{{"question": "...", "options": ["A", "B", "C", "D"], "answer": "a"}}],
              ...
              "5": [...]
            }}

            No explanation. No markdown. No comments.
            """

            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            raw_response = raw_text  # Keep for debug output

            # Clean up bad formatting
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()

            raw_text = raw_text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

            # Optional: remove trailing commas
            raw_text = re.sub(r",(\s*[\]}])", r"\1", raw_text)

            try:
                questions_json = json.loads(raw_text)
                questions_data = questions_json
            except Exception as e:
                error_message = f"❌ Failed to parse question JSON: {html.escape(str(e))}"
                return f"""
                <h3>{error_message}</h3>
                <hr>
                <h4>Raw Gemini Response:</h4>
                <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 1rem;">{html.escape(raw_response)}</pre>
                """

    return render_template("index.html", video_url=video_url, embed_url=embed_url,
                           questions=questions_data, error=error_message)


if __name__ == '__main__':
    app.run(debug=True)
