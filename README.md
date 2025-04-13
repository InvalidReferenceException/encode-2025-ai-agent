# ENCODE 2025 HACKATHON - GENESIS VOID
---

## 🧠 About STEVE (using Portia AI)

**STEVE** is an AI-powered agent designed to autonomously create and manage **3D assets** for a hybrid **Minecraft x Monopoly-style** game built on the **blockchain**. STEVE bridges the gap between player-driven creativity and scalable world-building by generating terrain, structures, and game elements that live on-chain.

---

## 🔤 What does STEVE stand for?

> **S.T.E.V.E.**  
> **S**mart **T**erraforming & **E**nvironment **V**isualization **E**ngine

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.11+
- `pip` or `poetry`
- `.env` file with API keys:

  ```
  PORTIA_API_KEY=

  OPENAI_API_KEY=
  GOOGLE_API_KEY=
  STABILITY_API_KEY=

  SUPABASE_URL=
  SUPABASE_SERVICE_ROLE_KEY=
  ```

### 📥 Install Dependencies

You can install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

Or with `poetry` if you're using it:

```bash
poetry install
```

---

## 🧪 Running the API Server

Start the FastAPI server using `uvicorn`:

```bash
uvicorn app.main:app --reload
```

Assumes your FastAPI entrypoint is in `app/main.py` with a variable named `app`.

---

## 🛰️ Example cURL Request

Here’s how to make a request to STEVE once the server is running:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scene_description": ""A cherry blossom"",
    "tile_index": 42,
    "neighbours": [11, 13, 7]
  }'
```

### Expected Output:

```json
{
  "uploaded_url": "generated_images/tile-42.glb"
}
```

---

## 💾 Upload to Supabase

Once the 3D model is created, STEVE automatically uploads both the `.png` and `.glb` files to a Supabase bucket and returns a public URL for the 3D asset.

---

## 📂 Project Structure

```
.
├── app/
│   ├── main.py            # FastAPI entrypoint
│   ├── tools/             # Tools for image gen, 3D modeling, and upload
│   └── models/            # Pydantic schemas
├── generated_images/      # Output directory for local images and models
├── .env                   # API keys
├── requirements.txt
└── README.md
```

---

## 🛠 Tech Stack

- **OpenAI DALL·E** – Image generation
- **Stability AI** – 3D asset generation
- **Supabase** – Asset storage
- **FastAPI** – Backend API
- **Python** – Everything else

---

## 👾 Built for ENCODE 2025 Hackathon

Made with ❤️ by a team of agents and humans — STEVE is your AI Terraforming sidekick.

---
