# Demigod Chronicles RPG

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Gemini API](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange)
![License](https://img.shields.io/badge/license-MIT-green)

A terminal-based text RPG set in the universe of Percy Jackson (by Rick Riordan). The game is dynamically powered by **Google's Gemini AI**, which acts as an intelligent Game Master. It reacts to your creative choices, generates the narrative, and secretly manages your character's stats using background JSON responses.

---

## Features

* **AI-Powered Game Master:** No pre-written paths. Gemini 2.5 Flash reacts to *any* action you take.
* **Bilingual:** Full localization for English and Polish (prompts, UI, and narrative).
* **Background RPG Engine:** The AI seamlessly controls your HP, Experience, Drachmas, Inventory, and Status Effects by appending structured JSON to its narrative output.
* **Resilient Parsing:** Built-in validation and retry mechanisms ensure the game won't crash if the AI hallucinates an invalid JSON block.
* **Colorful Terminal UI:** Interactive health/XP bars and formatted event logs using `colorama`.
* **Secret Demigod Parentage:** The AI secretly rolls your divine parent (Zeus, Poseidon, Hades, etc.) and leaves subtle hints in the narrative before the grand reveal.

---

## Installation & Setup

**1. Prerequisites**
* Python 3.10 or higher.
* A free **Google Gemini API Key**. You can get one at [Google AI Studio](https://aistudio.google.com/app/apikey).

**2. Clone and install dependencies**
```bash
git clone [https://github.com/YOUR_USERNAME/demigod-chronicles-rpg.git](https://github.com/YOUR_USERNAME/demigod-chronicles-rpg.git)
cd demigod-chronicles-rpg
pip install google-genai colorama
```

**3. Configure your API Key**
You must set your Gemini API key as an environment variable before running the game:

* **Windows (Command Prompt):**
    ```cmd
    set GEMINI_API_KEY=your_api_key_here
    ```
* **Windows (PowerShell):**
    ```powershell
    $env:GEMINI_API_KEY="your_api_key_here"
    ```
* **Linux / macOS:**
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```

**4. Run the game!**
```bash
python rpg_engine.py
```

---

## How to Play

The game plays like a classic tabletop RPG session. The Game Master describes the scene and gives you a set of choices (A, B, C). However, since it's an AI, **you don't have to pick the provided options**—you can type literally anything you want to do!

**In-Game System Commands:**
These commands do not advance the story but let you manage your session:
* `/status` or `/stat` — View your Level, HP, XP, Drachmas, and Status Effects.
* `/inventory` or `/inv` — Check what items you have.
* `/help` — Show the command list.
* `/quit` or `/exit` — End the game session.

---

## How it works under the hood

This project demonstrates a practical implementation of **LLM Structured Output extraction**. The AI is instructed via the System Prompt to append a specific delimiter (`---JSON---`) followed by a valid JSON object modifying the game state:

```text
The harpy swoops down and slashes your arm with its talons! You try to dodge, but you drop your backpack in the process.

---JSON---
{"damage": 5, "heal": 0, "gold_change": 0, "xp_gain": 10, "status_effect": "bleeding", "note": "Player lost backpack, dropped it in the alley."}
```
The Python engine parses this response, displays the narrative text to the player, and silently applies the JSON data to the `PlayerState` dataclass, triggering UI updates like Level Ups or Game Over screens.

---

*Disclaimer: This is a fan-made, non-commercial project. Percy Jackson and the Olympians are the property of Rick Riordan and Disney Hyperion.*
