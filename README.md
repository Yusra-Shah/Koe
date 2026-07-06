# Koe — AI-Powered Sign Language Accessibility Platform

Koe (声, Japanese for "voice") is an AI-powered accessibility platform that translates American Sign Language (ASL) fingerspelling into spoken and written language in real time. It is designed for deaf, mute, and hard-of-hearing users who need to communicate in environments where sign language interpreters are unavailable — clinics, government offices, banks, and emergency situations.

Built as a dual submission for the **Kaggle Agents for Good Capstone** and the **Google Cloud Skills Boost Hackathon (Problem Statement 1: Accessibility)**.

**Live Demo:** https://koe-alpha.vercel.app  
**Backend API:** https://koe-production-c3cb.up.railway.app  
**GitHub:** https://github.com/Yusra-Shah/Koe

---

## What It Does

A user signs in front of their webcam. MediaPipe detects 21 hand landmarks client-side (no video leaves the device). Those coordinates are sent to a backend powered by Google ADK, where a six-agent pipeline classifies the gesture, generates a natural-language sentence, translates it to Urdu, and returns the result. The translated text appears in the Koe Notebook and can be read aloud via Google Cloud Text-to-Speech.

When the system detects that the user is asking for help, requesting an appointment, or in an emergency, it surfaces an MCP (Model Context Protocol) confirmation dialog that lets the user trigger real-world actions with a single tap.

---

## Architecture

```
Browser (React + MediaPipe)
    |
    | landmark coordinates (21 points × x/y/z)
    v
FastAPI Backend  (port 8080)
    |
    | Google ADK SequentialAgent (6 LlmAgents)
    |   1. InputValidationAgent    — structural validation
    |   2. GestureRecognitionAgent — TFLite MLP inference (FunctionTool)
    |   3. ConfidenceAgent         — threshold gate + BigQuery logging
    |   4. GlossToSentenceAgent    — Gemini 2.5 Flash NLP
    |   5. TranslationAgent        — Gemini English to Urdu
    |   6. OutputAgent             — MCP intent detection + JSON formatting
    |
    | FastMCP Server  (port 8081)
    |   form_fill / emergency_contact / appointment_request
    |
    | Google Cloud Services
        BigQuery    — anonymized gesture analytics
        Firestore   — per-user notebook history
        Cloud TTS   — English and Urdu audio output
        Cloud Storage — TFLite model hosting
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS v4, Framer Motion |
| Auth | Clerk (JWT, React SDK) |
| Hand detection | MediaPipe Hands (CDN WebAssembly, client-side) |
| Backend | FastAPI, Python 3.12, Uvicorn |
| AI pipeline | Google ADK 1.5.0 (SequentialAgent, LlmAgent, FunctionTool) |
| NLP and translation | Gemini 2.5 Flash (google-genai) |
| Gesture model | TFLite MLP (100% accuracy on test set, 63-feature input) |
| External tools | FastMCP 2.8.1 (MCP server, HTTP transport) |
| Analytics | Google Cloud BigQuery |
| Notebook storage | Google Cloud Firestore |
| Text to speech | Google Cloud TTS (en-US, ur-PK) |
| Model storage | Google Cloud Storage |
| Deployment | Google Cloud Run (Docker) |

---

## Gesture Recognition Model

The TFLite MLP model was trained on a Kaggle dataset of ASL fingerspelling landmarks.

Input: 21 MediaPipe hand landmarks × 3 coordinates (x, y, z) = 63 normalized features  
Output: 23 ASL fingerspelling classes (A through Z minus J and Z, which require motion)  
Accuracy: 100% on held-out test split  
Inference: runs in under 5ms on CPU via TFLite  

The model files (`.tflite`, `.pkl`, `.npy`) are stored in `model/koe_models/` locally and in Google Cloud Storage for the Cloud Run deployment.

---

## MCP Tools

The MCP server exposes three tools, all gated behind a `confirmed=True` parameter. The frontend always shows a confirmation dialog before calling any tool with confirmation — this is the human-in-the-loop consent pattern from the ADK Day 4 specification.

**emergency_contact** — sends an emergency message to family, ambulance, police, or hospital staff  
**form_fill** — submits a form (hospital registration, bank account, ID card) on behalf of the user  
**appointment_request** — requests a medical or service appointment with a specified department and date  

The backend detects MCP intent from the translated sentence using the OutputAgent. If the sentence expresses a need for help, emergency contact, or an appointment, the frontend surfaces the confirmation dialog automatically.

---

## Project Structure

```
Koe/
  koe-backend/
    agents/
      pipeline.py         6-agent ADK SequentialAgent + direct fallback
    models/
      gesture_classifier.py   TFLite inference, Cloud Storage fallback
    routers/
      translate.py        POST /translate
      tts.py              POST /tts
      analytics.py        POST /analytics
      mcp.py              POST /mcp/execute
    services/
      bigquery_service.py
      firestore_service.py
      gemini_service.py
      tts_service.py
    middleware/
      auth.py             Clerk JWT verification (PyJWT)
    schemas/
      landmarks.py        Pydantic request/response models
    main.py
    config.py
    requirements.txt
    Dockerfile

  koe-mcp-server/
    main.py               FastMCP server with 3 tools
    Dockerfile

  koe-frontend/
    src/
      components/
        CameraView.jsx        webcam + MediaPipe overlay
        NotebookPanel.jsx     translation history
        MCPConfirmDialog.jsx  tool confirmation modal
        ConfidenceRing.jsx    animated SVG confidence indicator
        QuickCards.jsx        quick sign shortcuts
        ReverseMode.jsx       text-to-sign reverse mode
      hooks/
        useMediaPipe.js       MediaPipe CDN loader + landmark state
        useTranslation.js     debounced API calls + dedup
        useTTS.js             Cloud TTS with browser fallback
      services/
        api.js                Axios client with Clerk JWT injection
      App.jsx
      index.css               TailwindCSS v4 theme tokens

  model/
    koe_models/             TFLite model + encoder + normalization stats
    notebook.ipynb          Kaggle training notebook

  setup/
    bigquery_tables.sql     CREATE TABLE statements for analytics
    firestore.rules         owner-only security rules
    deploy.sh               Cloud Run deploy script
