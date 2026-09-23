from functools import lru_cache
from pathlib import Path
import time

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]

TOTO_PATH = ROOT / "models" / "Toto-2.0-22m"
CHRONOS_PATH = ROOT / "models" / "Chronos-2-Small"


# ETTm1 variables

FEATURES = [
    "HUFL",
    "HULL",
    "MUFL",
    "MULL",
    "LUFL",
    "LULL",
    "OT",
]

def get_device() -> torch.device:
    return torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )


# ============================================================
# Model loader
#
# lru_cache:
# 模型只加载一次，不会因为 Streamlit rerun 反复加载。
# ============================================================

@lru_cache(maxsize=2)
def load_model(model_name: str):

    device = get_device()

    # --------------------------------------------------------
    # Toto 2.0
    if model_name == "Toto-2.0-22m":
        from toto2 import Toto2Model
        if not TOTO_PATH.exists():
            raise FileNotFoundError(
                f"Toto model not found: {TOTO_PATH}"
            )
        print(f"[Model] Loading Toto from {TOTO_PATH}")
        model = Toto2Model.from_pretrained(str(TOTO_PATH))

        model = model.to(device)
        model.eval()

        print(f"[Model] Toto loaded on {device}")
        return {
            "type": "toto",
            "model": model,
            "device": device,
        }

    # Chronos-2
    if model_name == "Chronos-2-Small":
        from chronos import Chronos2Pipeline
        if not CHRONOS_PATH.exists():
            raise FileNotFoundError(
                f"Chronos model not found: "
                f"{CHRONOS_PATH}"
            )
        print(
            f"[Model] Loading Chronos from "
            f"{CHRONOS_PATH}"
        )
        pipeline = (
            Chronos2Pipeline.from_pretrained(
                str(CHRONOS_PATH),
                device_map=(
                    "cuda"
                    if device.type == "cuda"
                    else "cpu"
                ),
                torch_dtype=torch.float32,
            )
        )

        print(f"[Model] Chronos loaded on {device}")

        return {
            "type": "chronos",
            "model": pipeline,
            "device": device,
        }

    raise ValueError(f"Unsupported model: {model_name}")


# Toto forecast
def _forecast_toto(
    backend,
    context: np.ndarray,
    horizon: int,
    target_idx: int,
):

    model = backend["model"]
    device = backend["device"]

    context = np.asarray(
        context,
        dtype=np.float32,
    )

    x = context.T[None, :, :]
    valid_mask = np.isfinite(x)

    x = np.nan_to_num(
        x,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )
    target = torch.from_numpy(x).to(device)

    target_mask = torch.from_numpy(valid_mask).to(device)

    batch_size = target.shape[0]
    n_variates = target.shape[1]

    # All variables belong to one multivariate series.
    series_ids = torch.zeros(
        (batch_size, n_variates),
        dtype=torch.long,
        device=device,
    )

    has_missing_values = not bool(
        target_mask.all().item()
    )

    if device.type == "cuda":
        torch.cuda.synchronize()

    start_time = time.perf_counter()

    with torch.inference_mode():
        quantiles = model.forecast(
            {
                "target": target,
                "target_mask": target_mask,
                "series_ids": series_ids,
            },
            horizon=horizon,

            # Short-horizon prediction:
            # one forward pass.
            decode_block_size=None,

            has_missing_values=(
                has_missing_values
            ),
        )

    if device.type == "cuda":
        torch.cuda.synchronize()

    latency_ms = (
        time.perf_counter()
        - start_time
    ) * 1000.0

    # Toto output:
    #
    # (9, B, C, H)
    #
    # q0 -> 0.1
    # q4 -> 0.5
    # q8 -> 0.9

    q = (
        quantiles[
            :,
            0,
            target_idx,
            :
        ]
        .float()
        .cpu()
        .numpy()
    )

    return {
        "q10": q[0],
        "q50": q[4],
        "q90": q[8],
        "latency_ms": latency_ms,
    }


# Chronos-2 forecast
def _forecast_chronos(
    backend,
    context: np.ndarray,
    horizon: int,
    target_idx: int,
):
    pipeline = backend["model"]
    device = backend["device"]

    context = np.asarray(
        context,
        dtype=np.float32,
    )

    context = np.nan_to_num(
        context,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    # --------------------------------------------------------
    # Chronos-2 input
    #
    # (B, C, T)
    # --------------------------------------------------------

    x = context.T[None, :, :]

    if device.type == "cuda":
        torch.cuda.synchronize()

    start_time = time.perf_counter()

    quantiles, _ = (
        pipeline.predict_quantiles(
            x,
            prediction_length=horizon,
            quantile_levels=[
                0.1,
                0.5,
                0.9,
            ],
        )
    )

    if device.type == "cuda":
        torch.cuda.synchronize()

    latency_ms = (
        time.perf_counter() - start_time
    ) * 1000.0

    # Chronos-2:
    #
    # quantiles[0]:
    #
    # (C, H, 3)

    q = (
        quantiles[0][target_idx]
        .float()
        .cpu()
        .numpy()
    )

    return {
        "q10": q[:, 0],
        "q50": q[:, 1],
        "q90": q[:, 2],
        "latency_ms": latency_ms,
    }


# Unified API
def forecast(
    model_name: str,
    context: np.ndarray,
    horizon: int,
    target_name: str,
):
    if target_name not in FEATURES:
        raise ValueError(f"Unknown target: {target_name}")

    target_idx = FEATURES.index(target_name)

    backend = load_model(model_name)

    if backend["type"] == "toto":
        return _forecast_toto(
            backend,
            context,
            horizon,
            target_idx,
        )

    if backend["type"] == "chronos":
        return _forecast_chronos(
            backend,
            context,
            horizon,
            target_idx,
        )

    raise RuntimeError("Unknown backend.")