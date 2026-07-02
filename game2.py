import streamlit as st
import random

st.set_page_config(
    page_title="Hangman – princedexAI",
    page_icon="🪢",
    layout="centered",
)

# ─── Word bank ─────────────────────────────────────────────────────────────────
WORD_BANK = {
    "Animals": [
        "elephant", "crocodile", "penguin", "chimpanzee", "flamingo",
        "porcupine", "chameleon", "kangaroo", "wolverine", "armadillo",
        "rhinoceros", "salamander", "albatross", "orangutan", "barracuda",
    ],
    "Countries": [
        "nigeria", "brazil", "argentina", "indonesia", "portugal",
        "switzerland", "mozambique", "bangladesh", "zimbabwe", "kazakhstan",
        "madagascar", "philippines", "cameroon", "venezuela", "azerbaijan",
    ],
    "Technology": [
        "algorithm", "blockchain", "encryption", "compiler", "framework",
        "kubernetes", "cybersecurity", "javascript", "postgresql", "tensorflow",
        "microservice", "repository", "bandwidth", "deployment", "virtualization",
    ],
}

MAX_WRONG = 6

# ─── Hangman SVG ───────────────────────────────────────────────────────────────
def hangman_svg(wrong: int) -> str:
    parts = ["""
    <line x1="20" y1="230" x2="180" y2="230" stroke="#f59e0b" stroke-width="4" stroke-linecap="round"/>
    <line x1="60" y1="230" x2="60"  y2="20"  stroke="#f59e0b" stroke-width="4" stroke-linecap="round"/>
    <line x1="60" y1="20"  x2="130" y2="20"  stroke="#f59e0b" stroke-width="4" stroke-linecap="round"/>
    <line x1="130" y1="20" x2="130" y2="50"  stroke="#f59e0b" stroke-width="3" stroke-linecap="round"/>
    """]
    if wrong >= 1:
        parts.append('<circle cx="130" cy="70" r="20" stroke="#e2e8f0" stroke-width="3" fill="none"/>')
    if wrong >= 2:
        parts.append('<line x1="130" y1="90" x2="130" y2="160" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round"/>')
    if wrong >= 3:
        parts.append('<line x1="130" y1="110" x2="100" y2="140" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round"/>')
    if wrong >= 4:
        parts.append('<line x1="130" y1="110" x2="160" y2="140" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round"/>')
    if wrong >= 5:
        parts.append('<line x1="130" y1="160" x2="100" y2="200" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round"/>')
    if wrong >= 6:
        parts.append('<line x1="130" y1="160" x2="160" y2="200" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round"/>')
    inner = "\n".join(parts)
    return f'<svg viewBox="0 0 200 250" xmlns="http://www.w3.org/2000/svg" width="200" height="250"><rect width="200" height="250" fill="none"/>{inner}</svg>'

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Boogaloo&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
.stApp {
    background: #080b1a;
    background-image: radial-gradient(ellipse at 20% 10%, rgba(245,158,11,0.06) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 90%, rgba(34,211,238,0.05) 0%, transparent 50%);
    color: #e2e8f0;
}
section[data-testid="stSidebar"] { background: #0d1124 !important; border-right: 1px solid #1e2a4a !important; }
section[data-testid="stSidebar"] * { color: #c0cce8 !important; }

.game-title {
    font-family: 'Boogaloo', cursive; font-size: 3rem;
    background: linear-gradient(90deg, #f59e0b, #fbbf24, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1; margin: 0;
}
.game-subtitle { font-size: 0.82rem; letter-spacing: 0.25em; text-transform: uppercase; color: #4a5a7a; font-family: 'Share Tech Mono', monospace; }
.sec-label { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase; color: #3a4a6a; margin-bottom: 0.5rem; }

.word-row { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin: 1.5rem 0 1rem; }
.letter-box {
    width: 40px; height: 52px; border-bottom: 3px solid #2a3a5a;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Boogaloo', cursive; font-size: 1.8rem; color: #f59e0b; text-transform: uppercase;
}
.letter-box.shown { border-bottom-color: #f59e0b; }

.used-letters { font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; letter-spacing: 0.1em; text-align: center; color: #ef4444; margin-bottom: 0.5rem; }

.gallows-wrap { background: #0d1124; border: 1px solid #1e2a4a; border-radius: 16px; padding: 1rem; text-align: center; }

.stat-row { display: flex; justify-content: space-around; background: #0d1124; border: 1px solid #1e2a4a; border-radius: 12px; padding: 0.8rem; margin-bottom: 1rem; }
.stat-item { text-align: center; }
.stat-val { font-family: 'Boogaloo', cursive; font-size: 1.6rem; color: #fff; line-height: 1; }
.stat-lbl { font-size: 0.6rem; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.15em; color: #3a4a6a; text-transform: uppercase; }

.win-box  { background: #091a0d; border: 1px solid #22c55e; border-radius: 14px; padding: 2rem; text-align: center; margin: 1rem 0; }
.lose-box { background: #1a0909; border: 1px solid #ef4444; border-radius: 14px; padding: 2rem; text-align: center; margin: 1rem 0; }
.res-title { font-family: 'Boogaloo', cursive; font-size: 2.2rem; color: #fff; }
.res-word  { font-family: 'Boogaloo', cursive; font-size: 2.5rem; margin: 0.3rem 0; }
.res-sub   { font-size: 0.85rem; color: #6a7a9a; font-family: 'Share Tech Mono', monospace; }

.cat-badge { display: inline-block; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; font-family: 'Share Tech Mono', monospace; }
.cat-Animals    { background: #1a2a10; color: #86efac; border: 1px solid #22c55e; }
.cat-Countries  { background: #0a2030; color: #7dd3fc; border: 1px solid #38bdf8; }
.cat-Technology { background: #200a30; color: #d8b4fe; border: 1px solid #a855f7; }
.cat-Custom     { background: #2a200a; color: #fde68a; border: 1px solid #f59e0b; }

.stButton > button {
    background: linear-gradient(135deg, #d97706, #f59e0b) !important; color: #000 !important;
    border: none !important; border-radius: 12px !important;
    font-family: 'Rajdhani', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; width: 100% !important;
    box-shadow: 0 4px 20px rgba(245,158,11,0.25) !important;
}
.stButton > button:hover { background: linear-gradient(135deg, #f59e0b, #fbbf24) !important; }
.stTextInput > div > div > input, .stSelectbox > div > div {
    background: #0d1124 !important; border: 1px solid #1e2a4a !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
    font-family: 'Share Tech Mono', monospace !important; font-size: 1.1rem !important;
    text-transform: uppercase !important; letter-spacing: 0.15em !important;
}
label, .stTextInput label, .stSelectbox label {
    color: #4a5a7a !important; font-size: 0.7rem !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
}
h1, h2, h3 { color: #fff !important; }
hr { border-color: #1e2a4a !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────
def reset_game():
    for k in ["word","category","guessed","wrong_count","game_over","game_won","phase"]:
        if k in st.session_state:
            del st.session_state[k]

def init_state():
    for k, v in {
        "phase": "menu",
        "word": "",
        "category": "",
        "guessed": set(),
        "wrong_count": 0,
        "game_over": False,
        "game_won": False,
        "scores": {"wins": 0, "losses": 0},
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

def start_game(word, category):
    s.word        = word.lower().strip()
    s.category    = category
    s.guessed     = set()
    s.wrong_count = 0
    s.game_over   = False
    s.game_won    = False
    s.phase       = "playing"

def process_guess(letter):
    letter = letter.lower()
    if letter in s.guessed or s.game_over or not letter.isalpha():
        return
    s.guessed.add(letter)
    if letter not in s.word:
        s.wrong_count += 1
    if all(c in s.guessed for c in s.word):
        s.game_won = True
        s.game_over = True
        s.scores["wins"] += 1
        s.phase = "result"
    elif s.wrong_count >= MAX_WRONG:
        s.game_over = True
        s.scores["losses"] += 1
        s.phase = "result"

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style='text-align:center;padding:0.5rem 0 1rem'>
  <span style='font-family:Boogaloo,cursive;font-size:2rem;background:linear-gradient(90deg,#f59e0b,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>Hangman</span><br>
  <span style='font-size:0.65rem;letter-spacing:0.2em;color:#3a4a6a;font-family:Share Tech Mono,monospace'>HOW TO PLAY</span>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
**🎯 Objective**
Guess the hidden word before the hangman is fully drawn.

---

**🔤 How it works**
1. A secret word is chosen (random or custom).
2. You see blank slots — one per letter.
3. Type a letter and press Enter to guess.
4. ✅ Correct — the letter fills in its slot(s).
5. ❌ Wrong — a body part is added to the hangman.
6. You get **6 wrong guesses** before game over.

---

**📂 Categories**
🐘 **Animals** · 🌍 **Countries** · 💻 **Technology** · 🔡 **Custom**

---

**💡 Tips**
Start with vowels: **A, E, I, O, U**
Then try: **R, S, T, N, L**

---
""")
    st.markdown("<div class='sec-label'>Session Score</div>", unsafe_allow_html=True)
    st.markdown(f"""
<div style='display:flex;gap:0.8rem;justify-content:center;margin-bottom:1rem'>
  <div style='text-align:center;background:#091a0d;border:1px solid #22c55e44;border-radius:10px;padding:0.6rem 1.2rem'>
    <div style='font-family:Boogaloo,cursive;font-size:1.8rem;color:#22c55e'>{s.scores['wins']}</div>
    <div style='font-size:0.62rem;font-family:Share Tech Mono,monospace;color:#3a5a3a;letter-spacing:0.12em'>WINS</div>
  </div>
  <div style='text-align:center;background:#1a0909;border:1px solid #ef444444;border-radius:10px;padding:0.6rem 1.2rem'>
    <div style='font-family:Boogaloo,cursive;font-size:1.8rem;color:#ef4444'>{s.scores['losses']}</div>
    <div style='font-size:0.62rem;font-family:Share Tech Mono,monospace;color:#5a3a3a;letter-spacing:0.12em'>LOSSES</div>
  </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div style='padding:1rem;background:#0a0f1e;border:1px solid #1e2a4a;border-radius:12px;text-align:center'>
  <div style='font-family:Boogaloo,cursive;font-size:1.3rem;background:linear-gradient(90deg,#f59e0b,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text'>princedexAI</div>
  <div style='font-size:0.62rem;color:#3a4a6a;font-family:Share Tech Mono,monospace;letter-spacing:0.12em;margin:0.3rem 0 0.7rem'>GAME DEVELOPER</div>
  <div style='font-size:0.72rem;color:#5a6a8a;font-family:Share Tech Mono,monospace;line-height:1.9'>
    📧 ifeanyistephen003@gmail.com<br>📱 WhatsApp: 07061968856
  </div>
  <div style='font-size:0.6rem;color:#2a3a5a;font-family:Share Tech Mono,monospace;margin-top:0.7rem'>Built with ❤️ using Streamlit</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MENU
# ══════════════════════════════════════════════════════════════════════════════
if s.phase == "menu":
    st.markdown("""
<div style='text-align:center;padding:1.5rem 0 0.5rem'>
  <div class='game-title'>🪢 Hangman</div>
  <div class='game-subtitle'>Guess the word · Save the man</div>
</div>
""", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
<div style='background:#0d1124;border:1px solid #1e2a4a;border-radius:14px;padding:1.2rem;text-align:center;margin-bottom:0.8rem'>
  <div style='font-size:2rem'>🎲</div>
  <div style='font-weight:700;font-size:1.1rem;color:#fff;margin:0.3rem 0'>Random Word</div>
  <div style='font-size:0.8rem;color:#5a6a8a'>Computer picks from Animals, Countries or Technology</div>
</div>
""", unsafe_allow_html=True)
        category = st.selectbox("Category", ["Random mix", "Animals", "Countries", "Technology"])
        if st.button("▶ Play Random"):
            cat = random.choice(list(WORD_BANK.keys())) if category == "Random mix" else category
            start_game(random.choice(WORD_BANK[cat]), cat)
            st.rerun()

    with col2:
        st.markdown("""
<div style='background:#0d1124;border:1px solid #1e2a4a;border-radius:14px;padding:1.2rem;text-align:center;margin-bottom:0.8rem'>
  <div style='font-size:2rem'>🔡</div>
  <div style='font-weight:700;font-size:1.1rem;color:#fff;margin:0.3rem 0'>Custom Word</div>
  <div style='font-size:0.8rem;color:#5a6a8a'>A friend types a secret word for you to guess</div>
</div>
""", unsafe_allow_html=True)
        st.write("")
        st.write("")
        if st.button("▶ Play Custom"):
            s.phase = "custom_entry"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM ENTRY
# ══════════════════════════════════════════════════════════════════════════════
elif s.phase == "custom_entry":
    st.markdown("""
<div style='text-align:center;padding:1.5rem 0 0.5rem'>
  <div class='game-title' style='font-size:2.2rem'>🔡 Custom Word</div>
  <div class='game-subtitle'>Friend enters a secret word</div>
</div>
""", unsafe_allow_html=True)
    st.divider()
    st.info("📱 Hand the device to your friend — guesser should look away!")
    custom_word = st.text_input("Secret word (letters only)", type="password", placeholder="e.g. python")
    custom_cat  = st.text_input("Category hint (optional)", placeholder="e.g. Programming language")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✅ Start Game"):
            clean = custom_word.strip().lower()
            if not clean:
                st.error("Please enter a word.")
            elif not clean.isalpha():
                st.error("Letters only — no numbers or symbols.")
            else:
                start_game(clean, custom_cat.strip() or "Custom")
                st.rerun()
    with col_b:
        if st.button("↩ Back"):
            s.phase = "menu"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PLAYING
# ══════════════════════════════════════════════════════════════════════════════
elif s.phase == "playing":

    # Header
    st.markdown(f"""
<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem'>
  <div class='game-title' style='font-size:2rem'>🪢 Hangman</div>
  <span class='cat-badge cat-{s.category}'>{s.category}</span>
</div>
""", unsafe_allow_html=True)
    st.divider()

    # Stats
    lives_left  = MAX_WRONG - s.wrong_count
    lives_color = "#22c55e" if lives_left > 3 else ("#f59e0b" if lives_left > 1 else "#ef4444")
    correct_ct  = sum(1 for c in s.word if c in s.guessed)
    st.markdown(f"""
<div class='stat-row'>
  <div class='stat-item'><div class='stat-val' style='color:{lives_color}'>{lives_left}</div><div class='stat-lbl'>Lives Left</div></div>
  <div class='stat-item'><div class='stat-val'>{s.wrong_count}</div><div class='stat-lbl'>Wrong</div></div>
  <div class='stat-item'><div class='stat-val'>{correct_ct}</div><div class='stat-lbl'>Correct</div></div>
  <div class='stat-item'><div class='stat-val'>{len(s.word)}</div><div class='stat-lbl'>Letters</div></div>
</div>
""", unsafe_allow_html=True)

    # Gallows + word side by side using st.columns (no nesting inside)
    col_g, col_w = st.columns([1, 1.8])

    with col_g:
        st.markdown(f"<div class='gallows-wrap'>{hangman_svg(s.wrong_count)}</div>", unsafe_allow_html=True)

    with col_w:
        # Word slots
        slots = "".join(
            f"<div class='letter-box shown'>{c}</div>" if c in s.guessed
            else "<div class='letter-box'>_</div>"
            for c in s.word
        )
        st.markdown(f"<div class='word-row'>{slots}</div>", unsafe_allow_html=True)

        # Wrong letters
        wrong_letters = [l.upper() for l in sorted(s.guessed) if l not in s.word]
        if wrong_letters:
            st.markdown(f"<div class='used-letters'>✗ Wrong: {' · '.join(wrong_letters)}</div>", unsafe_allow_html=True)

        # Guess input — single text_input, no columns, no buttons inside columns
        st.markdown("<div class='sec-label' style='margin-top:1rem'>Type a letter and press Enter</div>", unsafe_allow_html=True)
        guess_input = st.text_input(
            "Your guess",
            key=f"guess_input_{len(s.guessed)}",   # new key each turn forces widget reset
            max_chars=1,
            placeholder="A",
            label_visibility="collapsed",
        )
        if guess_input:
            letter = guess_input.strip().lower()
            if letter and letter.isalpha():
                if letter in s.guessed:
                    st.warning(f"You already guessed '{letter.upper()}' — try another letter.")
                else:
                    process_guess(letter)
                    st.rerun()

    st.divider()
    if st.button("↩ Quit to Menu"):
        reset_game()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif s.phase == "result":

    if s.game_won:
        st.markdown(f"""
<div class='win-box'>
  <div style='font-size:3rem'>🎉</div>
  <div class='res-title'>You got it!</div>
  <div class='res-word' style='color:#f59e0b'>{s.word.upper()}</div>
  <div class='res-sub'>{s.wrong_count} wrong guess{"es" if s.wrong_count != 1 else ""} · {s.category}</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class='lose-box'>
  <div style='font-size:3rem'>💀</div>
  <div class='res-title'>Game Over</div>
  <div class='res-word' style='color:#ef4444'>{s.word.upper()}</div>
  <div class='res-sub'>The word was <strong>{s.word}</strong> · {s.category}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown(f"<div class='gallows-wrap' style='max-width:220px;margin:1rem auto'>{hangman_svg(MAX_WRONG)}</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Play Again"):
            reset_game()
            st.rerun()
    with col_b:
        if st.button("🏠 Main Menu"):
            reset_game()
            st.rerun()