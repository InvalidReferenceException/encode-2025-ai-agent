# ENCODE 2025 HACKATHON - GENESIS VOID
---

## 🎮 The Game: GENESIS VOID

An on-chain AI sandbox where every step you take carves reality out of the void.

Powered by Portia AI and LLM integration, just say "build a blue castle" and watch it appear in 3D before your eyes. 🏰✨

Players can **own tiles**, **rent land**, and **capture enemy zones** in a world where everything — terrain, buildings, ownership, and state — is stored fully on-chain using Starkware’s **Dojo engine** and **Cairo 1.0**.

In a strategic twist, **surrounding enemy zones lets you capture the center** — think **Minecraft meets chess**, all on the blockchain.

**Steve**, your AI assistant, turns your imagination into 3D assets, stores them in Supabase, and syncs them into the on-chain world. Built for full decentralization and player ownership.

Behind the scenes:
- **Dojo** handles the on-chain world state
- **Nethermind** powers seamless Starknet execution
- **Portia AI** + **LLMs** drive generative design

This isn’t just a game.  
It’s a living, breathing, generative world. And Steve? He’s here to help you shape it.

---

## 🧠 About STEVE (using Portia AI)

**STEVE** is an AI-powered agent designed to autonomously create and manage **3D assets** for a hybrid **Minecraft x Monopoly-style** game built on the **blockchain**. STEVE bridges the gap between player-driven creativity and scalable world-building by generating terrain, structures, and game elements that live on-chain.

---

## 🔤 What does STEVE stand for?

> **S.T.E.V.E.**  
> **S**mart **T**erraforming & **E**nvironment **V**isualization **E**ngine

---

## 🌐 Architecture Overview

- **🧠 Python Backend**: Uses Portia AI to generate images and 3D models from text prompts
- **🏗️ Dojo Engine**: Manages on-chain components, systems, and world logic using StarkNet
- **🎮 Three.js Frontend**: Renders tiles and 3D models in a fully interactive browser experience
- **🪂 Supabase**: Stores and serves public URLs for `.glb` and `.png` assets

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.11+
- `pip` or `poetry`
- Dojo CLI (`sozo`, `katana`, `torii`)
- Node.js (for frontend)
- `.env` file with API keys:

  ```env
  PORTIA_API_KEY=

  OPENAI_API_KEY=
  GOOGLE_API_KEY=
  STABILITY_API_KEY=

  SUPABASE_URL=
  SUPABASE_SERVICE_ROLE_KEY=
  ```

---

## 📥 Install Backend Dependencies

Using `pip`:

```bash
cd python-backend
pip install -r requirements.txt
```

Or with `poetry`:

```bash
poetry install
```

---

## 🧪 Run Backend API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Assumes your FastAPI entrypoint is in `app/main.py`.

---

## ⛓️ Run Dojo Locally (On-chain World)

From the `dojo/` directory:

```bash
katana     # in one terminal
torii --world <world_address>     # in another terminal
sozo migrate --name localworld    # to deploy the world
```

Configure your `dojo_dev.toml` with the deployed world address for Torii.

---

## 🖼️ Image + 3D Generation Flow

1. Portia AI receives a prompt
2. Generates an image using OpenAI DALL·E
3. Converts it to a 3D `.glb` model using Stability AI
4. Stores both files in `generated_assets/`
5. Uploads to Supabase and returns a public URL

---

## 🛰️ Example cURL Request

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scene_description": "A cherry blossom",
    "tile_index": 42,
    "neighbours": [11, 13, 7]
  }'
```

### ✅ Output

```json
{
  "uploaded_url": "https://<supabase-link>/encode-assets/42.glb"
}
```

---

## 🎮 Frontend (Three.js)

The frontend is located in `vue-frontend/` and uses **Three.js** to render tiles and load `.glb` models dynamically from Supabase.

### 📦 Setup

```bash
cd vue-frontend
npm install
npm run dev
```

> Make sure environment variables in the frontend match your Supabase setup.

---

## 📂 Project Structure

```
.
├── python-backend/
│   ├── app/
│   │   ├── main.py
│   │   └── tools/
│   ├── generated_assets/
│   ├── .env
│   └── requirements.txt
├── dojo/
│   ├── src/
│   ├── Scarb.toml
│   └── dojo_dev.toml
├── vue-frontend/
│   ├── public/
│   └── src/
└── README.md
```

---

## 🛠 Tech Stack

- **Portia AI** – Agent orchestration
- **OpenAI (DALL·E)** – Image generation
- **Stability AI** – 3D model generation
- **Supabase** – Asset storage & CDN
- **Dojo + StarkNet** – On-chain systems and world
- **FastAPI** – API backend
- **Three.js** – WebGL frontend
- **Python + Vue.js** – Full stack

---

## 👾 Built for ENCODE 2025 Hackathon

Made with ❤️ by a team of agents and humans — Genesis Void is your sandbox for using AI generated assets to create your own world on the blockchain!

---