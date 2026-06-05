import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Database connection
from database.connection import get_db, init_db, SessionLocal
from models.models import User, Wallet, Transaction, Match, Player, FantasyTeam, Contest, ContestEntry, PlayerPerformance
from services.auth import register_user, login_user
from services import match_service, contest_service, wallet_service, points_service
from utils import helpers

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fantasy11 Pro | Live Cricket",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dark Neon Cricket Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root Variables ── */
:root {
  --bg-deep:    #060811;
  --bg-card:    #0d1117;
  --bg-surface: #111827;
  --border:     #1f2937;
  --border-glow:#00ff88;
  --red:        #ff2d4b;
  --gold:       #f5c518;
  --green:      #00ff88;
  --cyan:       #00d4ff;
  --white:      #f1f5f9;
  --muted:      #6b7280;
  --font-head:  'Orbitron', monospace;
  --font-body:  'Rajdhani', sans-serif;
  --font-ui:    'Inter', sans-serif;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
  background-color: var(--bg-deep) !important;
  color: var(--white) !important;
  font-family: var(--font-ui) !important;
}

.stApp { background: var(--bg-deep) !important; }

/* Animated background grid */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image:
    linear-gradient(rgba(0,255,136,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,136,0.025) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #080d14 0%, #0a0f1a 100%) !important;
  border-right: 1px solid rgba(0,255,136,0.12) !important;
}
section[data-testid="stSidebar"] * { color: var(--white) !important; }

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--red), #c0213a) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: var(--font-body) !important;
  font-weight: 700 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
  font-size: 0.85rem !important;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 0 15px rgba(255,45,75,0.3) !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 0 25px rgba(255,45,75,0.5) !important;
}
.stButton > button[kind="secondary"] {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--green) !important;
  box-shadow: 0 0 12px rgba(0,255,136,0.2) !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stSelectbox select,
[data-baseweb="input"] input, [data-baseweb="select"] * {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--white) !important;
  border-radius: 8px !important;
  font-family: var(--font-ui) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 2px rgba(0,255,136,0.15) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 8px !important;
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px !important;
  transition: all 0.2s !important;
  font-size: 0.82rem !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: var(--red) !important;
  color: white !important;
  box-shadow: 0 0 12px rgba(255,45,75,0.35) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 20px !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
iframe[title="dataframe"] { background: var(--bg-card) !important; }

/* ── Form ── */
[data-testid="stForm"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 20px !important;
}

/* ── Success/Error/Info Messages ── */
.stAlert {
  border-radius: 10px !important;
  border-left-width: 3px !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
  background: var(--bg-surface) !important;
  border-color: var(--border) !important;
  border-radius: 8px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: #2a2a3d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--red); }

/* ── Custom Components ── */

/* Hero Banner */
.f11-hero {
  background: linear-gradient(135deg, #0a0f1a 0%, #0d1a0f 50%, #0a0f1a 100%);
  border: 1px solid rgba(0,255,136,0.15);
  border-radius: 16px;
  padding: 30px 35px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
.f11-hero::before {
  content: '🏏';
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 5rem;
  opacity: 0.08;
}
.f11-hero-title {
  font-family: var(--font-head);
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--white);
  letter-spacing: 2px;
  margin: 0;
}
.f11-hero-subtitle {
  color: var(--green);
  font-size: 0.85rem;
  font-family: var(--font-body);
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-top: 4px;
}

/* Live Match Card */
.live-match-card {
  background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
  border: 1px solid rgba(255,45,75,0.25);
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
}
.live-match-card:hover {
  border-color: rgba(255,45,75,0.5);
  box-shadow: 0 8px 30px rgba(255,45,75,0.15);
  transform: translateY(-2px);
}
.live-match-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--red), transparent);
}

/* Upcoming Match Card */
.upcoming-match-card {
  background: linear-gradient(135deg, #0d1117 0%, #0f1721 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px 24px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
}
.upcoming-match-card:hover {
  border-color: rgba(0,255,136,0.3);
  box-shadow: 0 8px 30px rgba(0,255,136,0.08);
  transform: translateY(-2px);
}
.upcoming-match-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--green), transparent);
}

/* Team names in match card */
.match-teams {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}
.team-name {
  font-family: var(--font-head);
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--white);
  letter-spacing: 2px;
}
.vs-badge {
  font-family: var(--font-head);
  font-size: 0.8rem;
  color: var(--red);
  font-weight: 700;
  background: rgba(255,45,75,0.12);
  border: 1px solid rgba(255,45,75,0.3);
  padding: 4px 8px;
  border-radius: 6px;
  letter-spacing: 1px;
}
.match-meta {
  font-size: 0.82rem;
  color: var(--muted);
  font-family: var(--font-ui);
}
.match-meta span { margin-right: 16px; }
.match-meta span::before { margin-right: 4px; }

/* Status Badges */
.badge-live {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255,45,75,0.15);
  border: 1px solid rgba(255,45,75,0.4);
  color: #ff6b7d;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  font-family: var(--font-body);
}
.badge-live::before {
  content: '';
  width: 6px; height: 6px;
  background: var(--red);
  border-radius: 50%;
  display: inline-block;
  animation: pulse-dot 1.2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.7); }
}

.badge-upcoming {
  display: inline-block;
  background: rgba(245,197,24,0.1);
  border: 1px solid rgba(245,197,24,0.3);
  color: var(--gold);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  font-family: var(--font-body);
}
.badge-completed {
  display: inline-block;
  background: rgba(107,114,128,0.15);
  border: 1px solid rgba(107,114,128,0.3);
  color: #9ca3af;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  font-family: var(--font-body);
}

/* Stat Cards */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--accent, var(--green));
  opacity: 0.6;
}
.stat-val {
  font-family: var(--font-head);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--white);
  line-height: 1;
}
.stat-lbl {
  font-size: 0.72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-top: 4px;
  font-family: var(--font-body);
}

/* Player Cards */
.player-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  transition: all 0.2s;
}
.player-card:hover {
  border-color: rgba(0,212,255,0.3);
  background: rgba(0,212,255,0.04);
}
.player-card.selected {
  border-color: var(--green);
  background: rgba(0,255,136,0.06);
  box-shadow: 0 0 12px rgba(0,255,136,0.1);
}
.player-name { font-weight: 600; font-size: 0.95rem; color: var(--white); }
.player-team-badge {
  font-size: 0.7rem; font-weight: 700; letter-spacing: 1px;
  padding: 2px 7px; border-radius: 4px; margin-right: 6px;
  background: rgba(255,45,75,0.15); color: var(--red); border: 1px solid rgba(255,45,75,0.25);
}
.player-role-badge {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 1px;
  padding: 2px 7px; border-radius: 4px;
  background: rgba(0,212,255,0.1); color: var(--cyan); border: 1px solid rgba(0,212,255,0.2);
}
.player-credits {
  font-family: var(--font-head); font-size: 1rem; font-weight: 700;
  color: var(--gold);
}

/* Contest Card */
.contest-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 22px;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}
.contest-card:hover {
  border-color: rgba(245,197,24,0.3);
  box-shadow: 0 4px 20px rgba(245,197,24,0.06);
}
.contest-name {
  font-family: var(--font-body);
  font-size: 1rem;
  font-weight: 700;
  color: var(--white);
  letter-spacing: 0.5px;
}
.contest-prize {
  font-family: var(--font-head);
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--gold);
}
.contest-fee {
  font-size: 0.8rem;
  color: var(--muted);
}
.contest-bar-wrap {
  background: rgba(255,255,255,0.06);
  border-radius: 4px;
  height: 4px;
  margin-top: 10px;
  overflow: hidden;
}
.contest-bar-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--green), var(--cyan));
  transition: width 0.5s ease;
}

