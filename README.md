# Dark Skies: The SDK Odyssey 🚀

**Dark Skies** is a space-themed educational game built with Python and Pygame to help developers learn key concepts about LaunchDarkly SDKs. Fly a VW camper van through the galaxy, dodging bugs, reading trivia, and making real-time decisions — powered by feature flags.

---

## 🕹️ Gameplay

- Press space to jump.
- Dodge obstacles representing SDK misconfigurations.
- Trivia modals will pause the game periodically with tips and questions.
- Optional: Feature flags (via LaunchDarkly) control game behaviors like background art, modal display, or difficulty.

---

## 🛠️ Built With

- 🐍 Python 3.11+
- 🎮 Pygame
- 🚩 LaunchDarkly (planned integration)
- 🎨 Custom sprites and sound assets

---

## 📦 Setup

0. Check your python3 and pip version
   ```bash
      python3 --version 
   ```
   should be greater than or equal to 3.11
   ```bash
      pip --version 
   ```
   should be greater than 20.0 (pygame requirement)

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/dark-skies-sdk-odyssey.git
   cd dark-skies-sdk-odyssey
   ```
2. Install the pygame dependency
   ```bash
      pip install pygame
   ```

3. Run the application at the root directory
   ```bash
      python3 main.py
   ```