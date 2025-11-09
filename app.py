from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import requests

# === CONFIG ===
openai.api_key = "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"
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
    """Process caller's speech and reply"""
    transcription = request.form.get("TranscriptionText", "")
    print(f"Caller said: {transcription}")

    # Generate AI reply
    prompt = f"You are a polite AI receptionist for {BUSINESS_NAME}. Respond helpfully to: {transcription}"
    ai_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    ai_text = ai_response.choices[0].message["content"]
    print(f"AI response: {ai_text}")

    # Convert AI text to speech (ElevenLabs)
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    tts_data = {
        "text": ai_text,
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}
    }
    tts_audio = requests.post(tts_url, json=tts_data, headers=headers).content

    # Save audio file
    with open("response.mp3", "wb") as f:
        f.write(tts_audio)

    # Return TwiML to play the audio
    response = VoiceResponse()
    response.play("https://YOUR_SERVER_URL/response.mp3")
    response.say("Goodbye!")
    return Response(str(response), mimetype="text/xml")

@app.route("/response.mp3", methods=["GET"])
def serve_audio():
    """Serve audio file to Twilio"""
    return open("response.mp3", "rb").read(), 200, {"Content-Type": "audio/mpeg"}

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