/* Contest type badges */
.ctype-mega { background:rgba(255,45,75,0.1); color:var(--red); border:1px solid rgba(255,45,75,0.25); }
.ctype-h2h  { background:rgba(0,212,255,0.1); color:var(--cyan); border:1px solid rgba(0,212,255,0.25); }
.ctype-small{ background:rgba(245,197,24,0.1); color:var(--gold); border:1px solid rgba(245,197,24,0.25); }
.ctype-practice { background:rgba(107,114,128,0.1); color:#9ca3af; border:1px solid rgba(107,114,128,0.2); }

.ctype-badge {
  display: inline-block;
  font-size: 0.68rem; font-weight: 700; letter-spacing: 1px;
  padding: 2px 8px; border-radius: 4px; margin-left: 8px;
  text-transform: uppercase; font-family: var(--font-body);
}

/* Wallet Card */
.wallet-card {
  background: linear-gradient(135deg, #0d1a12, #0f2014);
  border: 1px solid rgba(0,255,136,0.2);
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
.wallet-card::before {
  content: '';
  position: absolute;
  top: -40%; right: -10%;
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(0,255,136,0.08), transparent 70%);
  pointer-events: none;
}
.wallet-total {
  font-family: var(--font-head);
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--green);
  line-height: 1;
}
.wallet-label { font-size: 0.75rem; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }
.wallet-breakdown {
  display: flex; gap: 24px; margin-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 14px;
}
.wb-item { }
.wb-val { font-family: var(--font-head); font-size: 1.1rem; font-weight: 700; }
.wb-lbl { font-size: 0.7rem; color: var(--muted); }

/* Sidebar Logo */
.sidebar-logo {
  font-family: var(--font-head);
  font-size: 1.6rem;
  font-weight: 900;
  color: white;
  letter-spacing: 3px;
  text-align: center;
  padding: 8px 0 4px;
}
.sidebar-logo span { color: var(--green); }
.sidebar-pro-badge {
  text-align: center;
  margin-bottom: 20px;
}
.sidebar-pro-badge span {
  background: var(--red);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 2px 10px;
  border-radius: 20px;
  text-transform: uppercase;
}

/* Leaderboard rows */
.lb-row {
  display: flex; align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 8px;
  transition: all 0.2s;
}
.lb-row:hover { border-color: rgba(245,197,24,0.3); }
.lb-rank {
  font-family: var(--font-head);
  font-size: 1.2rem;
  font-weight: 700;
  width: 40px;
  color: var(--muted);
}
.lb-rank.top1 { color: var(--gold); }
.lb-rank.top2 { color: #c0c0c0; }
.lb-rank.top3 { color: #cd7f32; }
.lb-user { flex: 1; font-weight: 600; }
.lb-pts {
  font-family: var(--font-head);
  font-size: 1rem;
  font-weight: 700;
  color: var(--cyan);
  margin-right: 20px;
}
.lb-prize { font-weight: 700; color: var(--green); }

/* Section Headers */
.section-header {
  font-family: var(--font-body);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--white);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-header::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
}

/* Auth Page */
.auth-logo {
  font-family: var(--font-head);
  font-size: 3.5rem;
  font-weight: 900;
  text-align: center;
  letter-spacing: 4px;
  margin-bottom: 4px;
}
.auth-logo .f { color: var(--white); }
.auth-logo .eleven { color: var(--green); }
.auth-logo .pro { color: var(--red); }

/* Builder progress bar */
.builder-bar {
  display: flex; gap: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 16px 0;
  flex-wrap: wrap;
}
.builder-item {
  text-align: center; flex: 1; min-width: 80px;
}
.builder-val {
  font-family: var(--font-head);
  font-size: 1.4rem;
  font-weight: 700;
}
.builder-lbl {
  font-size: 0.65rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Active player indicator */
.active-dot {
  display: inline-block;
  width: 7px; height: 7px;
  background: var(--green);
  border-radius: 50%;
  margin-right: 6px;
  box-shadow: 0 0 6px var(--green);
}

/* Transaction rows */
.tx-row {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 8px;
}
.tx-type { font-weight: 600; font-size: 0.9rem; }
.tx-amount-pos { color: var(--green); font-family: var(--font-head); font-weight: 700; }
.tx-amount-neg { color: var(--red); font-family: var(--font-head); font-weight: 700; }
.tx-date { font-size: 0.75rem; color: var(--muted); }

/* Admin Panel */
.admin-section {
  background: linear-gradient(135deg, #12080f, #1a0d0d);
  border: 1px solid rgba(255,45,75,0.2);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
}

/* No matches placeholder */
.no-matches {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted);
}
.no-matches .icon { font-size: 3rem; margin-bottom: 12px; }
.no-matches .title {
  font-family: var(--font-body);
  font-size: 1.1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #374151;
  margin-bottom: 6px;
}
.no-matches .sub { font-size: 0.85rem; }

/* Spinner overrides */
.stSpinner > div { border-color: var(--green) !important; border-top-color: transparent !important; }

/* Hide default streamlit menu bar elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DB INIT & SEEDING
# ─────────────────────────────────────────────────────────────────────────────
init_db()

def seed_database_if_empty():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin_user, _ = register_user(db, "admin", "admin@fantasy11.com", "admin123", role="admin")
            user1, _ = register_user(db, "cricket_fan", "user@fantasy11.com", "password123")
            user2, _ = register_user(db, "dhoni_fan", "dhoni@fantasy11.com", "password123")
            user3, _ = register_user(db, "virat_club", "virat@fantasy11.com", "password123")
            user4, _ = register_user(db, "sky_high", "sky@fantasy11.com", "password123")
            wallet_service.add_funds(db, user1.id, 500.0, "Welcome Bonus")
            wallet_service.add_funds(db, user2.id, 1000.0, "Deposit via UPI")
            wallet_service.add_funds(db, user3.id, 1500.0, "Deposit via Netbanking")
            wallet_service.add_funds(db, user4.id, 2000.0, "Deposit via Card")
            m1 = match_service.create_match(db=db, team_a="IND", team_b="AUS",
                match_date=datetime.now() + timedelta(days=2, hours=4),
                venue="Wankhede Stadium, Mumbai", status="upcoming")
            m2 = match_service.create_match(db=db, team_a="ENG", team_b="PAK",
                match_date=datetime.now() + timedelta(days=3, hours=2),
                venue="Lord's, London", status="upcoming")
            m3 = match_service.create_match(db=db, team_a="IND", team_b="ENG",
                match_date=datetime.now() - timedelta(days=1),
                venue="Eden Gardens, Kolkata", status="upcoming")
            contest_service.create_contest(db, m1.id, "Mega Contest 10K", "mega", 49.0, 10000.0, 100)
            contest_service.create_contest(db, m1.id, "Head To Head (Winner Takes All)", "h2h", 299.0, 500.0, 2)
            contest_service.create_contest(db, m1.id, "Small League (Top 3 Win)", "small", 99.0, 800.0, 10)
            contest_service.create_contest(db, m1.id, "Practice Match", "practice", 0.0, 0.0, 50)
            c3_1 = contest_service.create_contest(db, m3.id, "Mega League", "mega", 50.0, 5000.0, 50)
            c3_2 = contest_service.create_contest(db, m3.id, "H2H Clash", "h2h", 100.0, 180.0, 2)
            m3_players = match_service.get_match_players(db, m3.id)
            m3_ind = [p for p in m3_players if p.team == "IND"]
            m3_eng = [p for p in m3_players if p.team == "ENG"]
            squad_players = m3_ind[:6] + m3_eng[:5]
            c_id = squad_players[0].id
            vc_id = squad_players[1].id
            team_u1 = FantasyTeam(user_id=user1.id, match_id=m3.id, name="CricketPro XI",
                captain_id=c_id, vice_captain_id=vc_id)
            team_u1.players = squad_players
            db.add(team_u1)
            team_u2 = FantasyTeam(user_id=user2.id, match_id=m3.id, name="Dhoni Army",
                captain_id=squad_players[2].id, vice_captain_id=squad_players[3].id)
            team_u2.players = squad_players
            db.add(team_u2)
            team_u3 = FantasyTeam(user_id=user3.id, match_id=m3.id, name="Virat XI",
                captain_id=squad_players[4].id, vice_captain_id=squad_players[5].id)
            team_u3.players = squad_players
            db.add(team_u3)
            db.commit()
            db.add(ContestEntry(contest_id=c3_1.id, fantasy_team_id=team_u1.id, user_id=user1.id, entry_fee_paid=50.0))
            c3_1.filled_spots += 1
            db.add(ContestEntry(contest_id=c3_1.id, fantasy_team_id=team_u2.id, user_id=user2.id, entry_fee_paid=50.0))
            c3_1.filled_spots += 1
            db.add(ContestEntry(contest_id=c3_1.id, fantasy_team_id=team_u3.id, user_id=user3.id, entry_fee_paid=50.0))
            c3_1.filled_spots += 1
            db.add(ContestEntry(contest_id=c3_2.id, fantasy_team_id=team_u1.id, user_id=user1.id, entry_fee_paid=100.0))
            c3_2.filled_spots += 1
            db.add(ContestEntry(contest_id=c3_2.id, fantasy_team_id=team_u2.id, user_id=user2.id, entry_fee_paid=100.0))
            c3_2.filled_spots += 1
            db.commit()
            points_service.simulate_match_and_calculate_points(db, m3.id)
    finally:
        db.close()

seed_database_if_empty()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("authenticated", False), ("user", None), ("current_page", "dashboard"),
    ("selected_match_id", None), ("squad_builder_match_id", None),
    ("joining_contest_id", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def navigate_to(page, match_id=None, contest_id=None):
    st.session_state.current_page = page
    if match_id is not None:
        st.session_state.selected_match_id = match_id
    if contest_id is not None:
        st.session_state.joining_contest_id = contest_id
    st.rerun()

def status_badge(status):
    if status == "live":
        return "<span class='badge-live'>LIVE</span>"
    elif status == "upcoming":
        return "<span class='badge-upcoming'>UPCOMING</span>"
    return "<span class='badge-completed'>COMPLETED</span>"

def ctype_badge(ctype):
    label = {"mega": "MEGA", "h2h": "HEAD-2-HEAD", "small": "SMALL", "practice": "PRACTICE"}.get(ctype, ctype.upper())
    return f"<span class='ctype-badge ctype-{ctype}'>{label}</span>"

def render_match_card(match, card_class="upcoming-match-card"):
    date_str = match.match_date.strftime('%d %b %Y · %I:%M %p')
    return f"""
    <div class="{card_class}">
      <div class="match-teams">
        <span class="team-name">{match.team_a}</span>
        <span class="vs-badge">VS</span>
        <span class="team-name">{match.team_b}</span>
        &nbsp;&nbsp;{status_badge(match.status)}
      </div>
      <div class="match-meta">
        <span>🏟️ {match.venue}</span>
        <span>📅 {date_str}</span>
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    st.sidebar.markdown("""
    <div class='sidebar-logo'>FANTASY<span>11</span></div>
    <div class='sidebar-pro-badge'><span>PRO EDITION</span></div>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    db = SessionLocal()
    try:
        user_db = db.query(User).filter(User.id == user["id"]).first()
        wallet = user_db.wallet
        total_bal = wallet.deposit_balance + wallet.winning_balance
        role = user_db.role
    finally:
        db.close()

    st.sidebar.markdown(f"""
    <div style='background:rgba(255,255,255,0.04); border:1px solid #1f2937;
         border-radius:12px; padding:14px 16px; margin-bottom:20px;'>
      <div style='font-size:0.72rem; color:#6b7280; text-transform:uppercase; letter-spacing:1.5px;'>Logged in as</div>
      <div style='font-weight:700; font-size:1.05rem; color:#f1f5f9; margin:3px 0;'>@{user['username']}</div>
      <div style='display:inline-block; font-size:0.62rem; background:rgba(255,45,75,0.15);
           color:#ff6b7d; padding:2px 8px; border-radius:4px; border:1px solid rgba(255,45,75,0.2);
           letter-spacing:1px; font-weight:700;'>{role.upper()}</div>
      <div style='border-top:1px solid #1f2937; margin-top:12px; padding-top:10px;'>
        <div style='font-size:0.7rem; color:#6b7280;'>WALLET BALANCE</div>
        <div style='font-family:"Orbitron",monospace; font-size:1.4rem; font-weight:700;
             color:#00ff88; margin-top:2px;'>₹{total_bal:,.2f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='font-size:0.68rem; color:#4b5563; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:8px; padding:0 4px;'>NAVIGATION</div>", unsafe_allow_html=True)

    nav_items = [
        ("dashboard", "🏠", "Arena"),
        ("my_entries", "🎯", "My Teams"),
        ("wallet", "💰", "Wallet"),
        ("leaderboard", "🏆", "Leaderboard"),
        ("analytics", "📊", "Analytics"),
    ]
    for page_key, icon, label in nav_items:
        is_active = st.session_state.current_page == page_key
        btn_type = "primary" if is_active else "secondary"
        if st.sidebar.button(f"{icon}  {label}", use_container_width=True, type=btn_type, key=f"nav_{page_key}"):
            navigate_to(page_key)

    if role == "admin":
        st.sidebar.markdown("<hr style='border-color:#1f2937; margin:16px 0;' />", unsafe_allow_html=True)
        st.sidebar.markdown("<div style='font-size:0.68rem; color:#4b5563; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:8px; padding:0 4px;'>ADMIN</div>", unsafe_allow_html=True)
        if st.sidebar.button("⚙️  Control Panel", use_container_width=True,
                              type="primary" if st.session_state.current_page == "admin" else "secondary"):
            navigate_to("admin")

    st.sidebar.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
    if st.sidebar.button("🚪  Logout", use_container_width=True, type="secondary"):
        for k in ["authenticated", "user", "current_page", "selected_match_id", "squad_builder_match_id", "joining_contest_id"]:
            st.session_state[k] = False if k == "authenticated" else None if k != "current_page" else "dashboard"
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_auth_page():
    st.markdown("""
    <div style='text-align:center; padding:50px 0 30px;'>
      <div class='auth-logo'>
        <span class='f'>FANTASY</span><span class='eleven'>11</span><span class='pro'> PRO</span>
      </div>
      <div style='color:#6b7280; font-size:0.9rem; letter-spacing:3px; text-transform:uppercase;
           font-family:"Rajdhani",sans-serif; font-weight:600; margin-top:6px;'>
        India's Premium Fantasy Cricket Arena
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑  LOGIN", "📝  REGISTER"])
        with tab_login:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                username_input = st.text_input("Username or Email", placeholder="cricket_fan")
                password_input = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("LOGIN TO PLAY", use_container_width=True)
                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please fill all fields.")
                    else:
                        db = SessionLocal()
                        try:
                            user, message = login_user(db, username_input, password_input)
                            if user:
                                st.session_state.authenticated = True
                                st.session_state.user = {"id": user.id, "username": user.username, "email": user.email, "role": user.role}
                                st.rerun()
                            else:
                                st.error(message)
                        finally:
                            db.close()

        with tab_register:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                reg_username = st.text_input("Choose Username", placeholder="virat_warrior")
                reg_email = st.text_input("Email Address", placeholder="warrior@gmail.com")
                reg_password = st.text_input("Set Password", type="password", placeholder="Min 6 characters")
                reg_password_confirm = st.text_input("Confirm Password", type="password")
                submit_reg = st.form_submit_button("REGISTER & GET ₹1,000 BONUS", use_container_width=True)
                if submit_reg:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("All fields are required.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif reg_password != reg_password_confirm:
                        st.error("Passwords do not match.")
                    else:
                        db = SessionLocal()
                        try:
                            new_user, message = register_user(db, reg_username, reg_email, reg_password)
                            if new_user:
                                st.success("Account created! Log in to get started.")
                            else:
                                st.error(message)
                        finally:
                            db.close()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD — LIVE MATCHES FIRST, then upcoming
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard_page():
    st.markdown("""
    <div class='f11-hero'>
      <div class='f11-hero-subtitle'>⚡ Live Fantasy Platform</div>
      <div class='f11-hero-title'>CRICKET ARENA</div>
      <div style='color:#6b7280; font-size:0.85rem; margin-top:8px;
           font-family:"Inter",sans-serif;'>
        Build your dream squad · Enter contests · Win real cash
      </div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        live_matches = match_service.get_matches_by_status(db, "live")
        upcoming_matches = match_service.get_matches_by_status(db, "upcoming")
        completed_matches = match_service.get_matches_by_status(db, "completed")

        # Quick Stats
        st.markdown(f"""
        <div class='stat-grid'>
          <div class='stat-card' style='--accent:#ff2d4b;'>
            <div class='stat-val' style='color:#ff6b7d;'>{len(live_matches)}</div>
            <div class='stat-lbl'>Live Now</div>
          </div>
          <div class='stat-card' style='--accent:#f5c518;'>
            <div class='stat-val' style='color:#f5c518;'>{len(upcoming_matches)}</div>
            <div class='stat-lbl'>Upcoming</div>
          </div>
          <div class='stat-card' style='--accent:#00d4ff;'>
            <div class='stat-val' style='color:#00d4ff;'>{len(live_matches)+len(upcoming_matches)}</div>
            <div class='stat-lbl'>Active</div>
          </div>
          <div class='stat-card' style='--accent:#6b7280;'>
            <div class='stat-val' style='color:#9ca3af;'>{len(completed_matches)}</div>
            <div class='stat-lbl'>Completed</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tab_live, tab_upcoming, tab_completed = st.tabs([
            f"🔴  LIVE ({len(live_matches)})",
            f"📅  UPCOMING ({len(upcoming_matches)})",
            f"🏆  COMPLETED ({len(completed_matches)})"
        ])

        with tab_live:
            if not live_matches:
                st.markdown("""
                <div class='no-matches'>
                  <div class='icon'>🔴</div>
                  <div class='title'>No Live Matches</div>
                  <div class='sub'>Live matches will appear here when declared by admin</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for match in live_matches:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(render_match_card(match, "live-match-card"), unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
                        if st.button("⚡ View Live", key=f"btn_live_{match.id}", use_container_width=True):
                            navigate_to("match_details", match_id=match.id)

        with tab_upcoming:
            if not upcoming_matches:
                st.markdown("""
                <div class='no-matches'>
                  <div class='icon'>📅</div>
                  <div class='title'>No Upcoming Matches</div>
                  <div class='sub'>Check back soon for new matches</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for match in upcoming_matches:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(render_match_card(match), unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
                        if st.button("Enter Match", key=f"btn_enter_{match.id}", use_container_width=True, type="primary"):
                            navigate_to("match_details", match_id=match.id)

        with tab_completed:
            if not completed_matches:
                st.markdown("""
                <div class='no-matches'>
                  <div class='icon'>🏆</div>
                  <div class='title'>No Completed Matches</div>
                  <div class='sub'>Past matches with results will appear here</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for match in completed_matches:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(render_match_card(match), unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
                        if st.button("View Results", key=f"btn_comp_{match.id}", use_container_width=True):
                            navigate_to("match_details", match_id=match.id)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# MATCH DETAILS — with ACTIVE PLAYERS ONLY (is_playing=True)
# ─────────────────────────────────────────────────────────────────────────────
def render_match_details_page():
    match_id = st.session_state.selected_match_id
    if not match_id:
        navigate_to("dashboard")
        return

    db = SessionLocal()
    try:
        match = match_service.get_match_by_id(db, match_id)
        if not match:
            st.error("Match not found.")
            if st.button("Back to Arena"):
                navigate_to("dashboard")
            return

        if st.button("← Back to Arena", key="back_btn"):
            navigate_to("dashboard")

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#0d1117,#111827);
             border:1px solid #1f2937; border-radius:16px; padding:24px 28px;
             margin:12px 0 24px; position:relative; overflow:hidden;'>
          <div style='position:absolute; top:0; left:0; right:0; height:2px;
               background:linear-gradient(90deg,transparent,
               {"#ff2d4b" if match.status == "live" else "#00ff88" if match.status == "upcoming" else "#6b7280"},
               transparent);'></div>
          <div style='display:flex; align-items:center; gap:16px; flex-wrap:wrap;'>
            <div style='font-family:"Orbitron",monospace; font-size:2rem; font-weight:900;
                 color:#f1f5f9; letter-spacing:2px;'>
              {match.team_a} <span style='color:#ff2d4b; font-size:1.2rem;'>VS</span> {match.team_b}
            </div>
            {status_badge(match.status)}
          </div>
          <div style='margin-top:10px; font-size:0.85rem; color:#6b7280;'>
            🏟️ {match.venue} &nbsp;·&nbsp; 📅 {match.match_date.strftime('%d %b %Y, %I:%M %p')}
          </div>
        </div>
        """, unsafe_allow_html=True)

        my_teams = db.query(FantasyTeam).filter(
            FantasyTeam.user_id == st.session_state.user["id"],
            FantasyTeam.match_id == match_id
        ).all()

        col_main, col_side = st.columns([3, 1.2])

        with col_side:
            st.markdown("<div class='section-header'>My Squads</div>", unsafe_allow_html=True)
            if not my_teams:
                st.markdown("""
                <div style='background:rgba(255,45,75,0.06); border:1px dashed rgba(255,45,75,0.25);
                     border-radius:10px; padding:16px; text-align:center; color:#6b7280;
                     font-size:0.85rem;'>No squad created yet</div>
                """, unsafe_allow_html=True)
            else:
                for team in my_teams:
                    captain = db.query(Player).filter(Player.id == team.captain_id).first()
                    vc = db.query(Player).filter(Player.id == team.vice_captain_id).first()
                    pts_color = "#00ff88" if team.total_points > 0 else "#6b7280"
                    st.markdown(f"""
                    <div style='background:#0d1117; border:1px solid #1f2937; border-radius:12px;
                         padding:14px 16px; margin-bottom:10px;'>
                      <div style='font-weight:700; color:#f1f5f9; font-size:0.95rem;'>{team.name}</div>
                      <div style='font-size:0.78rem; color:#6b7280; margin-top:6px;'>
                        ⚡ C: <b style='color:#f5c518;'>{captain.name if captain else "N/A"}</b>
                        &nbsp; VC: <b style='color:#9ca3af;'>{vc.name if vc else "N/A"}</b>
                      </div>
                      <div style='margin-top:8px; font-family:"Orbitron",monospace;
                           font-size:1rem; font-weight:700; color:{pts_color};'>
                        {team.total_points:.1f} pts
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            if match.status == "upcoming":
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                if st.button("➕ Create Squad", use_container_width=True, type="primary"):
                    st.session_state.squad_builder_match_id = match_id
                    navigate_to("squad_builder")

        with col_main:
            st.markdown("<div class='section-header'>Available Contests</div>", unsafe_allow_html=True)
            contests = contest_service.get_contests_by_match(db, match_id)
            if not contests:
                st.info("No contests available for this match.")
            else:
                for contest in contests:
                    joined_entry = db.query(ContestEntry).filter(
                        ContestEntry.contest_id == contest.id,
                        ContestEntry.user_id == st.session_state.user["id"]
                    ).first()
                    fill_pct = (contest.filled_spots / contest.total_spots * 100) if contest.total_spots > 0 else 0
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.markdown(f"""
                        <div class='contest-card'>
                          <div style='display:flex; align-items:center; justify-content:space-between;'>
                            <div>
                              <span class='contest-name'>{contest.name}</span>
                              {ctype_badge(contest.contest_type)}
                            </div>
                            <div class='contest-prize'>₹{contest.prize_pool:,.0f}</div>
                          </div>
                          <div style='display:flex; gap:20px; margin-top:10px;'>
                            <div class='contest-fee'>Entry: <b style='color:#f1f5f9;'>
                              {"FREE" if contest.entry_fee == 0 else f"₹{contest.entry_fee:.0f}"}
                            </b></div>
                            <div class='contest-fee'>Spots: <b style='color:#f1f5f9;'>
                              {contest.filled_spots}/{contest.total_spots}
                            </b></div>
                          </div>
                          <div class='contest-bar-wrap'>
                            <div class='contest-bar-fill' style='width:{fill_pct:.1f}%;'></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_col2:
                        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
                        if joined_entry:
                            st.success(f"✓ Joined #{joined_entry.rank or '-'}")
                            if match.status == "completed" and joined_entry.prize_won > 0:
                                st.markdown(f"<div style='font-weight:700; color:#00ff88;'>Won ₹{joined_entry.prize_won:,.2f}</div>", unsafe_allow_html=True)
                        elif match.status == "upcoming":
                            if not my_teams:
                                st.button("Need Squad", key=f"dis_{contest.id}", disabled=True, use_container_width=True)
                            else:
                                if st.button("Join", key=f"join_{contest.id}", use_container_width=True, type="primary"):
                                    navigate_to("join_confirm", match_id=match_id, contest_id=contest.id)
                        else:
                            st.markdown("<div style='color:#6b7280; font-size:0.8rem; text-align:center; padding-top:8px;'>Closed</div>", unsafe_allow_html=True)

        # ── Playing XI – ACTIVE PLAYERS ONLY ──
        st.markdown("<hr style='border-color:#1f2937; margin:24px 0 20px;' />", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🟢 Active Playing XI</div>", unsafe_allow_html=True)

        # Filter only active/playing players (is_playing=True)
        all_players = match_service.get_match_players(db, match_id)
        players = [p for p in all_players if getattr(p, 'is_playing', True)]  # fallback to show all if attr missing

        if not players:
            st.markdown("""
            <div class='no-matches'>
              <div class='icon'>⏳</div>
              <div class='title'>Playing XI Not Announced</div>
              <div class='sub'>Active squad will appear once announced</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            team_a_players = [p for p in players if p.team == match.team_a]
            team_b_players = [p for p in players if p.team == match.team_b]

            t_col1, t_col2 = st.columns(2)
            for col, team_name, team_players in [(t_col1, match.team_a, team_a_players), (t_col2, match.team_b, team_b_players)]:
                with col:
                    st.markdown(f"""
                    <div style='background:rgba(255,45,75,0.05); border:1px solid rgba(255,45,75,0.15);
                         border-radius:10px; padding:10px 14px; margin-bottom:14px; text-align:center;'>
                      <span style='font-family:"Orbitron",monospace; font-size:1.1rem; font-weight:700;
                           letter-spacing:2px; color:#f1f5f9;'>{team_name}</span>
                      <span style='font-size:0.75rem; color:#6b7280; margin-left:8px;'>
                        {len(team_players)} players
                      </span>
                    </div>
                    """, unsafe_allow_html=True)

                    for p in team_players:
                        perf = db.query(PlayerPerformance).filter(PlayerPerformance.player_id == p.id).first()
                        pts = perf.total_points if perf else 0.0
                        runs = perf.runs if perf else 0
                        wks = perf.wickets if perf else 0
                        pts_disp = f"<span style='font-family:\"Orbitron\",monospace; font-weight:700; color:#00ff88;'>{pts:.0f}</span> pts" if pts > 0 else ""
                        perf_str = ""
                        if runs > 0: perf_str += f"🏏 {runs}r "
                        if wks > 0: perf_str += f"🎯 {wks}w"
                        st.markdown(f"""
                        <div class='player-card'>
                          <div>
                            <div style='display:flex; align-items:center; gap:6px;'>
                              <span class='active-dot'></span>
                              <span class='player-name'>{p.name}</span>
                            </div>
                            <div style='margin-top:4px;'>
                              <span class='player-team-badge'>{p.team}</span>
                              <span class='player-role-badge'>{p.role}</span>
                              {f"<span style='font-size:0.75rem; color:#9ca3af; margin-left:4px;'>{perf_str}</span>" if perf_str else ""}
                            </div>
                          </div>
                          <div style='text-align:right;'>
                            <div class='player-credits'>{p.credits}cr</div>
                            <div style='font-size:0.75rem; margin-top:2px;'>{pts_disp}</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# SQUAD BUILDER — uses only is_playing=True players
# ─────────────────────────────────────────────────────────────────────────────
def render_squad_builder_page():
    match_id = st.session_state.squad_builder_match_id
    if not match_id:
        navigate_to("dashboard")
        return

    db = SessionLocal()
    try:
        match = match_service.get_match_by_id(db, match_id)
        if not match:
            navigate_to("dashboard")
            return

        st.markdown(f"""
        <div class='f11-hero'>
          <div class='f11-hero-subtitle'>Squad Builder</div>
          <div class='f11-hero-title'>{match.team_a} VS {match.team_b}</div>
          <div style='color:#6b7280; font-size:0.82rem; margin-top:6px;'>
            Select 11 active players · Budget 100 credits · Min: 1 WK · 3 BAT · 1 AR · 3 BOWL · Max 7 from one team
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ACTIVE PLAYERS ONLY
        all_players = match_service.get_match_players(db, match_id)
        players = [p for p in all_players if getattr(p, 'is_playing', True)]

        selected_key = f"builder_selection_{match_id}"
        if selected_key not in st.session_state:
            st.session_state[selected_key] = []
        selected_ids = st.session_state[selected_key]

        roles = ["WK", "BAT", "AR", "BOWL"]
        role_icons = {"WK": "🧤", "BAT": "🏏", "AR": "⚡", "BOWL": "🍒"}
        role_labels = {"WK": "Wicket Keepers", "BAT": "Batsmen", "AR": "All Rounders", "BOWL": "Bowlers"}

        role_tabs = st.tabs([
            f"{role_icons[r]}  {role_labels[r]} ({len([p for p in players if p.role == r])})"
            for r in roles
        ])

        for idx, role in enumerate(roles):
            with role_tabs[idx]:
                role_players = [p for p in players if p.role == role]
                if not role_players:
                    st.markdown("<div style='color:#6b7280; text-align:center; padding:20px;'>No active players in this role</div>", unsafe_allow_html=True)
                    continue
                for player in role_players:
                    is_selected = player.id in selected_ids
                    card_class = "player-card selected" if is_selected else "player-card"
                    row_col1, row_col2 = st.columns([5, 1])
                    with row_col1:
                        st.markdown(f"""
                        <div class='{card_class}'>
                          <div>
                            <div style='display:flex; align-items:center; gap:6px;'>
                              <span class='active-dot'></span>
                              <span class='player-name'>{player.name}</span>
                              {"<span style='font-size:0.7rem; color:#00ff88; font-weight:700;'>✓ SELECTED</span>" if is_selected else ""}
                            </div>
                            <div style='margin-top:4px;'>
                              <span class='player-team-badge'>{player.team}</span>
                              <span class='player-role-badge'>{player.role}</span>
                            </div>
                          </div>
                          <div class='player-credits'>{player.credits}cr</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with row_col2:
                        checked = st.checkbox("Select", value=is_selected, key=f"p_check_{player.id}", label_visibility="collapsed")
                        if checked and player.id not in selected_ids:
                            st.session_state[selected_key].append(player.id)
                            st.rerun()
                        elif not checked and player.id in selected_ids:
                            st.session_state[selected_key].remove(player.id)
                            st.rerun()

        # Stats bar
        selected_objects = [p for p in players if p.id in selected_ids]
        total_credits = sum(p.credits for p in selected_objects)
        credits_left = 100.0 - total_credits
        team_counts = {}
        role_counts = {"WK": 0, "BAT": 0, "AR": 0, "BOWL": 0}
        for p in selected_objects:
            team_counts[p.team] = team_counts.get(p.team, 0) + 1
            role_counts[p.role] = role_counts.get(p.role, 0) + 1

        credits_color = "#ff2d4b" if credits_left < 0 else "#00ff88"
        players_color = "#00ff88" if len(selected_ids) == 11 else "#f5c518" if len(selected_ids) > 0 else "#6b7280"

        st.markdown(f"""
        <div class='builder-bar'>
          <div class='builder-item'>
            <div class='builder-val' style='color:{players_color};'>{len(selected_ids)}/11</div>
            <div class='builder-lbl'>Players</div>
          </div>
          <div class='builder-item'>
            <div class='builder-val' style='color:{credits_color};'>{credits_left:.1f}</div>
            <div class='builder-lbl'>Credits Left</div>
          </div>
          <div class='builder-item'>
            <div class='builder-val' style='color:{"#00ff88" if role_counts["WK"]>=1 else "#ff2d4b"};'>{role_counts["WK"]}</div>
            <div class='builder-lbl'>WK (≥1)</div>
          </div>
          <div class='builder-item'>
            <div class='builder-val' style='color:{"#00ff88" if role_counts["BAT"]>=3 else "#ff2d4b"};'>{role_counts["BAT"]}</div>
            <div class='builder-lbl'>BAT (≥3)</div>
          </div>
          <div class='builder-item'>
            <div class='builder-val' style='color:{"#00ff88" if role_counts["AR"]>=1 else "#ff2d4b"};'>{role_counts["AR"]}</div>
            <div class='builder-lbl'>AR (≥1)</div>
          </div>
          <div class='builder-item'>
            <div class='builder-val' style='color:{"#00ff88" if role_counts["BOWL"]>=3 else "#ff2d4b"};'>{role_counts["BOWL"]}</div>
            <div class='builder-lbl'>BOWL (≥3)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if len(selected_ids) == 11:
            st.markdown("<div class='section-header'>Choose Captain & Vice-Captain</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:#6b7280; font-size:0.83rem; margin-bottom:12px;'>Captain earns 2× points · Vice-Captain earns 1.5× points</div>", unsafe_allow_html=True)
            c_options = [(p.id, f"{p.name} ({p.role} · {p.team})") for p in selected_objects]
            col_c, col_vc = st.columns(2)
            with col_c:
                cap_id = st.selectbox("👑 Captain (2×)", options=[o[0] for o in c_options], format_func=lambda x: next(o[1] for o in c_options if o[0] == x))
            with col_vc:
                vc_options = [o for o in c_options if o[0] != cap_id]
                vc_id = st.selectbox("🥈 Vice-Captain (1.5×)", options=[o[0] for o in vc_options], format_func=lambda x: next(o[1] for o in vc_options if o[0] == x)) if vc_options else None

            existing_count = db.query(FantasyTeam).filter(
                FantasyTeam.user_id == st.session_state.user["id"],
                FantasyTeam.match_id == match_id
            ).count()
            team_name = st.text_input("Name Your Fantasy Squad", value=f"Team {existing_count + 1}")

            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Save Squad", use_container_width=True, type="primary"):
                    is_valid, err_msg = helpers.validate_fantasy_team(selected_objects, cap_id, vc_id)
                    if not is_valid:
                        st.error(err_msg)
                    else:
                        try:
                            new_team = FantasyTeam(user_id=st.session_state.user["id"], match_id=match_id,
                                name=team_name, captain_id=cap_id, vice_captain_id=vc_id, total_points=0.0)
                            new_team.players = selected_objects
                            db.add(new_team)
                            db.commit()
                            st.success(f"Squad '{team_name}' saved!")
                            del st.session_state[selected_key]
                            navigate_to("match_details", match_id=match_id)
                        except Exception as e:
                            db.rollback()
                            st.error(f"Failed: {str(e)}")
            with col_cancel:
                if st.button("Cancel", use_container_width=True):
                    if selected_key in st.session_state:
                        del st.session_state[selected_key]
                    navigate_to("match_details", match_id=match_id)
        else:
            st.info(f"Select {11 - len(selected_ids)} more player(s) to continue.")
            if st.button("← Cancel & Go Back"):
                if selected_key in st.session_state:
                    del st.session_state[selected_key]
                navigate_to("match_details", match_id=match_id)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# JOIN CONFIRM
# ─────────────────────────────────────────────────────────────────────────────
def render_join_confirm_page():
    match_id = st.session_state.selected_match_id
    contest_id = st.session_state.joining_contest_id
    if not match_id or not contest_id:
        navigate_to("dashboard")
        return

    db = SessionLocal()
    try:
        match = match_service.get_match_by_id(db, match_id)
        contest = contest_service.get_contest_by_id(db, contest_id)
        if not match or not contest:
            st.error("Error loading match/contest.")
            if st.button("Go Back"):
                navigate_to("dashboard")
            return

        st.markdown(f"""
        <div class='f11-hero'>
          <div class='f11-hero-subtitle'>Contest Entry</div>
          <div class='f11-hero-title'>{match.team_a} VS {match.team_b}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown(f"""
            <div class='contest-card'>
              <div class='contest-name'>{contest.name} {ctype_badge(contest.contest_type)}</div>
              <div style='margin-top:14px; display:flex; gap:30px; align-items:center;'>
                <div>
                  <div style='font-size:0.7rem; color:#6b7280; letter-spacing:1px; text-transform:uppercase;'>Prize Pool</div>
                  <div class='contest-prize'>₹{contest.prize_pool:,.0f}</div>
                </div>
                <div>
                  <div style='font-size:0.7rem; color:#6b7280; letter-spacing:1px; text-transform:uppercase;'>Entry Fee</div>
                  <div style='font-family:"Orbitron",monospace; font-size:1.4rem; font-weight:700; color:#f5c518;'>
                    {"FREE" if contest.entry_fee == 0 else f"₹{contest.entry_fee:.0f}"}
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            wallet = wallet_service.get_wallet_by_user(db, st.session_state.user["id"])
            total_bal = wallet.deposit_balance + wallet.winning_balance
            bal_color = "#00ff88" if total_bal >= contest.entry_fee else "#ff2d4b"
            st.markdown(f"""
            <div class='wallet-card' style='margin-bottom:0;'>
              <div class='wallet-label'>Your Balance</div>
              <div class='wallet-total' style='font-size:2rem; color:{bal_color};'>₹{total_bal:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        my_teams = db.query(FantasyTeam).filter(
            FantasyTeam.user_id == st.session_state.user["id"],
            FantasyTeam.match_id == match_id
        ).all()

        if not my_teams:
            st.error("Create a fantasy squad first!")
            if st.button("Go to Team Builder"):
                navigate_to("squad_builder")
            return

        team_options = {t.id: t.name for t in my_teams}
        selected_team_id = st.selectbox("Select Squad to Play With", options=list(team_options.keys()),
                                         format_func=lambda x: team_options[x])

        if total_bal < contest.entry_fee:
            st.error(f"Insufficient funds! Need ₹{contest.entry_fee - total_bal:.2f} more.")
            if st.button("Go to Wallet"):
                navigate_to("wallet")
        else:
            col_pay, col_back = st.columns(2)
            with col_pay:
                if st.button("✅ Pay & Join Contest", use_container_width=True, type="primary"):
                    success, message = contest_service.join_contest(db, st.session_state.user["id"], contest_id, selected_team_id)
                    if success:
                        st.success(message)
                        navigate_to("match_details", match_id=match_id)
                    else:
                        st.error(message)
            with col_back:
                if st.button("← Cancel", use_container_width=True):
                    navigate_to("match_details", match_id=match_id)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# WALLET
# ─────────────────────────────────────────────────────────────────────────────
def render_wallet_page():
    st.markdown("""
    <div class='f11-hero'>
      <div class='f11-hero-subtitle'>Finance Center</div>
      <div class='f11-hero-title'>MY WALLET</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        user_id = st.session_state.user["id"]
        wallet = wallet_service.get_wallet_by_user(db, user_id)
        dep = wallet.deposit_balance
        win = wallet.winning_balance
        total = dep + win

        st.markdown(f"""
        <div class='wallet-card'>
          <div class='wallet-label'>Total Balance</div>
          <div class='wallet-total'>₹{total:,.2f}</div>
          <div class='wallet-breakdown'>
            <div class='wb-item'>
              <div class='wb-val' style='color:#00d4ff;'>₹{dep:,.2f}</div>
              <div class='wb-lbl'>Deposit Balance</div>
            </div>
            <div class='wb-item'>
              <div class='wb-val' style='color:#00ff88;'>₹{win:,.2f}</div>
              <div class='wb-lbl'>Winnings Balance</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_dep, col_wdr = st.columns(2)
        with col_dep:
            st.markdown("<div class='section-header'>💳 Add Funds</div>", unsafe_allow_html=True)
            with st.form("deposit_form"):
                amount_dep = st.number_input("Amount (INR)", min_value=10.0, max_value=50000.0, value=100.0, step=50.0)
                dep_desc = st.text_input("Payment Method", value="UPI / GPay / PhonePe")
                if st.form_submit_button("ADD CASH INSTANTLY", use_container_width=True):
                    success, msg = wallet_service.add_funds(db, user_id, amount_dep, dep_desc)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col_wdr:
            st.markdown("<div class='section-header'>🏦 Withdraw</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:0.82rem; color:#6b7280; margin-bottom:12px;'>Withdrawals deducted from winnings balance only</div>", unsafe_allow_html=True)
            with st.form("withdrawal_form"):
                amount_wdr = st.number_input("Withdrawal Amount (INR)", min_value=50.0, max_value=10000.0, value=100.0, step=50.0)
                if st.form_submit_button("WITHDRAW TO BANK", use_container_width=True):
                    success, msg = wallet_service.withdraw_funds(db, user_id, amount_wdr)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("<hr style='border-color:#1f2937; margin:24px 0 20px;' />", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>📋 Transaction History</div>", unsafe_allow_html=True)

        transactions = wallet_service.get_transaction_history(db, user_id)
        if not transactions:
            st.markdown("<div style='color:#6b7280; text-align:center; padding:30px;'>No transactions yet</div>", unsafe_allow_html=True)
        else:
            tx_labels = {
                "deposit": ("💳 Deposit", "#00d4ff"),
                "withdraw": ("🏦 Withdrawal", "#ff2d4b"),
                "entry_fee": ("🎯 Entry Fee", "#ff2d4b"),
                "winnings_payout": ("🏆 Winnings", "#00ff88"),
                "bonus": ("🎁 Bonus", "#f5c518"),
            }
            for tx in transactions:
                label, color = tx_labels.get(tx.transaction_type, (tx.transaction_type, "#9ca3af"))
                is_pos = tx.amount > 0
                date_str = tx.created_at.strftime('%d %b %Y, %I:%M %p')
                st.markdown(f"""
                <div class='tx-row'>
                  <div>
                    <div class='tx-type'>{label}</div>
                    <div class='tx-date'>{tx.description or ""} · {date_str}</div>
                  </div>
                  <div class='{"tx-amount-pos" if is_pos else "tx-amount-neg"}'>
                    {"+" if is_pos else ""}₹{abs(tx.amount):,.2f}
                  </div>
                </div>
                """, unsafe_allow_html=True)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# MY ENTRIES
# ─────────────────────────────────────────────────────────────────────────────
def render_my_entries_page():
    st.markdown("""
    <div class='f11-hero'>
      <div class='f11-hero-subtitle'>My Activity</div>
      <div class='f11-hero-title'>MY TEAMS & CONTESTS</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        user_id = st.session_state.user["id"]
        entries = db.query(ContestEntry).filter(ContestEntry.user_id == user_id).order_by(ContestEntry.created_at.desc()).all()

        if not entries:
            st.markdown("""
            <div class='no-matches'>
              <div class='icon'>🎯</div>
              <div class='title'>No Contest Entries Yet</div>
              <div class='sub'>Browse matches and build your squad to get started</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for entry in entries:
                match = entry.contest.match
                status_clr = {"live": "#ff6b7d", "upcoming": "#f5c518", "completed": "#9ca3af"}.get(match.status, "#9ca3af")
                prize_disp = f"₹{entry.prize_won:,.2f}" if entry.prize_won > 0 else "—"
                prize_clr = "#00ff88" if entry.prize_won > 0 else "#6b7280"
                st.markdown(f"""
                <div style='background:#0d1117; border:1px solid #1f2937; border-radius:12px;
                     padding:16px 20px; margin-bottom:10px;'>
                  <div style='display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;'>
                    <div>
                      <div style='font-family:"Orbitron",monospace; font-weight:700; font-size:0.95rem;
                           color:#f1f5f9; letter-spacing:1px;'>
                        {match.team_a} VS {match.team_b}
                      </div>
                      <div style='font-size:0.8rem; color:#6b7280; margin-top:3px;'>
                        <span style='color:{status_clr}; font-weight:700;'>{match.status.upper()}</span>
                        &nbsp;·&nbsp; {entry.contest.name}
                        &nbsp;·&nbsp; Squad: <b style='color:#f1f5f9;'>{entry.team.name}</b>
                      </div>
                    </div>
                    <div style='display:flex; gap:24px; align-items:center;'>
                      <div style='text-align:center;'>
                        <div style='font-family:"Orbitron",monospace; font-weight:700; color:#00d4ff;'>{entry.points:.1f}</div>
                        <div style='font-size:0.65rem; color:#6b7280; text-transform:uppercase; letter-spacing:1px;'>Points</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-weight:700; color:#9ca3af;'>#{entry.rank if entry.rank else "—"}</div>
                        <div style='font-size:0.65rem; color:#6b7280; text-transform:uppercase; letter-spacing:1px;'>Rank</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-family:"Orbitron",monospace; font-weight:700; color:{prize_clr};'>{prize_disp}</div>
                        <div style='font-size:0.65rem; color:#6b7280; text-transform:uppercase; letter-spacing:1px;'>Won</div>
                      </div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_leaderboard_page():
    st.markdown("""
    <div class='f11-hero'>
      <div class='f11-hero-subtitle'>Hall of Fame</div>
      <div class='f11-hero-title'>LEADERBOARDS</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        completed_matches = db.query(Match).filter(Match.status == "completed").all()
        if not completed_matches:
            st.markdown("""
            <div class='no-matches'>
              <div class='icon'>🏆</div>
              <div class='title'>No Results Yet</div>
              <div class='sub'>Leaderboards appear once matches are completed</div>
            </div>
            """, unsafe_allow_html=True)
            return

        match_options = {m.id: f"{m.team_a} vs {m.team_b} · {m.match_date.strftime('%d %b %Y')}" for m in completed_matches}
        selected_match_id = st.selectbox("Select Match", options=list(match_options.keys()), format_func=lambda x: match_options[x])

        contests = db.query(Contest).filter(Contest.match_id == selected_match_id).all()
        if not contests:
            st.warning("No contests found for this match.")
            return

        contest_options = {c.id: f"{c.name}  (Prize Pool: ₹{c.prize_pool:,.0f})" for c in contests}
        selected_contest_id = st.selectbox("Select Contest", options=list(contest_options.keys()), format_func=lambda x: contest_options[x])

        entries = db.query(ContestEntry).filter(ContestEntry.contest_id == selected_contest_id).order_by(ContestEntry.points.desc()).all()
        if not entries:
            st.info("No entries recorded for this contest.")
            return

        for idx, entry in enumerate(entries):
            rank = idx + 1
            rank_class = f"top{rank}" if rank <= 3 else ""
            rank_display = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"#{rank}"
            prize_clr = "#00ff88" if entry.prize_won > 0 else "#6b7280"
            st.markdown(f"""
            <div class='lb-row'>
              <div class='lb-rank {rank_class}'>{rank_display}</div>
              <div class='lb-user'>
                <div style='font-weight:700;'>@{entry.user.username}</div>
                <div style='font-size:0.78rem; color:#6b7280;'>{entry.team.name}</div>
              </div>
              <div class='lb-pts'>{entry.points:.1f} pts</div>
              <div class='lb-prize' style='color:{prize_clr};'>₹{entry.prize_won:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
def render_analytics_page():
    st.markdown("""
    <div class='f11-hero'>
      <div class='f11-hero-subtitle'>Platform Intelligence</div>
      <div class='f11-hero-title'>ANALYTICS DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        from models.models import User as UserModel
        total_users = db.query(UserModel).count()
        total_matches = db.query(Match).count()
        total_contests = db.query(Contest).count()
        total_entries = db.query(ContestEntry).count()

        st.markdown(f"""
        <div class='stat-grid'>
          <div class='stat-card' style='--accent:#00ff88;'>
            <div class='stat-val' style='color:#00ff88;'>{total_users}</div>
            <div class='stat-lbl'>Total Users</div>
          </div>
          <div class='stat-card' style='--accent:#00d4ff;'>
            <div class='stat-val' style='color:#00d4ff;'>{total_matches}</div>
            <div class='stat-lbl'>Matches</div>
          </div>
          <div class='stat-card' style='--accent:#f5c518;'>
            <div class='stat-val' style='color:#f5c518;'>{total_contests}</div>
            <div class='stat-lbl'>Contests</div>
          </div>
          <div class='stat-card' style='--accent:#ff2d4b;'>
            <div class='stat-val' style='color:#ff6b7d;'>{total_entries}</div>
            <div class='stat-lbl'>Entries</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            matches = db.query(Match).all()
            if matches:
                status_counts = {"upcoming": 0, "live": 0, "completed": 0}
                for m in matches:
                    status_counts[m.status] = status_counts.get(m.status, 0) + 1
                fig = go.Figure(data=[go.Pie(
                    labels=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    hole=0.6,
                    marker_colors=["#f5c518", "#ff2d4b", "#6b7280"]
                )])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9', family='Rajdhani'),
                    title=dict(text="Match Status Distribution", font=dict(color='#f1f5f9')),
                    legend=dict(font=dict(color='#9ca3af')),
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_c2:
            contests = db.query(Contest).all()
            if contests:
                ctype_counts = {}
                for c in contests:
                    ctype_counts[c.contest_type] = ctype_counts.get(c.contest_type, 0) + 1
                fig2 = go.Figure(data=[go.Bar(
                    x=list(ctype_counts.keys()),
                    y=list(ctype_counts.values()),
                    marker_color=["#ff2d4b", "#00d4ff", "#f5c518", "#6b7280"][:len(ctype_counts)]
                )])
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f1f5f9', family='Rajdhani'),
                    title=dict(text="Contests by Type", font=dict(color='#f1f5f9')),
                    xaxis=dict(color='#9ca3af'), yaxis=dict(color='#9ca3af', gridcolor='#1f2937')
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Points distribution
        completed_teams = db.query(FantasyTeam).filter(FantasyTeam.total_points > 0).all()
        if completed_teams:
            scores = [t.total_points for t in completed_teams]
            fig3 = px.histogram(pd.DataFrame({"Points": scores}), x="Points", nbins=15,
                                title="Fantasy Squad Score Distribution",
                                color_discrete_sequence=["#ff2d4b"],
                                template="plotly_dark")
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#f1f5f9', family='Rajdhani'))
            st.plotly_chart(fig3, use_container_width=True)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────────────────────────────────────
def render_admin_panel():
    st.markdown("""
    <div class='f11-hero' style='background:linear-gradient(135deg,#12080f,#1a0d0d);
         border-color:rgba(255,45,75,0.25);'>
      <div class='f11-hero-subtitle' style='color:#ff6b7d;'>⚡ Admin Access</div>
      <div class='f11-hero-title'>CONTROL CENTER</div>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        tab_cr_match, tab_cr_contest, tab_simulate = st.tabs([
            "🏏  SCHEDULE MATCH", "🏆  CREATE CONTEST", "⚡  MATCH SIMULATOR"
        ])

        with tab_cr_match:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            with st.form("create_match_form"):
                col_ma, col_mb = st.columns(2)
                with col_ma:
                    t_a = st.selectbox("Team A", options=["IND", "AUS", "ENG", "PAK", "NZ", "SA", "WI"])
                with col_mb:
                    t_b = st.selectbox("Team B", options=["IND", "AUS", "ENG", "PAK", "NZ", "SA", "WI"])
                match_venue = st.text_input("Match Venue", value="Chidambaram Stadium, Chennai")
                match_dt = st.date_input("Match Date", value=datetime.now() + timedelta(days=5))
                match_tm = st.time_input("Match Time", value=datetime.now().time())
                if st.form_submit_button("CREATE MATCH & SEED ROSTERS", use_container_width=True):
                    if t_a == t_b:
                        st.error("Team A and Team B cannot be the same.")
                    else:
                        full_dt = datetime.combine(match_dt, match_tm)
                        match_service.create_match(db, t_a, t_b, full_dt, match_venue)
                        st.success(f"Match {t_a} vs {t_b} scheduled! 22 players seeded.")

        with tab_cr_contest:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            upcoming_matches = db.query(Match).filter(Match.status == "upcoming").all()
            if not upcoming_matches:
                st.warning("Schedule an upcoming match first.")
            else:
                m_options = {m.id: f"{m.team_a} vs {m.team_b} ({m.venue})" for m in upcoming_matches}
                with st.form("create_contest_form"):
                    sel_match_id = st.selectbox("Select Match", options=list(m_options.keys()), format_func=lambda x: m_options[x])
                    c_name = st.text_input("Contest Title", value="Grand Mega League")
                    c_type = st.selectbox("Contest Format", options=["mega", "h2h", "small", "practice"])
                    c_fee = st.number_input("Entry Fee (INR)", min_value=0.0, max_value=5000.0, value=49.0)
                    c_prize = st.number_input("Total Prize Pool (INR)", min_value=0.0, max_value=100000.0, value=1000.0)
                    c_spots = st.number_input("Total Spots", min_value=2, max_value=10000, value=50)
                    if st.form_submit_button("PUBLISH CONTEST", use_container_width=True):
                        contest_service.create_contest(db, sel_match_id, c_name, c_type, c_fee, c_prize, int(c_spots))
                        st.success(f"Contest '{c_name}' published!")

        with tab_simulate:
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background:rgba(255,45,75,0.06); border:1px solid rgba(255,45,75,0.2);
                 border-radius:10px; padding:14px 18px; margin-bottom:16px; font-size:0.85rem; color:#9ca3af;'>
              Simulating a match generates randomized player stats and automatically calculates
              fantasy points, ranks, and wallet payouts for all contestants.
            </div>
            """, unsafe_allow_html=True)
            upcoming_matches = db.query(Match).filter(Match.status == "upcoming").all()
            if not upcoming_matches:
                st.info("No upcoming matches to simulate.")
            else:
                sim_options = {m.id: f"{m.team_a} vs {m.team_b} ({m.venue})" for m in upcoming_matches}
                selected_sim_id = st.selectbox("Select Match to Resolve", options=list(sim_options.keys()), format_func=lambda x: sim_options[x])
                entries_count = db.query(ContestEntry).join(Contest).filter(Contest.match_id == selected_sim_id).count()
                st.info(f"{entries_count} contest entries registered for this match.")
                if st.button("🔴 RUN MATCH SIMULATION & CALCULATE WINNINGS", use_container_width=True, type="primary"):
                    with st.spinner("Simulating match... calculating player scores and distributing winnings..."):
                        success, message = points_service.simulate_match_and_calculate_points(db, selected_sim_id)
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        render_auth_page()
    else:
        render_sidebar()
        page = st.session_state.current_page
        dispatch = {
            "dashboard":    render_dashboard_page,
            "match_details": render_match_details_page,
            "squad_builder": render_squad_builder_page,
            "join_confirm":  render_join_confirm_page,
            "wallet":        render_wallet_page,
            "my_entries":    render_my_entries_page,
            "leaderboard":   render_leaderboard_page,
            "analytics":     render_analytics_page,
        }
        if page in dispatch:
            dispatch[page]()
        elif page == "admin":
            if st.session_state.user["role"] == "admin":
                render_admin_panel()
            else:
                st.error("Unauthorized: Admin privileges required.")
                navigate_to("dashboard")

if __name__ == "__main__":
    main()
