"""Feuilles de style CSS pour l'application."""

from __future__ import annotations

# CSS principal

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,600;1,400&display=swap');

/* Variables */
:root {
  --bg-base:    #181b21;
  --bg-card:    #1f2329;
  --bg-surface: #262b33;
  --border:     #363c48;
  --border-hi:  #c09840;
  --green:      #c09840;
  --green-hi:   #d4ac50;
  --blue:       #5f82a6;
  --blue-hi:    #7a9aba;
  --red:        #b84a3f;
  --red-hi:     #cc6055;
  --text:       #d8dbe2;
  --muted:      #828894;
  --faint:      #252930;
}

/* Base */
[data-testid="stAppViewContainer"] {
  background: var(--bg-base);
  color: var(--text);
}
[data-testid="stSidebar"] {
  background: var(--bg-card);
  border-right: 1px solid var(--border);
}
[data-testid="stHeader"] { background: transparent !important; }

html, body, [class*="css"] {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* Title */
.term-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2em;
  font-weight: 600;
  color: var(--green);
  text-align: center;
  letter-spacing: 0.06em;
  margin-bottom: 0;
  line-height: 1.2;
}
.term-byline {
  text-align: center;
  color: var(--muted);
  font-size: 0.75em;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.08em;
  margin-top: 4px;
  margin-bottom: 4px;
}
.term-divider {
  text-align: center;
  color: var(--border);
  font-size: 0.72em;
  letter-spacing: 0.1em;
  margin-bottom: 20px;
}

/* Output boxes */
.out-plain {
  background: #1a2520;
  border: 1px solid #5a8a6a;
  border-left: 3px solid #5a8a6a;
  border-radius: 2px;
  padding: 12px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.05em;
  letter-spacing: 0.1em;
  color: #7aaa8a;
  word-break: break-all;
}
.out-key {
  background: #1a1f28;
  border: 1px solid #5f82a6;
  border-left: 3px solid #5f82a6;
  border-radius: 2px;
  padding: 12px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.05em;
  letter-spacing: 0.1em;
  color: #7a9aba;
  word-break: break-all;
}
.out-cipher {
  background: #221a1a;
  border: 1px solid #b84a3f;
  border-left: 3px solid #b84a3f;
  border-radius: 2px;
  padding: 12px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.05em;
  letter-spacing: 0.1em;
  color: #cc6055;
  word-break: break-all;
}

/* Step log card */
.step-card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 2px;
  padding: 8px 12px;
  margin-bottom: 5px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82em;
  color: var(--muted);
}
.step-card b { color: var(--text); }

/* Metrics */
[data-testid="stMetric"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 2px !important;
  padding: 10px !important;
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72em !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--green) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.6em !important;
}

/* Tabs */
[data-testid="stTab"] {
  color: var(--muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82em !important;
  letter-spacing: 0.04em !important;
}
[data-testid="stTabList"] { border-bottom: 1px solid var(--border) !important; }
[data-testid="stTab"][aria-selected="true"] {
  color: var(--green) !important;
  border-bottom-color: var(--green) !important;
}

/* Buttons */
.stButton > button {
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 0.04em !important;
  font-size: 0.82em !important;
  border-radius: 2px !important;
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  transition: border-color 0.12s, color 0.12s;
}
.stButton > button:hover {
  border-color: var(--green) !important;
  color: var(--green) !important;
}
button[kind="primary"] {
  background: var(--faint) !important;
  border-color: var(--green) !important;
  color: var(--green) !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9em !important;
  border-radius: 2px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--green) !important;
  box-shadow: none !important;
}

/* Letter table */
.letter-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}
.letter-table th {
  padding: 6px 10px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  color: var(--muted);
  font-weight: 400;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.letter-table td { padding: 5px 10px; text-align: center; }

/* Headings */
h1, h2, h3 {
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--text) !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
}
h4, h5, h6 {
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--muted) !important;
  font-weight: 400 !important;
  text-transform: uppercase !important;
  font-size: 0.78em !important;
  letter-spacing: 0.1em !important;
}

/* Sidebar */
[data-testid="stSidebar"] h2 {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.9em !important;
  color: var(--text) !important;
  border-bottom: 1px solid var(--border) !important;
  padding-bottom: 8px !important;
}
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 0.82em !important; }
[data-testid="stSidebar"] p { color: var(--text); }

/* Divider */
hr { border-color: var(--border) !important; }

/* Alerts */
[data-testid="stAlert"] {
  border-radius: 2px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.84em !important;
}

/* Expander */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 2px !important;
  background: var(--bg-card) !important;
}
[data-testid="stExpander"] summary {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82em !important;
  color: var(--muted) !important;
  letter-spacing: 0.04em !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 1px; }

