import threading
import time
import math
import xml.etree.ElementTree as ET
from datetime import datetime

import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
import requests
import yfinance as yf

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from google import genai


# =============================================================================
# STOCKSTATS
# CLEAN QUANT TERMINAL UI
# DESIGNED BY LEANDER DLIMA
# =============================================================================


# =============================================================================
# CONFIG
# =============================================================================

GEMINI_API_KEY = "PLEASE_ENTER_YOUR_API_KEY_HERE"


# =============================================================================
# THEME
# =============================================================================

ctk.set_appearance_mode("dark")

BG = "#000000"
CARD = "#080809"
CARD_2 = "#0C0C0F"
CARD_3 = "#111114"

BORDER = "#242428"
BORDER_SOFT = "#18181B"

WHITE = "#FFFFFF"
TEXT = "#E4E4E7"
MUTED = "#71717A"
MUTED_2 = "#52525B"

PURPLE = "#A855F7"
PURPLE_SOFT = "#7C3AED"

BLUE = "#3B82F6"
GREEN = "#30D158"
RED = "#FF453A"
YELLOW = "#FACC15"

FONT_UI = "Helvetica"
FONT_MONO = "Courier"


# =============================================================================
# FEEDS
# =============================================================================

RSS_FEEDS = [
    (
        "CNBC",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"
    ),
    (
        "Yahoo",
        "https://finance.yahoo.com/news/rssindex"
    )
]


# =============================================================================
# HELPERS
# =============================================================================

