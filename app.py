from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import requests

# === CONFIG ===
openai.api_key = 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
ELEVENLABS_API_KEY = "sk_38722ef7138d73e230b272d05d9b29e2748fbe7455e1020a"
ELEVEN_VOICE_ID = "ZF6FPAbjXT4488VcRRnw"
BUSINESS_NAME = "Gemini Universal Services"
# ===============

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    """Handle incoming call"""
    response = VoiceResponse()
    response.say("Hello! Thank you for calling Gemini Universal Services. Please say how I can help you after the beep.")
    response.record(
        action="/process_recording",
        maxLength=10,
        transcribe=True,
        playBeep=True
    )
    return Response(str(response), mimetype="text/xml")

@app.route("/process_recording", methods=["POST"])
def process_recording():
    transcript = request.form.get("TranscriptionText")
    if not transcript:
        transcript = "Caller did not say anything or transcription failed."

    print("Caller said:", transcript)

    try:
        ai_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a helpful receptionist for {BUSINESS_NAME}."},
                {"role": "user", "content": transcript}
            ]
        )
        ai_text = ai_response.choices[0].message.content
    except Exception as e:
        # Print the full error to Render logs
        import traceback
        print("OpenAI error traceback:")
        traceback.print_exc()
        ai_text = "Sorry, there was a problem processing your request."

    resp = VoiceResponse()
    resp.say(ai_text)
    return Response(str(resp), mimetype="application/xml")



@app.route("/response.mp3", methods=["GET"])
def serve_audio():
    """Serve audio file to Twilio"""
    return open("response.mp3", "rb").read(), 200, {"Content-Type": "audio/mpeg"}

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)







