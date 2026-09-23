from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from components import render_realtime_chart

from src.inference import (
    FEATURES,
    forecast,
    get_device,
)

# Paths
ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT
    / "data"
    / "ETTm1.csv"
)


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="工业时间序列大模型实时推理平台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Global CSS
st.markdown(
    """
    <style>

    /* ======================================================
       Main
       ====================================================== */

    .block-container {
        padding-top: 1.15rem;
        padding-bottom: 1.2rem;
    }

    /* ======================================================
       Sidebar header
       ====================================================== */

    section[data-testid="stSidebar"]
    [data-testid="stSidebarHeader"] {

        position: relative !important;

        height: 3.45rem !important;
        min-height: 3.45rem !important;

        padding:
            0
            0.8rem
            0
            1rem !important;

        display: flex !important;
        align-items: center !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSidebarHeader"]::before {

        content: "推理控制";

        position: absolute;

        left: 1rem;
        top: 50%;

        transform:
            translateY(-50%);

        font-size: 1.28rem;
        font-weight: 700;

        white-space: nowrap;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSidebarCollapseButton"] {

        position: absolute !important;

        right: 0.70rem !important;
        top: 50% !important;

        transform:
            translateY(-50%) !important;

        margin: 0 !important;

        z-index: 9999 !important;
    }

    /* ======================================================
       Remove sidebar top gap
       ====================================================== */

    section[data-testid="stSidebar"]
    [data-testid="stSidebarUserContent"] {

        padding-top: 0 !important;
    }

    /* ======================================================
       Compact sidebar
       ====================================================== */

    section[data-testid="stSidebar"]
    [data-testid="stVerticalBlock"] {

        gap: 0.58rem !important;
    }

    section[data-testid="stSidebar"]
    hr {

        margin:
            0.45rem
            0 !important;
    }

    section[data-testid="stSidebar"]
    .stButton {

        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Dataset
# ============================================================

@st.cache_data
def load_dataset():

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])

    df = (df.sort_values("date").reset_index(drop=True)
    )

    df[FEATURES] = (
        df[FEATURES]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .interpolate()
        .ffill()
        .bfill()
    )
    return df

df = load_dataset()


# Sampling interval
INTERVAL = (
    df["date"]
    .diff()
    .dropna()
    .median()
)

INTERVAL_MS = int(
    INTERVAL.total_seconds()
    * 1000
)


# Constants
DISPLAY_HISTORY = 256

# Front-end playback buffer.
#
# 4000 ETTm1 points ≈ 41.7 days.
STREAM_POINTS = 4000


# Header
st.title("工业时间序列大模型实时推理平台")

st.caption(
    "基于 ETTm1 电力变压器数据模拟实时传感器数据流，"
    "调用 Toto 2.0 / Chronos-2 进行零样本在线预测。"
)


# Session defaults
defaults = {
    "running": False,
    "reset_token": 0,
    "forecast_seq": 0,
    "forecast_packet": None,
    "structural_signature": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Sidebar
with st.sidebar:
    model_name = st.selectbox(
        "基础模型",
        [
            "Toto-2.0-22m",
            "Chronos-2-Small",
        ],
        key="model_name",
    )

    target_name = st.selectbox(
        "预测变量",
        FEATURES,
        index=FEATURES.index("HUFL"),
        key="target_name",
    )

    context_length = (
        st.select_slider(
            "历史上下文长度",
            options=[
                256,
                512,
                1024,
                2048,
            ],
            value=512,
            key="context_length",
        )
    )

    horizon = (
        st.select_slider(
            "预测长度",
            options=[
                24,
                48,
                96,
                192,
            ],
            value=96,
            key="horizon",
        )
    )

    inference_every = (
        st.select_slider(
            "每隔多少个新数据点推理一次",
            options=[
                1,
                2,
                4,
                8,
                16,
                32,
            ],
            value=8,
            key="inference_every",
        )
    )

    playback_speed = (
        st.select_slider(
            "模拟数据流速度",
            options=[
                0.5,
                1.0,
                2.0,
                4.0,
                8.0,
            ],
            value=2.0,
            format_func=(
                lambda value:
                    f"{value:g} 点/秒"
            ),
            key="playback_speed",
        )
    )

    start_pct = st.slider(
        "数据回放起始位置",
        min_value=5,
        max_value=90,
        value=20,
        step=5,
        format="%d%%",
        key="start_pct",
    )
    
    show_future_truth = st.toggle(
        "显示未来真值（演示评估）",
        value=True,
        key="show_future_truth",
    )

    # Controls
    col1, col2, col3 = (
        st.columns(3)
    )

    start_clicked = (
        col1.button(
            "▶ 启动",
            use_container_width=True,
        )
    )

    pause_clicked = (
        col2.button(
            "Ⅱ 暂停",
            use_container_width=True,
        )
    )

    reset_clicked = (
        col3.button(
            "↺ 重置",
            use_container_width=True,
        )
    )

    st.caption(
        (
            f"计算设备：{get_device()}"
            "　｜　"
            "ETTm1：15 min/点"
        )
    )

# Start position
initial_cursor = max(
    context_length,
    int(
        len(df)
        * start_pct
        / 100
    ),
)


# ============================================================
# Structural configuration
#
# Changing these settings resets playback.
#
# Changing speed / inference interval does NOT reset.
# ============================================================

structural_signature = (
    model_name,
    target_name,
    context_length,
    horizon,
    start_pct,
)


if st.session_state.structural_signature != structural_signature:
    st.session_state.structural_signature = structural_signature
    st.session_state.running = False
    st.session_state.reset_token += 1
    st.session_state.forecast_packet = None
    
# Buttons
if start_clicked:
    st.session_state.running = True


if pause_clicked:
    st.session_state.running = False


if reset_clicked:
    st.session_state.running = False
    st.session_state.reset_token += 1
    st.session_state.forecast_packet = None


# Forecast function at an arbitrary online cursor
# Cursor definition:
# df.iloc[:cursor]
# are already observed.
# The first forecast corresponds to:
# df.iloc[cursor]

def make_forecast_packet(cursor: int):
    model_name_now = (
        st.session_state.model_name
    )
    target_name_now = st.session_state.target_name
    context_length_now = int(st.session_state.context_length)
    horizon_now = int(st.session_state.horizon)
    cursor = int(
        np.clip(
            cursor,
            context_length_now,
            len(df) - 1,
        )
    )


    context_start = cursor - context_length_now


    context = (
        df.iloc[
            context_start:
            cursor
        ][FEATURES]
        .to_numpy(
            dtype=np.float32
        )
    )


    # Actual foundation-model inference
    result = forecast(
        model_name=model_name_now,
        context=context,
        horizon=horizon_now,
        target_name=target_name_now
    )

    # Future timestamps
    last_observed_time = df["date"].iloc[cursor - 1]

    forecast_dates = [
        int(
            (
                last_observed_time
                + INTERVAL * (step + 1)
            )
            .timestamp()
            * 1000
        )

        for step in range(
            horizon_now
        )
    ]
    st.session_state.forecast_seq += 1

    return {
        "seq":
            int(
                st.session_state
                .forecast_seq
            ),

        "cursor":
            cursor,

        "dates":
            forecast_dates,

        "q10":
            np.asarray(
                result["q10"],
                dtype=float,
            ).tolist(),

        "q50":
            np.asarray(
                result["q50"],
                dtype=float,
            ).tolist(),

        "q90":
            np.asarray(
                result["q90"],
                dtype=float,
            ).tolist(),

        "latency_ms":
            float(
                result[
                    "latency_ms"
                ]
            ),
    }


# Initial prediction
#
# Only when:
#
# - app first opens
# - model changes
# - target changes
# - context changes
# - horizon changes
# - reset is pressed


if st.session_state.forecast_packet is None:
    with st.spinner(f"正在加载 {model_name} 并生成初始预测..."):
        st.session_state.forecast_packet = make_forecast_packet(initial_cursor)


# ============================================================
# Callback from JavaScript
#
# This runs only when the front-end reaches:
#
# inference_every
#
# new points.
#
# Example:
#
# 2 points/s
# inference_every = 8
#
# Python model inference:
#
# every ≈4 seconds
#
# Browser animation:
#
# ~60 FPS continuously.
# ============================================================

def handle_inference_request():
    component_state = (
        st.session_state.get("realtime_dashboard")
    )

    if component_state is None:
        return

    request = getattr(component_state, "inference_request", None)
    if not request:
        return

    try:
        cursor = int(request["cursor"])
    except (
        TypeError,
        KeyError,
        ValueError,
    ):
        return

    # Safety checks
    cursor = max(
        cursor,
        int(
            st.session_state
            .context_length
        ),
    )

    cursor = min(
        cursor,
        len(df) - 1,
    )

    # Actual model inference.
    st.session_state.forecast_packet = (
        make_forecast_packet(
            cursor
        )
    )


# ============================================================
# Front-end playback segment
#
# Need historical points before initial cursor +
# enough points after it for playback.
# ============================================================

segment_start = max(
    0,
    initial_cursor
    - DISPLAY_HISTORY
    - 32,
)

segment_end = min(
    len(df),
    initial_cursor
    + STREAM_POINTS,
)

segment = df.iloc[
    segment_start:
    segment_end
]


# Browser payload
# All 7 variables are sent for the current playback segment.
# The browser can therefore update the "current device state"
# without asking Python every frame.

timestamps = [
    int(timestamp.timestamp() * 1000)
    for timestamp in (
        segment["date"]
    )
]

series = {
    feature:
        segment[
            feature
        ]
        .astype(float)
        .tolist()
    for feature in FEATURES
}


component_data = {
    "segment_start":segment_start,
    "segment_end":segment_end,
    
    "initial_cursor":initial_cursor,
    "timestamps":timestamps,
    "series":series,
    "features":FEATURES,
    "target_name":target_name,
    "model_name":model_name,
    "history_points":DISPLAY_HISTORY,
    "horizon":horizon,
    "interval_ms":INTERVAL_MS,
    "playback_speed":playback_speed,
    "inference_every":inference_every,
    "show_future_truth":show_future_truth,
    
    "running":st.session_state.running,
    "reset_token":st.session_state.reset_token,
    "forecast":st.session_state.forecast_packet,
}


# Render
# IMPORTANT:
# key stays fixed.
# Therefore Streamlit updates the existing component instead
# of replacing it on each model inference.

render_realtime_chart(
    data=component_data,
    key="realtime_dashboard",
    on_inference_request_change=(
        handle_inference_request
    ),
)

# Footer
st.caption(
    "说明：ETTm1 历史数据按时间顺序回放，"
    "用于模拟工业现场传感器实时数据流。"
    "曲线动画在浏览器端连续运行；"
    "Python 仅在达到设定推理间隔时调用基础模型。"
)