def make_bar(value, minimum, maximum, width=10):

    if maximum == minimum:
        return "░" * width

    pct = max(
        0,
        min(
            1,
            (value - minimum) / (maximum - minimum)
        )
    )

    filled = int(
        pct * width
    )

    return (
        "█" * filled +
        "░" * (width - filled)
    )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class StockStats(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "StockStats — Leander Dlima"
        )

        self.geometry(
            "1750x1000"
        )

        self.minsize(
            1400,
            820
        )

        self.configure(
            fg_color=BG
        )

        self.is_running = True

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )

        # ---------------------------------------------------------------------
        # GEMINI
        # ---------------------------------------------------------------------

        try:

            self.gemini_client = genai.Client(
                api_key=GEMINI_API_KEY
            )

        except Exception:

            self.gemini_client = None

        # ---------------------------------------------------------------------
        # GRID
        # ---------------------------------------------------------------------

        self.grid_rowconfigure(
            0,
            weight=0
        )

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_columnconfigure(
            1,
            weight=2
        )

        self.grid_columnconfigure(
            2,
            weight=1
        )

        # ---------------------------------------------------------------------
        # BUILD UI
        # ---------------------------------------------------------------------

        self.build_header()
        self.build_left_column()
        self.build_center_column()
        self.build_right_column()

        self.sys_log(
            "StockStats initialized."
        )

        if self.gemini_client:

            self.sys_log(
                "Gemini neural bridge online."
            )

        else:

            self.sys_log(
                "Gemini unavailable."
            )

        threading.Thread(
            target=self.background_worker,
            daemon=True
        ).start()


    # =========================================================================
    # HEADER
    # =========================================================================

    def build_header(self):

        self.header = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER
        )

        self.header.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=16,
            pady=(16, 8)
        )

        # ---------------------------------------------------------------------
        # BRAND
        # ---------------------------------------------------------------------

        left = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        left.pack(
            side="left",
            padx=18,
            pady=12
        )

        ctk.CTkLabel(
            left,
            text="StockStats",
            font=(
                FONT_UI,
                17,
                "bold"
            ),
            text_color=WHITE
        ).pack(
            side="left"
        )

        ctk.CTkLabel(
            left,
            text="  /  LEANDER DLIMA",
            font=(
                FONT_MONO,
                10
            ),
            text_color=MUTED
        ).pack(
            side="left"
        )

        # ---------------------------------------------------------------------
        # CENTER STATUS
        # ---------------------------------------------------------------------

        center = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        center.pack(
            side="left",
            padx=30
        )

        self.market_state = ctk.CTkLabel(
            center,
            text="MARKET DATA  •  LIVE",
            font=(
                FONT_MONO,
                9,
                "bold"
            ),
            text_color=MUTED
        )

        self.market_state.pack()

        # ---------------------------------------------------------------------
        # RIGHT STATUS
        # ---------------------------------------------------------------------

        right = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        right.pack(
            side="right",
            padx=16
        )

        self.status_dot = ctk.CTkLabel(
            right,
            text="●",
            font=(
                FONT_UI,
                13
            ),
            text_color=GREEN
        )

        self.status_dot.pack(
            side="left",
            padx=(0, 5)
        )

        self.status_text = ctk.CTkLabel(
            right,
            text="ONLINE",
            font=(
                FONT_UI,
                11,
                "bold"
            ),
            text_color=GREEN
        )

        self.status_text.pack(
            side="left"
        )


    # =========================================================================
    # CARD CREATION
    # =========================================================================

    def make_card(
        self,
        parent,
        title,
        subtitle=None,
        accent=PURPLE
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            border_width=1,
            border_color=BORDER,
            corner_radius=15
        )

        # Header
        header = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=16,
            pady=(13, 10)
        )

        title_row = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_row.pack(
            fill="x"
        )

        ctk.CTkLabel(
            title_row,
            text=title.upper(),
            font=(
                FONT_UI,
                10,
                "bold"
            ),
            text_color=accent
        ).pack(
            side="left"
        )

        if subtitle:

            ctk.CTkLabel(
                title_row,
                text=subtitle,
                font=(
                    FONT_MONO,
                    8
                ),
                text_color=MUTED_2
            ).pack(
                side="right"
            )

        separator = ctk.CTkFrame(
            header,
            fg_color=BORDER_SOFT,
            height=1
        )

        separator.pack(
            fill="x",
            pady=(9, 0)
        )

        return frame


    # =========================================================================
    # LEFT COLUMN
    # =========================================================================

    def build_left_column(self):

        self.left = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.left.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(8, 0),
            pady=(0, 8)
        )

        self.left.grid_columnconfigure(
            0,
            weight=1
        )

        self.left.grid_rowconfigure(
            0,
            weight=4
        )

        self.left.grid_rowconfigure(
            1,
            weight=3
        )

        self.left.grid_rowconfigure(
            2,
            weight=2
        )

        # ---------------------------------------------------------------------
        # MARKET SNAPSHOT
        # ---------------------------------------------------------------------

        self.snapshot_card = self.make_card(
            self.left,
            "Market Snapshot",
            "CORE ASSETS",
            YELLOW
        )

        self.snapshot_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(8, 4),
            pady=8
        )

        self.snapshot_body = ctk.CTkFrame(
            self.snapshot_card,
            fg_color="transparent"
        )

        self.snapshot_body.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14)
        )

        self.asset_rows = {}

        for index, ticker in enumerate(
            ["SPY", "TLT", "GLD", "BTC"]
        ):

            row = ctk.CTkFrame(
                self.snapshot_body,
                fg_color=CARD_2,
                corner_radius=9
            )

            row.pack(
                fill="x",
                pady=4
            )

            symbol = ctk.CTkLabel(
                row,
                text=ticker,
                width=42,
                font=(
                    FONT_MONO,
                    10,
                    "bold"
                ),
                text_color=WHITE
            )

            symbol.pack(
                side="left",
                padx=(10, 6),
                pady=9
            )

            price = ctk.CTkLabel(
                row,
                text="—",
                font=(
                    FONT_MONO,
                    10
                ),
                text_color=TEXT
            )

            price.pack(
                side="left"
            )

            distance = ctk.CTkLabel(
                row,
                text="—",
                font=(
                    FONT_MONO,
                    9,
                    "bold"
                ),
                text_color=MUTED
            )

            distance.pack(
                side="right",
                padx=10
            )

            self.asset_rows[ticker] = (
                price,
                distance
            )

        # ---------------------------------------------------------------------
        # YIELD CURVE
        # ---------------------------------------------------------------------

        self.yield_card = self.make_card(
            self.left,
            "Yield Curve",
            "10Y — 3M",
            RED
        )

        self.yield_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(8, 4),
            pady=4
        )

        self.yield_chart = ctk.CTkFrame(
            self.yield_card,
            fg_color="transparent"
        )

        self.yield_chart.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 4)
        )

        self.yield_stats = ctk.CTkLabel(
            self.yield_card,
            text="Waiting for yield data...",
            font=(
                FONT_MONO,
                9
            ),
            text_color=MUTED
        )

        self.yield_stats.pack(
            anchor="w",
            padx=16,
            pady=(0, 13)
        )

        # ---------------------------------------------------------------------
        # SYSTEM
        # ---------------------------------------------------------------------

        self.health_card = self.make_card(
            self.left,
            "System Health",
            "TELEMETRY",
            MUTED
        )

        self.health_card.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(8, 4),
            pady=(4, 8)
        )

        self.health_box = ctk.CTkTextbox(
            self.health_card,
            fg_color="transparent",
            border_width=0,
            font=(
                FONT_MONO,
                9
            ),
            text_color=MUTED,
            wrap="word"
        )

        self.health_box.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 12)
        )


    # =========================================================================
    # CENTER COLUMN
    # =========================================================================

    def build_center_column(self):

        self.center = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.center.grid(
            row=1,
            column=1,
            sticky="nsew",
            pady=(0, 8)
        )

        self.center.grid_columnconfigure(
            0,
            weight=1
        )

        self.center.grid_rowconfigure(
            0,
            weight=7
        )

        self.center.grid_rowconfigure(
            1,
            weight=3
        )

        # ---------------------------------------------------------------------
        # MAIN CHART CARD
        # ---------------------------------------------------------------------

        self.chart_card = ctk.CTkFrame(
            self.center,
            fg_color=CARD,
            border_width=1,
            border_color=PURPLE,
            corner_radius=15
        )

        self.chart_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=4,
            pady=8
        )

        # ---------------------------------------------------------------------
        # CHART HEADER
        # ---------------------------------------------------------------------

        chart_header = ctk.CTkFrame(
            self.chart_card,
            fg_color="transparent"
        )

        chart_header.pack(
            fill="x",
            padx=18,
            pady=(14, 5)
        )

        # Left
        chart_title = ctk.CTkFrame(
            chart_header,
            fg_color="transparent"
        )

        chart_title.pack(
            side="left"
        )

        ctk.CTkLabel(
            chart_title,
            text="SPY",
            font=(
                FONT_UI,
                18,
                "bold"
            ),
            text_color=WHITE
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            chart_title,
            text="S&P 500 ETF  •  1 YEAR",
            font=(
                FONT_MONO,
                8
            ),
            text_color=MUTED
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        # Right metrics
        metrics = ctk.CTkFrame(
            chart_header,
            fg_color="transparent"
        )

        metrics.pack(
            side="right"
        )

        self.chart_price = ctk.CTkLabel(
            metrics,
            text="$—",
            font=(
                FONT_MONO,
                16,
                "bold"
            ),
            text_color=WHITE
        )

        self.chart_price.pack(
            side="left",
            padx=12
        )

        self.chart_vs_sma = ctk.CTkLabel(
            metrics,
            text="—",
            font=(
                FONT_MONO,
                9,
                "bold"
            ),
            text_color=GREEN
        )

        self.chart_vs_sma.pack(
            side="left"
        )

        # ---------------------------------------------------------------------
        # CHART
        # ---------------------------------------------------------------------

        self.chart_container = ctk.CTkFrame(
            self.chart_card,
            fg_color="transparent"
        )

        self.chart_container.pack(
            fill="both",
            expand=True,
            padx=7,
            pady=(0, 8)
        )

        # ---------------------------------------------------------------------
        # RISK ENGINE
        # ---------------------------------------------------------------------

        self.risk_card = self.make_card(
            self.center,
            "Algorithmic Risk Engine",
            "AI SUMMARY",
            WHITE
        )

        self.risk_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=4,
            pady=(4, 8)
        )

        self.risk_body = ctk.CTkFrame(
            self.risk_card,
            fg_color="transparent"
        )

        self.risk_body.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 13)
        )

        # Metrics row
        metric_container = ctk.CTkFrame(
            self.risk_body,
            fg_color="transparent"
        )

        metric_container.pack(
            fill="x"
        )

        self.risk_metrics = {}

        for label in [
            "DRAWDOWN",
            "VOLATILITY",
            "SHARPE",
            "200D DISTANCE"
        ]:

            block = ctk.CTkFrame(
                metric_container,
                fg_color=CARD_2,
                corner_radius=8
            )

            block.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )

            ctk.CTkLabel(
                block,
                text=label,
                font=(
                    FONT_MONO,
                    7
                ),
                text_color=MUTED
            ).pack(
                anchor="w",
                padx=9,
                pady=(8, 1)
            )

            value = ctk.CTkLabel(
                block,
                text="—",
                font=(
                    FONT_MONO,
                    11,
                    "bold"
                ),
                text_color=WHITE
            )

            value.pack(
                anchor="w",
                padx=9,
                pady=(0, 8)
            )

            self.risk_metrics[label] = value

        # AI directive
        self.directive = ctk.CTkLabel(
            self.risk_body,
            text="Waiting for analysis...",
            font=(
                FONT_MONO,
                10
            ),
            text_color=WHITE,
            justify="left",
            anchor="w"
        )

        self.directive.pack(
            fill="x",
            pady=(12, 0)
        )


    # =========================================================================
    # RIGHT COLUMN
    # =========================================================================

    def build_right_column(self):

        self.right = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.right.grid(
            row=1,
            column=2,
            sticky="nsew",
            padx=(0, 8),
            pady=(0, 8)
        )

        self.right.grid_columnconfigure(
            0,
            weight=1
        )

        self.right.grid_rowconfigure(
            0,
            weight=5
        )

        self.right.grid_rowconfigure(
            1,
            weight=3
        )

        self.right.grid_rowconfigure(
            2,
            weight=2
        )

        # ---------------------------------------------------------------------
        # AI FILTER
        # ---------------------------------------------------------------------

        self.ai_card = self.make_card(
            self.right,
            "Gemini Neural Filter",
            "LIVE FEED",
            PURPLE
        )

        self.ai_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(4, 8),
            pady=8
        )

        self.ai_box = ctk.CTkTextbox(
            self.ai_card,
            fg_color="transparent",
            border_width=0,
            font=(
                FONT_MONO,
                9
            ),
            text_color=TEXT,
            wrap="word"
        )

        self.ai_box.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 12)
        )

        # ---------------------------------------------------------------------
        # NEWS
        # ---------------------------------------------------------------------

        self.news_card = self.make_card(
            self.right,
            "Market Intelligence",
            "HEADLINES",
            BLUE
        )

        self.news_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(4, 8),
            pady=4
        )

        self.news_box = ctk.CTkTextbox(
            self.news_card,
            fg_color="transparent",
            border_width=0,
            font=(
                FONT_MONO,
                8
            ),
            text_color=MUTED,
            wrap="word"
        )

        self.news_box.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 12)
        )

        # ---------------------------------------------------------------------
        # TELEMETRY
        # ---------------------------------------------------------------------

        self.telemetry_card = self.make_card(
            self.right,
            "System Telemetry",
            "EVENT STREAM",
            MUTED
        )

        self.telemetry_card.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(4, 8),
            pady=(4, 8)
        )

        self.telemetry_box = ctk.CTkTextbox(
            self.telemetry_card,
            fg_color="transparent",
            border_width=0,
            font=(
                FONT_MONO,
                8
            ),
            text_color=MUTED,
            wrap="word"
        )

        self.telemetry_box.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 10)
        )


    # =========================================================================
    # LOGGING
    # =========================================================================

    def sys_log(self, message):

        if not self.is_running:
            return

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        line = (
            f"[{timestamp}] {message}\n"
        )

        def update():

            try:

                self.telemetry_box.insert(
                    "end",
                    line
                )

                self.telemetry_box.see(
                    "end"
                )

            except Exception:
                pass

        self.after(
            0,
            update
        )


    # =========================================================================
    # RSS
    # =========================================================================

    def fetch_rss(self):

        articles = []

        try:

            for source, url in RSS_FEEDS:

                response = requests.get(
                    url,
                    headers={
                        "User-Agent":
                        "Mozilla/5.0"
                    },
                    timeout=5
                )

                if response.status_code != 200:
                    continue

                root = ET.fromstring(
                    response.content
                )

                items = root.findall(
                    "./channel/item"
                )[:5]

                for item in items:

                    node = item.find(
                        "title"
                    )

                    if (
                        node is not None
                        and
                        node.text
                    ):

                        articles.append({
                            "source": source,
                            "title":
                                node.text.strip()
                        })

        except Exception as exc:

            self.sys_log(
                f"RSS ERR: {exc}"
            )

        return articles[:8]


    # =========================================================================
    # GEMINI
    # =========================================================================

    def get_ai_analysis(
        self,
        headlines,
        drawdown,
        volatility,
        sharpe,
        price,
        sma200
    ):

        if not self.gemini_client:

            return (
                ">> DIRECTIVE: HOLD CORE / AVOID CHASING\n\n"
                "TACTICAL: Trend remains constructive above the 200D average.\n\n"
                "RISK: Monitor volatility expansion and breaks below trend support.\n\n"
                "BIAS: Positive, but avoid adding exposure purely on momentum."
            )

        headline_text = ""

        for i, item in enumerate(
            headlines
        ):

            headline_text += (
                f"{i+1}. "
                f"[{item['source']}] "
                f"{item['title']}\n"
            )

        prompt = f"""
You are an internal quantitative risk engine.

SPY:
Price: ${price:.2f}
200D SMA: ${sma200:.2f}
Distance from 200D SMA: {((price - sma200) / sma200) * 100:.2f}%
Current drawdown: {drawdown:.2f}%
Annualized volatility: {volatility:.2f}%
Sharpe proxy: {sharpe:.2f}

News:
{headline_text}

Return ONLY this format:

>> DIRECTIVE: [maximum 10 words]

TACTICAL: [maximum 18 words]

RISK: [maximum 18 words]

BIAS: [maximum 18 words]

Rules:
- Sound like a quantitative terminal.
- No motivational language.
- No corporate jargon.
- No "secular bull trend".
- No generic Warren Buffett language.
- Do not repeat numbers unnecessarily.
- Do not invent facts.
- Be concise and decisive.
"""

        try:

            response = (
                self.gemini_client
                .models
                .generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
            )

            return response.text.strip()

        except Exception as exc:

            self.sys_log(
                f"Gemini ERR: {exc}"
            )

            return (
                ">> DIRECTIVE: HOLD CORE / AVOID CHASING\n\n"
                "TACTICAL: Trend data remains constructive.\n\n"
                "RISK: Await further market confirmation.\n\n"
                "BIAS: Neutral-positive."
            )


    # =========================================================================
    # MAIN WORKER
    # =========================================================================

    def background_worker(self):

        last_market_fetch = 0
        last_ai_fetch = 0

        cache = {}

        tickers = [
            "SPY",
            "TLT",
            "GLD",
            "BTC-USD",
            "^VIX",
            "^TNX",
            "^IRX"
        ]

        while self.is_running:

            now = time.time()

            # -----------------------------------------------------------------
            # FETCH MARKET DATA
            # -----------------------------------------------------------------

            if now - last_market_fetch > 60:

                self.sys_log(
                    "Syncing market telemetry..."
                )

                try:

                    data = yf.download(
                        tickers,
                        period="1y",
                        interval="1d",
                        progress=False,
                        auto_adjust=False
                    )["Close"]

                    for ticker in tickers:

                        if ticker in data.columns:

                            series = (
                                data[ticker]
                                .dropna()
                            )

                            if not series.empty:

                                cache[ticker] = series

                    last_market_fetch = now

                    self.sys_log(
                        "Market feed updated."
                    )

                except Exception as exc:

                    self.sys_log(
                        f"MARKET ERR: {exc}"
                    )

            # -----------------------------------------------------------------
            # PROCESS
            # -----------------------------------------------------------------

            if (
                cache
                and
                "SPY" in cache
                and
                self.is_running
            ):

                try:

                    spy = cache["SPY"]

                    sma50 = (
                        spy
                        .rolling(50)
                        .mean()
                    )

                    sma200 = (
                        spy
                        .rolling(200)
                        .mean()
                    )

                    price = float(
                        spy.iloc[-1]
                    )

                    sma200_value = float(
                        sma200.iloc[-1]
                    )

                    # Proper current drawdown
                    peak = (
                        spy.cummax()
                    )

                    drawdown_series = (
                        (spy - peak)
                        /
                        peak
                        *
                        100
                    )

                    drawdown = float(
                        drawdown_series.iloc[-1]
                    )

                    volatility = float(
                        spy
                        .pct_change()
                        .dropna()
                        .std()
                        *
                        math.sqrt(252)
                        *
                        100
                    )

                    annual_return = (
                        (
                            price -
                            spy.iloc[0]
                        )
                        /
                        spy.iloc[0]
                        *
                        100
                    )

                    sharpe = (
                        (annual_return - 4)
                        /
                        volatility
                        if volatility
                        else 0
                    )

                    sma_distance = (
                        (
                            price -
                            sma200_value
                        )
                        /
                        sma200_value
                        *
                        100
                    )

                    # =========================================================
                    # AI
                    # =========================================================

                    headlines = []

                    if (
                        now - last_ai_fetch > 600
                        or
                        last_ai_fetch == 0
                    ):

                        headlines = (
                            self.fetch_rss()
                        )

                        if headlines:

                            self.sys_log(
                                "Running Gemini risk engine..."
                            )

                            ai_text = (
                                self.get_ai_analysis(
                                    headlines,
                                    drawdown,
                                    volatility,
                                    sharpe,
                                    price,
                                    sma200_value
                                )
                            )

                            last_ai_fetch = now

                        else:

                            ai_text = (
                                "Waiting for market intelligence..."
                            )

                    else:

                        ai_text = (
                            self.get_cached_ai_text()
                        )

                    # Save AI text
                    self.cached_ai_text = ai_text

                    # =========================================================
                    # RENDER
                    # =========================================================

                    self.after(
                        0,
                        self.render_dashboard,
                        cache,
                        spy,
                        sma50,
                        sma200,
                        price,
                        sma_distance,
                        drawdown,
                        volatility,
                        sharpe,
                        ai_text,
                        headlines
                    )

                except Exception as exc:

                    self.sys_log(
                        f"PROCESS ERR: {exc}"
                    )

            for _ in range(5):

                if not self.is_running:
                    break

                time.sleep(1)


    # =========================================================================
    # CACHE AI
    # =========================================================================

    def get_cached_ai_text(self):

        if hasattr(
            self,
            "cached_ai_text"
        ):

            return (
                self.cached_ai_text
            )

        return (
            "Waiting for next AI cycle..."
        )


    # =========================================================================
    # DASHBOARD RENDER
    # =========================================================================

    def render_dashboard(
        self,
        cache,
        spy,
        sma50,
        sma200,
        price,
        sma_distance,
        drawdown,
        volatility,
        sharpe,
        ai_text,
        headlines
    ):

        if not self.is_running:
            return

        # ---------------------------------------------------------------------
        # MARKET STATUS
        # ---------------------------------------------------------------------

        self.market_state.configure(
            text="MARKET DATA  •  LIVE"
        )

        # ---------------------------------------------------------------------
        # SNAPSHOT
        # ---------------------------------------------------------------------

        mapping = {
            "SPY": "SPY",
            "TLT": "TLT",
            "GLD": "GLD",
            "BTC": "BTC-USD"
        }

        for symbol, ticker in mapping.items():

            if ticker not in cache:
                continue

            series = cache[ticker]

            current = float(
                series.iloc[-1]
            )

            average = (
                series
                .rolling(200)
                .mean()
                .iloc[-1]
            )

            if pd.isna(
                average
            ):

                distance = 0

            else:

                distance = (
                    (
                        current -
                        average
                    )
                    /
                    average
                    *
                    100
                )

            price_label, distance_label = (
                self.asset_rows[symbol]
            )

            price_label.configure(
                text=f"${current:,.2f}"
            )

            distance_label.configure(
                text=f"{distance:+.1f}%"
            )

            distance_label.configure(
                text_color=(
                    GREEN
                    if distance >= 0
                    else RED
                )
            )

        # ---------------------------------------------------------------------
        # RISK METRICS
        # ---------------------------------------------------------------------

        self.risk_metrics[
            "DRAWDOWN"
        ].configure(
            text=f"{drawdown:+.2f}%"
        )

        self.risk_metrics[
            "VOLATILITY"
        ].configure(
            text=f"{volatility:.2f}%"
        )

        self.risk_metrics[
            "SHARPE"
        ].configure(
            text=f"{sharpe:.2f}"
        )

        self.risk_metrics[
            "200D DISTANCE"
        ].configure(
            text=f"{sma_distance:+.1f}%"
        )

        self.risk_metrics[
            "DRAWDOWN"
        ].configure(
            text_color=(
                RED
                if drawdown < -5
                else WHITE
            )
        )

        self.risk_metrics[
            "200D DISTANCE"
        ].configure(
            text_color=(
                GREEN
                if sma_distance >= 0
                else RED
            )
        )

        # ---------------------------------------------------------------------
        # DIRECTIVE
        # ---------------------------------------------------------------------

        self.directive.configure(
            text=ai_text
        )

        # ---------------------------------------------------------------------
        # AI FEED
        # ---------------------------------------------------------------------

        self.ai_box.delete(
            "0.0",
            "end"
        )

        self.ai_box.insert(
            "0.0",
            ai_text
        )

        # ---------------------------------------------------------------------
        # NEWS
        # ---------------------------------------------------------------------

        self.news_box.delete(
            "0.0",
            "end"
        )

        if headlines:

            lines = []

            for index, item in enumerate(
                headlines[:8]
            ):

                lines.append(
                    f"{index + 1:02d}  "
                    f"{item['title']}\n"
                )

            self.news_box.insert(
                "0.0",
                "\n".join(lines)
            )

        else:

            self.news_box.insert(
                "0.0",
                "No fresh headlines."
            )

        # ---------------------------------------------------------------------
        # HEALTH
        # ---------------------------------------------------------------------

        health = (
            "DATA FEED     ONLINE\n"
            "YFINANCE      CONNECTED\n"
            "GEMINI        "
            +
            (
                "CONNECTED\n"
                if self.gemini_client
                else "OFFLINE\n"
            )
            +
            "\n"
            "SYNC INTERVAL 60s\n"
            "AI INTERVAL   10m\n"
            "ENGINE        ACTIVE"
        )

        self.health_box.delete(
            "0.0",
            "end"
        )

        self.health_box.insert(
            "0.0",
            health
        )

        # ---------------------------------------------------------------------
        # YIELD CHART
        # ---------------------------------------------------------------------

        self.render_yield_chart(
            cache
        )

        # ---------------------------------------------------------------------
        # MAIN CHART
        # ---------------------------------------------------------------------

        self.render_main_chart(
            spy,
            sma50,
            sma200
        )


    # =========================================================================
    # YIELD CHART
    # =========================================================================

    def render_yield_chart(
        self,
        cache
    ):

        if (
            "^TNX" not in cache
            or
            "^IRX" not in cache
        ):
            return

        for child in (
            self.yield_chart
            .winfo_children()
        ):

            child.destroy()

        spread = (
            cache["^TNX"] -
            cache["^IRX"]
        ).tail(60)

        fig, ax = plt.subplots(
            figsize=(4.3, 1.7),
            facecolor=CARD
        )

        ax.set_facecolor(
            CARD
        )

        ax.plot(
            spread.index,
            spread.values,
            color=RED,
            linewidth=2
        )

        ax.fill_between(
            spread.index,
            spread.values,
            0,
            color=RED,
            alpha=0.10
        )

        ax.axhline(
            0,
            color=MUTED_2,
            linewidth=1,
            linestyle="--"
        )

        ax.axis(
            "off"
        )

        fig.tight_layout(
            pad=0
        )

        canvas = FigureCanvasTkAgg(
            fig,
            master=self.yield_chart
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        current_spread = (
            float(spread.iloc[-1])
        )

        self.yield_stats.configure(
            text=(
                f"10Y — 3M  "
                f"{current_spread:+.2f}%     "
                +
                (
                    "NORMAL"
                    if current_spread >= 0
                    else "INVERTED"
                )
            ),
            text_color=(
                GREEN
                if current_spread >= 0
                else RED
            )
        )

        plt.close(
            fig
        )


    # =========================================================================
    # MAIN SPY CHART
    # =========================================================================

    def render_main_chart(
        self,
        spy,
        sma50,
        sma200
    ):

        for child in (
            self.chart_container
            .winfo_children()
        ):

            child.destroy()

        visible = spy.tail(
            min(
                252,
                len(spy)
            )
        )

        sma50_visible = (
            sma50
            .reindex(
                visible.index
            )
        )

        sma200_visible = (
            sma200
            .reindex(
                visible.index
            )
        )

        current = float(
            visible.iloc[-1]
        )

        current_sma = float(
            sma200_visible.iloc[-1]
        )

        distance = (
            (
                current -
                current_sma
            )
            /
            current_sma
            *
            100
        )

        self.chart_price.configure(
            text=f"${current:,.2f}"
        )

        self.chart_vs_sma.configure(
            text=(
                f"{distance:+.1f}% vs 200D"
            ),
            text_color=(
                GREEN
                if distance >= 0
                else RED
            )
        )

        # ---------------------------------------------------------------------
        # FIGURE
        # ---------------------------------------------------------------------

        fig, ax = plt.subplots(
            figsize=(8, 5),
            facecolor=CARD
        )

        ax.set_facecolor(
            CARD
        )

        low = float(
            visible.min()
        )

        high = float(
            visible.max()
        )

        padding = (
            high - low
        ) * 0.08

        if padding <= 0:
            padding = 10

        # ---------------------------------------------------------------------
        # SUBTLE GLOW
        # ---------------------------------------------------------------------

        ax.plot(
            visible.index,
            visible.values,
            color=PURPLE,
            linewidth=8,
            alpha=0.035,
            zorder=1
        )

        # ---------------------------------------------------------------------
        # PRICE
        # ---------------------------------------------------------------------

        ax.plot(
            visible.index,
            visible.values,
            color=PURPLE,
            linewidth=2.6,
            solid_capstyle="round",
            zorder=4
        )

        # ---------------------------------------------------------------------
        # AREA
        # ---------------------------------------------------------------------

        ax.fill_between(
            visible.index,
            visible.values,
            low - padding,
            color=PURPLE,
            alpha=0.055,
            zorder=1
        )

        # ---------------------------------------------------------------------
        # SMA
        # ---------------------------------------------------------------------

        ax.plot(
            visible.index,
            sma50_visible.values,
            color=YELLOW,
            linewidth=1.0,
            linestyle=":",
            alpha=0.9
        )

        ax.plot(
            visible.index,
            sma200_visible.values,
            color=RED,
            linewidth=1.2,
            linestyle="--",
            alpha=0.9
        )

        # ---------------------------------------------------------------------
        # LAST POINT
        # ---------------------------------------------------------------------

        ax.scatter(
            [visible.index[-1]],
            [visible.iloc[-1]],
            s=32,
            color=WHITE,
            edgecolor=PURPLE,
            linewidth=2,
            zorder=8
        )

        # ---------------------------------------------------------------------
        # CURRENT PRICE LINE
        # ---------------------------------------------------------------------

        ax.axhline(
            current,
            color=WHITE,
            linewidth=0.6,
            linestyle="--",
            alpha=0.12
        )

        # ---------------------------------------------------------------------
        # AXES
        # ---------------------------------------------------------------------

        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(
                lambda value, pos:
                f"${value:,.0f}"
            )
        )

        ax.xaxis.set_major_locator(
            mdates.MonthLocator(
                interval=1
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%b"
            )
        )

        ax.grid(
            color=BORDER,
            linewidth=0.65,
            alpha=0.30
        )

        ax.set_axisbelow(
            True
        )

        ax.set_ylim(
            low - padding,
            high + padding
        )

        for spine in (
            "top",
            "right",
            "left",
            "bottom"
        ):

            ax.spines[
                spine
            ].set_visible(False)

        ax.tick_params(
            colors=MUTED,
            labelsize=8,
            length=0,
            pad=6
        )

        # ---------------------------------------------------------------------
        # LEGEND
        # ---------------------------------------------------------------------

        ax.plot(
            [],
            [],
            color=PURPLE,
            linewidth=2.5,
            label="SPY"
        )

        ax.plot(
            [],
            [],
            color=YELLOW,
            linewidth=1,
            linestyle=":",
            label="50D SMA"
        )

        ax.plot(
            [],
            [],
            color=RED,
            linewidth=1.2,
            linestyle="--",
            label="200D SMA"
        )

        legend = ax.legend(
            loc="upper right",
            frameon=False,
            ncol=3,
            prop={
                "family": FONT_MONO,
                "size": 8
            },
            handlelength=2
        )

        for text in (
            legend.get_texts()
        ):

            text.set_color(
                WHITE
            )

        fig.tight_layout(
            pad=1.1
        )

        canvas = FigureCanvasTkAgg(
            fig,
            master=self.chart_container
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        plt.close(
            fig
        )


    # =========================================================================
    # CLOSE
    # =========================================================================

    def on_closing(self):

        self.is_running = False

        try:
            self.destroy()
        except Exception:
            pass


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    app = StockStats()

    app.mainloop()