```

---

## Local Development Setup

**Prerequisites:** Python 3.12, Node.js 18+, Google Cloud SDK

**1. Clone and set up environment variables**

Create `Koe/.env` with:

```
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
CLERK_SECRET_KEY=your_clerk_secret_key
FIRESTORE_PROJECT=your_gcp_project_id
BIGQUERY_DATASET=koe_analytics
MCP_SERVER_URL=http://localhost:8081
MODEL_BUCKET=
```

Create `koe-frontend/.env` with:

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
VITE_API_URL=http://localhost:8080
```

**2. Install backend dependencies**

```bash
cd koe-backend
pip install -r requirements.txt
```

**3. Start the MCP server**

```bash
cd koe-mcp-server
pip install fastmcp
python main.py
```

**4. Start the backend**

```bash
cd koe-backend
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

**5. Start the frontend**

```bash
cd koe-frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Sign in with Clerk, click Start Camera, and begin signing.

---

## Google Cloud Setup

**BigQuery** — run `setup/bigquery_tables.sql` in the BigQuery console to create the `gesture_events` and `tool_events` tables under dataset `koe_analytics`.

**Firestore** — create a Firestore database in Native mode in the GCP console. Apply `setup/firestore.rules` for security.

**Application Default Credentials** — run `gcloud auth application-default login` so the backend can access BigQuery, Firestore, and TTS locally.

**Cloud Run deployment** — fill in project and region in `setup/deploy.sh`, then run it from the repo root. The script uploads model files to Cloud Storage, builds and pushes Docker images, and deploys both services.

---

## Privacy

MediaPipe hand detection runs entirely in the browser using WebAssembly. No video frames are ever sent to the backend. Only the 63 normalized landmark coordinates (floating-point numbers) are transmitted per recognition event. No personally identifiable information is stored — BigQuery events are keyed by a hashed session ID.

---

## Hackathon Context

**Kaggle Agents for Good Capstone** — demonstrates a multi-agent ADK pipeline (Day 1 to Day 5 patterns: tool use, sequential agents, memory via Firestore, MCP integration, human-in-the-loop confirmation).

**Google Cloud Skills Boost Hackathon, Problem Statement 1 (Accessibility)** — uses Gemini 2.5 Flash for NLP, Google Cloud TTS for audio output, BigQuery for analytics, Firestore for persistence, and Cloud Run for deployment.

---

## Author

Yusra Batool  
Kaggle: [kaggle.com/yusrashah05](https://kaggle.com/yusrashah05)  
GitHub: [github.com/Yusra-Shah](https://github.com/Yusra-Shah)