/* Slider */
[data-testid="stSlider"] { padding: 4px 0; }
[data-testid="stSlider"] label { font-family: 'JetBrains Mono', monospace !important; }
</style>
"""


# CSS de la démonstration (table de poker, animations)

DEMO_CSS = """
<style>
/* Card animations */
@keyframes dealCard {
    0%   { transform: translateY(-60px) scale(0.6) rotate(-8deg); opacity: 0; }
    60%  { transform: translateY(6px) scale(1.03) rotate(1deg); opacity: 1; }
    100% { transform: translateY(0) scale(1) rotate(0deg); opacity: 1; }
}
@keyframes slideFromLeft {
    from { transform: translateX(-120px) rotate(-12deg); opacity: 0; }
    to   { transform: translateX(0) rotate(0); opacity: 1; }
}
@keyframes slideFromRight {
    from { transform: translateX(120px) rotate(12deg); opacity: 0; }
    to   { transform: translateX(0) rotate(0); opacity: 1; }
}
@keyframes cardHover {
    0%   { transform: translateY(0); }
    50%  { transform: translateY(-4px); }
    100% { transform: translateY(0); }
}
@keyframes pulseGold {
    0%   { box-shadow: 0 0 4px rgba(192,152,64,0.2); }
    50%  { box-shadow: 0 0 8px rgba(192,152,64,0.3); }
    100% { box-shadow: 0 0 4px rgba(192,152,64,0.2); }
}
@keyframes glowPulse {
    0%   { filter: brightness(1); }
    50%  { filter: brightness(1.05); }
    100% { filter: brightness(1); }
}
@keyframes bubbleIn {
    from { transform: scale(0.9) translateY(8px); opacity: 0; }
    to   { transform: scale(1) translateY(0); opacity: 1; }
}
@keyframes feltShimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Poker table */
.poker-table-outer {
    background: linear-gradient(145deg, #2a1a0a 0%, #1a0f05 50%, #0d0800 100%);
    border-radius: 50% / 30%;
    padding: 12px;
    box-shadow: 0 12px 48px rgba(0,0,0,0.7),
                inset 0 2px 4px rgba(255,255,255,0.05);
    position: relative;
}
.poker-table-rail {
    background: linear-gradient(180deg, #5a3a1a 0%, #3a2510 40%, #2a1a08 100%);
    border-radius: 50% / 30%;
    padding: 8px;
    box-shadow: inset 0 4px 12px rgba(0,0,0,0.5),
                inset 0 -2px 6px rgba(212,175,55,0.1);
    position: relative;
}
.poker-table-rail::before {
    content: '';
    position: absolute;
    top: 3px; left: 3px; right: 3px; bottom: 3px;
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 50% / 30%;
    pointer-events: none;
}
.poker-table-felt {
    background: radial-gradient(ellipse at 50% 40%, #1f7a3a 0%, #196b30 25%, #135a28 50%, #0d4a1e 75%, #083814 100%);
    border-radius: 50% / 30%;
    min-height: 320px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px 20px;
    box-shadow: inset 0 0 80px rgba(0,0,0,0.3),
                inset 0 0 20px rgba(0,0,0,0.2);
}
.poker-table-felt::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%226%22 height=%226%22><rect width=%226%22 height=%226%22 fill=%22transparent%22/><circle cx=%223%22 cy=%223%22 r=%220.6%22 fill=%22rgba(255,255,255,0.015)%22/></svg>');
    pointer-events: none;
    z-index: 0;
}
.poker-table-felt::after {
    content: '';
    position: absolute;
    top: 12px; left: 12px; right: 12px; bottom: 12px;
    border: 1.5px solid rgba(212,175,55,0.12);
    border-radius: 50% / 30%;
    pointer-events: none;
    z-index: 0;
}

/* Spotlight card */
.spotlight-card {
    display: inline-block;
    text-align: center;
    position: relative;
    z-index: 1;
    transition: transform 0.3s ease;
}
.spotlight-card:hover {
    transform: translateY(-8px) scale(1.04);
}
.spotlight-card img {
    border-radius: 10px;
    display: block;
    transition: all 0.3s ease;
}
.spotlight-card:nth-child(1) { animation: slideFromLeft 0.5s ease-out; }
.spotlight-card:nth-child(2) { animation: dealCard 0.6s ease-out 0.1s both; }
.spotlight-card:nth-child(3) { animation: slideFromRight 0.5s ease-out 0.2s both; }
.spotlight-card:nth-child(4) { animation: dealCard 0.5s ease-out 0.3s both; }
.spotlight-card-label {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    margin-top: 8px;
    letter-spacing: 0.06em;
}

/* Info bubble */
.demo-bubble {
    background: linear-gradient(135deg, #1e2530 0%, #181c24 100%);
    border: 1px solid #363c48;
    border-radius: 10px;
    border-bottom-left-radius: 4px;
    padding: 16px 20px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.demo-bubble::before {
    content: '';
    position: absolute;
    bottom: -8px; left: 16px;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-top: 8px solid #30363d;
}
.demo-bubble-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95em; font-weight: 700;
    letter-spacing: 0.04em; margin-bottom: 6px;
}
.demo-bubble-text {
    color: #c9d1d9;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em; line-height: 1.5;
}
.demo-bubble-tip {
    color: #8b949e;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72em; font-style: italic;
    margin-top: 6px; padding-top: 6px;
    border-top: 1px solid #21262d;
}

/* Scoreboard */
.demo-scoreboard {
    background: radial-gradient(ellipse at center, #1a2e20 0%, #0f1f15 100%);
    border: 1px solid #c09840;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 10px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

/* Cipher tracker */
.demo-cipher-char {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4em; font-weight: 700;
    margin: 0 3px; padding: 4px 10px;
    border-radius: 6px;
    transition: all 0.3s ease;
}
.demo-cipher-done {
    background: rgba(192,152,64,0.1);
    border: 1px solid rgba(192,152,64,0.3);
    color: #c09840;
}
.demo-cipher-current {
    background: rgba(192,152,64,0.15);
    border: 2px solid #c09840;
    color: #d4ac50;
}
.demo-cipher-pending {
    background: rgba(139,148,158,0.1);
    border: 1px solid #30363d;
    color: #484f58;
}
.demo-progress-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7em; color: #8b949e;
    letter-spacing: 0.1em; text-transform: uppercase;
    text-align: center; margin: 4px 0;
}
</style>
"""
