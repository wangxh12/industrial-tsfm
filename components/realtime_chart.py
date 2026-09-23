import streamlit as st


# ============================================================
# HTML
# ============================================================

HTML = """
<div class="dashboard-root">

    <div class="metric-grid">

        <div class="metric-card">
            <div class="metric-label">模拟时间</div>
            <div class="metric-value" id="metric-time">-</div>
        </div>

        <div class="metric-card">
            <div class="metric-label" id="metric-value-label">
                当前值
            </div>
            <div class="metric-value" id="metric-value">-</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">运行模型</div>
            <div class="metric-value metric-model" id="metric-model">
                -
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-label">最近推理延迟</div>
            <div class="metric-value" id="metric-latency">-</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">在线验证 MAE</div>
            <div class="metric-value" id="metric-mae">-</div>
        </div>

    </div>


    <div class="status-row">

        <div class="status-left">

            <span
                class="status-dot"
                id="status-dot">
            </span>

            <span id="status-text">
                已暂停
            </span>

            <span class="status-separator">|</span>

            <span id="position-text">
                -
            </span>

        </div>

        <div id="inference-status">
        </div>

    </div>


    <div class="chart-card">

        <div class="chart-title-row">

            <div
                class="chart-title"
                id="chart-title">
                实时监测与未来预测
            </div>

        </div>

        <canvas id="rt-canvas"></canvas>

        <div class="legend">

            <div class="legend-item">
                <span class="legend-line actual"></span>
                实时观测值
            </div>

            <div class="legend-item">
                <span class="legend-line median"></span>
                P50 预测
            </div>

            <div class="legend-item">
                <span class="legend-block band"></span>
                P10–P90 预测区间
            </div>
            
            <div class="legend-item">
                <span class="legend-line truth"></span>
                未来真值
            </div>

            <div class="legend-item">
                <span class="legend-line now"></span>
                当前时刻
            </div>

        </div>

    </div>


    <div class="state-section">

        <div class="state-title">
            当前设备多变量状态
        </div>

        <div
            class="state-grid"
            id="state-grid">
        </div>

    </div>

</div>
"""


# ============================================================
# CSS
# ============================================================

CSS = """
* {
    box-sizing: border-box;
}

.dashboard-root {
    width: 100%;
    height: 100%;

    font-family:
        var(--st-font),
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    color: var(--st-text-color);
}


/* ==========================================================
   Metrics
   ========================================================== */

.metric-grid {
    display: grid;

    grid-template-columns:
        repeat(5, minmax(0, 1fr));

    gap: 12px;

    margin-bottom: 12px;
}

.metric-card {
    min-width: 0;

    padding: 12px 14px;

    border:
        1px solid
        color-mix(
            in srgb,
            var(--st-text-color) 13%,
            transparent
        );

    border-radius: 10px;

    background:
        var(--st-background-color);
}

.metric-label {
    font-size: 13px;

    opacity: 0.70;

    margin-bottom: 5px;
}

.metric-value {
    font-size: 23px;
    font-weight: 500;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.metric-model {
    font-size: 20px;
}


/* ==========================================================
   Status
   ========================================================== */

.status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;

    min-height: 28px;

    padding: 0 3px;

    margin-bottom: 8px;

    font-size: 13px;

    opacity: 0.78;
}

.status-left {
    display: flex;
    align-items: center;

    gap: 7px;
}

.status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #9ca3af;
}

.status-dot.running {
    background: #22c55e;

    box-shadow:
        0 0 0 3px
        rgba(34, 197, 94, 0.13);
}

.status-separator {
    opacity: 0.45;
}

#inference-status {
    min-width: 120px;

    text-align: right;
}


/* ==========================================================
   Chart
   ========================================================== */

.chart-card {
    width: 100%;

    padding: 13px 14px 8px 14px;

    border:
        1px solid
        color-mix(
            in srgb,
            var(--st-text-color) 11%,
            transparent
        );

    border-radius: 11px;

    background:
        var(--st-background-color);
}

.chart-title-row {
    display: flex;

    justify-content: space-between;
    align-items: center;

    margin-bottom: 5px;
}

.chart-title {
    font-size: 15px;
    font-weight: 650;
}

.chart-hint {
    font-size: 12px;
    opacity: 0.52;
}

#rt-canvas {
    display: block;

    width: 100%;
    height: 390px;

    border-radius: 5px;
}


/* ==========================================================
   Legend
   ========================================================== */

.legend {
    display: flex;

    align-items: center;

    gap: 20px;

    height: 27px;

    padding-left: 45px;

    font-size: 12px;

    opacity: 0.78;
}

.legend-item {
    display: flex;

    align-items: center;

    gap: 6px;
}

.legend-line {
    width: 22px;
    height: 0;

    border-top: 2px solid;
}

.legend-line.actual {
    border-color: #2563eb;
}

.legend-line.median {
    border-color: #ef4444;
}

.legend-line.truth {
    border-color: #16a34a;
    border-top-style: dashed;
}

.legend-line.now {
    border-color: #64748b;

    border-top-style: dashed;
}

.legend-block {
    width: 22px;
    height: 9px;

    border-radius: 2px;
}

.legend-block.band {
    background: rgba(239, 68, 68, 0.22);
}


/* ==========================================================
   Variable state
   ========================================================== */

.state-section {
    margin-top: 14px;
}

.state-title {
    font-size: 17px;
    font-weight: 650;

    margin-bottom: 9px;
}

.state-grid {
    display: grid;

    grid-template-columns:
        repeat(7, minmax(0, 1fr));

    gap: 8px;
}

.state-item {
    padding: 8px 10px;

    border:
        1px solid
        color-mix(
            in srgb,
            var(--st-text-color) 11%,
            transparent
        );

    border-radius: 8px;
}

.state-name {
    font-size: 11px;
    opacity: 0.60;

    margin-bottom: 2px;
}

.state-value {
    font-size: 15px;
    font-weight: 550;
}


/* ==========================================================
   Responsive
   ========================================================== */

@media (max-width: 1000px) {

    .metric-grid {
        grid-template-columns:
            repeat(3, minmax(0, 1fr));
    }

    .state-grid {
        grid-template-columns:
            repeat(4, minmax(0, 1fr));
    }
}
"""


# ============================================================
# JavaScript
# ============================================================

JS = r"""
export default function({
    parentElement,
    data,
    setTriggerValue
}) {

    const root =
        parentElement.querySelector(
            ".dashboard-root"
        );

    const canvas =
        parentElement.querySelector(
            "#rt-canvas"
        );

    const ctx =
        canvas.getContext("2d");


    // ========================================================
    // Helper functions
    // ========================================================

    function rootConnected() {

        if (parentElement.host) {
            return parentElement.host.isConnected;
        }

        return parentElement.isConnected;
    }


    function localIndex(
        state,
        absoluteIndex
    ) {

        return (
            absoluteIndex
            - state.segmentStart
        );
    }


    function valueAt(
        state,
        feature,
        absoluteIndex
    ) {

        const index =
            localIndex(
                state,
                absoluteIndex
            );

        const values =
            state.series[feature];

        if (
            !values
            || index < 0
            || index >= values.length
        ) {
            return null;
        }

        const value =
            Number(values[index]);

        return Number.isFinite(value)
            ? value
            : null;
    }


    function timestampAt(
        state,
        absoluteIndex
    ) {

        const local =
            localIndex(
                state,
                absoluteIndex
            );

        if (
            local >= 0
            && local < state.timestamps.length
        ) {

            return Number(
                state.timestamps[local]
            );
        }

        return (
            state.baseTimestamp
            + (
                absoluteIndex
                - state.segmentStart
            )
            * state.intervalMs
        );
    }


    function positionTimestamp(
        state,
        position
    ) {

        const floorPos =
            Math.floor(position);

        const fraction =
            position
            - floorPos;

        const t0 =
            timestampAt(
                state,
                floorPos
            );

        const t1 =
            timestampAt(
                state,
                floorPos + 1
            );

        return (
            t0
            + (t1 - t0)
            * fraction
        );
    }


    function formatNumber(value) {

        if (
            value === null
            || value === undefined
            || !Number.isFinite(value)
        ) {
            return "-";
        }

        return value.toFixed(3);
    }


    function formatDateTime(ms) {

        const date =
            new Date(ms);

        const pad =
            value =>
                String(value).padStart(
                    2,
                    "0"
                );

        return (
            date.getFullYear()
            + "-"
            + pad(
                date.getMonth() + 1
            )
            + "-"
            + pad(
                date.getDate()
            )
            + " "
            + pad(
                date.getHours()
            )
            + ":"
            + pad(
                date.getMinutes()
            )
        );
    }


    function formatAxisTime(ms) {

        const date =
            new Date(ms);

        const pad =
            value =>
                String(value).padStart(
                    2,
                    "0"
                );

        return (
            pad(
                date.getMonth() + 1
            )
            + "-"
            + pad(
                date.getDate()
            )
            + " "
            + pad(
                date.getHours()
            )
            + ":"
            + pad(
                date.getMinutes()
            )
        );
    }


    function average(values) {

        if (!values.length) {
            return null;
        }

        let sum = 0;

        for (
            const value
            of values
        ) {
            sum += value;
        }

        return (
            sum
            / values.length
        );
    }


    // ========================================================
    // Canvas sizing
    // ========================================================

    function resizeCanvas(
        state
    ) {

        const rect =
            canvas.getBoundingClientRect();

        const ratio =
            window.devicePixelRatio
            || 1;

        const width =
            Math.max(
                1,
                Math.round(
                    rect.width * ratio
                )
            );

        const height =
            Math.max(
                1,
                Math.round(
                    rect.height * ratio
                )
            );

        if (
            canvas.width !== width
            || canvas.height !== height
        ) {

            canvas.width = width;
            canvas.height = height;

            state.needsDraw = true;
        }

        return {
            cssWidth: rect.width,
            cssHeight: rect.height,
            ratio: ratio,
        };
    }


    // ========================================================
    // Forecast handling
    // ========================================================

    function applyForecast(
        state,
        forecast
    ) {

        if (!forecast) {
            return;
        }

        const seq =
            Number(
                forecast.seq
                ?? 0
            );

        if (
            seq <= state.forecastSeq
        ) {
            return;
        }

        state.forecastSeq =
            seq;

        state.forecast = forecast;

        state.latestLatency =
            Number(
                forecast.latency_ms
                ?? 0
            );

        state.lastForecastCursor =
            Number(
                forecast.cursor
            );

        state.requestPending =
            false;


        // ----------------------------------------------------
        // Store q50 predictions for future online evaluation.
        // Newer forecasts overwrite older forecasts for
        // future points.
        // ----------------------------------------------------

        const q50 =
            forecast.q50 || [];

        for (
            let i = 0;
            i < q50.length;
            i++
        ) {

            const index =
                Number(
                    forecast.cursor
                ) + i;

            state.pendingPredictions.set(
                index,
                Number(q50[i])
            );
        }

        state.needsDraw = true;
    }


    // ========================================================
    // Online evaluation
    // ========================================================

    function evaluateNewPoint(
        state,
        actualIndex
    ) {

        if (
            !state.pendingPredictions.has(
                actualIndex
            )
        ) {
            return;
        }

        const predicted =
            state.pendingPredictions.get(
                actualIndex
            );

        const actual =
            valueAt(
                state,
                state.targetName,
                actualIndex
            );

        state.pendingPredictions.delete(
            actualIndex
        );

        if (
            actual === null
            || !Number.isFinite(predicted)
        ) {
            return;
        }

        const error =
            Math.abs(
                actual
                - predicted
            );

        state.errors.push(
            error
        );

        if (
            state.errors.length
            > 500
        ) {

            state.errors =
                state.errors.slice(
                    -500
                );
        }
    }


    // ========================================================
    // Inference request
    // ========================================================

    function maybeRequestInference(
        state
    ) {

        if (
            state.requestPending
        ) {
            return;
        }

        if (
            state.currentCursor
            - state.lastForecastCursor
            < state.inferenceEvery
        ) {
            return;
        }

        if (
            state.currentCursor
            >= state.segmentEnd
        ) {
            return;
        }


        state.requestPending =
            true;

        state.requestSeq += 1;


        setTriggerValue(
            "inference_request",
            {
                cursor:
                    state.currentCursor,

                seq:
                    state.requestSeq,
            }
        );
    }


    // ========================================================
    // Metrics
    // ========================================================

    function updateMetrics(
        state
    ) {

        const latestIndex =
            state.currentCursor - 1;

        const currentValue =
            valueAt(
                state,
                state.targetName,
                latestIndex
            );

        const currentTime =
            timestampAt(
                state,
                latestIndex
            );


        parentElement
            .querySelector(
                "#metric-time"
            )
            .textContent =
                formatDateTime(
                    currentTime
                );


        parentElement
            .querySelector(
                "#metric-value-label"
            )
            .textContent =
                `当前 ${state.targetName}`;


        parentElement
            .querySelector(
                "#metric-value"
            )
            .textContent =
                formatNumber(
                    currentValue
                );


        parentElement
            .querySelector(
                "#metric-model"
            )
            .textContent =
                state.modelName;


        parentElement
            .querySelector(
                "#metric-latency"
            )
            .textContent = (
                Number.isFinite(
                    state.latestLatency
                )
                && state.latestLatency > 0
            )
                ? (
                    state.latestLatency
                    .toFixed(1)
                    + " ms"
                )
                : "-";


        const recentErrors =
            state.errors.slice(
                -200
            );

        const mae =
            average(
                recentErrors
            );


        parentElement
            .querySelector(
                "#metric-mae"
            )
            .textContent =
                mae === null
                    ? "-"
                    : mae.toFixed(4);


        parentElement
            .querySelector(
                "#chart-title"
            )
            .textContent =
                (
                    state.targetName
                    + " 实时监测与未来预测"
                );


        // ----------------------------------------------------
        // Status
        // ----------------------------------------------------

        const statusDot =
            parentElement
            .querySelector(
                "#status-dot"
            );

        const statusText =
            parentElement
            .querySelector(
                "#status-text"
            );


        if (state.running) {

            statusDot
                .classList
                .add(
                    "running"
                );

            statusText.textContent =
                "运行中";

        } else {

            statusDot
                .classList
                .remove(
                    "running"
                );

            statusText.textContent =
                state.finished
                    ? "回放结束"
                    : "已暂停";
        }


        parentElement
            .querySelector(
                "#position-text"
            )
            .textContent =
                (
                    "数据位置："
                    + state.currentCursor
                    .toLocaleString()
                    + " / "
                    + state.segmentEnd
                    .toLocaleString()
                    + "　"
                    + "在线验证："
                    + state.errors.length
                    .toLocaleString()
                    + " 点"
                );


        parentElement
            .querySelector(
                "#inference-status"
            )
            .textContent =
                state.requestPending
                    ? "模型正在推理..."
                    : "";
    }


    // ========================================================
    // Variable state cards
    // ========================================================

    function buildStateGrid(
        state
    ) {

        const grid =
            parentElement
            .querySelector(
                "#state-grid"
            );

        grid.innerHTML = "";

        for (
            const feature
            of state.features
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "state-item";

            item.innerHTML = `
                <div class="state-name">
                    ${feature}
                </div>

                <div
                    class="state-value"
                    id="state-${feature}">
                    -
                </div>
            `;

            grid.appendChild(
                item
            );
        }
    }


    function updateStateGrid(
        state
    ) {

        const index =
            state.currentCursor - 1;

        for (
            const feature
            of state.features
        ) {

            const element =
                parentElement
                .querySelector(
                    `#state-${feature}`
                );

            if (!element) {
                continue;
            }

            const value =
                valueAt(
                    state,
                    feature,
                    index
                );

            element.textContent =
                formatNumber(
                    value
                );
        }
    }


    // ========================================================
    // Y range
    // ========================================================

    function updateYRange(
        state,
        values
    ) {

        const finite =
            values.filter(
                value =>
                    Number.isFinite(value)
            );

        if (!finite.length) {
            return;
        }

        let min =
            Math.min(
                ...finite
            );

        let max =
            Math.max(
                ...finite
            );

        let span =
            max - min;

        if (
            !Number.isFinite(span)
            || span < 1e-6
        ) {
            span = 1;
        }

        const padding =
            span * 0.10;


        min -= padding;
        max += padding;


        if (
            state.yMin === null
            || state.yMax === null
        ) {

            state.yMin = min;
            state.yMax = max;

            return;
        }


        // ----------------------------------------------------
        // Only expand.
        //
        // Prevents the vertical axis from continuously
        // jumping up and down.
        // ----------------------------------------------------

        if (
            min < state.yMin
        ) {
            state.yMin = min;
        }

        if (
            max > state.yMax
        ) {
            state.yMax = max;
        }
    }


    // ========================================================
    // Drawing
    // ========================================================

    function draw(
        state
    ) {

        const size =
            resizeCanvas(
                state
            );

        const ratio =
            size.ratio;

        const width =
            size.cssWidth;

        const height =
            size.cssHeight;


        // ----------------------------------------------------
        // Draw in CSS pixel coordinates.
        // ----------------------------------------------------

        ctx.setTransform(
            ratio,
            0,
            0,
            ratio,
            0,
            0
        );


        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        const margin = {
            left: 58,
            right: 18,
            top: 18,
            bottom: 40,
        };


        const plotLeft =
            margin.left;

        const plotRight =
            width
            - margin.right;

        const plotTop =
            margin.top;

        const plotBottom =
            height
            - margin.bottom;


        const plotWidth =
            plotRight
            - plotLeft;

        const plotHeight =
            plotBottom
            - plotTop;


        // ----------------------------------------------------
        // Smooth current time.
        //
        // virtualCursor advances continuously, even though
        // real ETTm1 data arrives discretely.
        // ----------------------------------------------------

        const currentTime =
            positionTimestamp(
                state,
                state.virtualCursor
            );


        const leftTime =
            currentTime
            - (
                state.historyPoints
                * state.intervalMs
            );


        const rightTime =
            currentTime
            + (
                state.horizon
                * state.intervalMs
            );


        const xOf =
            timestamp => (
                plotLeft
                + (
                    (
                        timestamp
                        - leftTime
                    )
                    /
                    (
                        rightTime
                        - leftTime
                    )
                )
                * plotWidth
            );


        // ----------------------------------------------------
        // Collect visible values for Y range.
        // ----------------------------------------------------

        const valuesForScale = [];


        const historyStart =
            Math.max(
                state.segmentStart,
                state.currentCursor
                - state.historyPoints
                - 4
            );


        for (
            let index = historyStart;
            index < state.currentCursor;
            index++
        ) {

            const value =
                valueAt(
                    state,
                    state.targetName,
                    index
                );

            if (
                value !== null
            ) {
                valuesForScale.push(
                    value
                );
            }
        }
        
        if (
            state.showFutureTruth
        ) {

            const truthEnd =
                Math.min(
                    state.currentCursor
                    + state.horizon,
                    state.segmentEnd
                );


            for (
                let index = state.currentCursor;
                index < truthEnd;
                index++
            ) {

                const value =
                    valueAt(
                        state,
                        state.targetName,
                        index
                    );

                if (
                    value !== null
                ) {

                    valuesForScale.push(
                        value
                    );
                }
            }
        }


        if (
            state.forecast
        ) {

            for (
                const value
                of state.forecast.q10
            ) {

                if (
                    Number.isFinite(
                        Number(value)
                    )
                ) {
                    valuesForScale.push(
                        Number(value)
                    );
                }
            }

            for (
                const value
                of state.forecast.q90
            ) {

                if (
                    Number.isFinite(
                        Number(value)
                    )
                ) {
                    valuesForScale.push(
                        Number(value)
                    );
                }
            }
        }


        updateYRange(
            state,
            valuesForScale
        );


        const yMin =
            state.yMin ?? 0;

        const yMax =
            state.yMax ?? 1;


        const yOf =
            value => (
                plotBottom
                - (
                    (
                        value
                        - yMin
                    )
                    /
                    (
                        yMax
                        - yMin
                    )
                )
                * plotHeight
            );


        // ====================================================
        // Grid
        // ====================================================

        ctx.lineWidth = 1;
        ctx.strokeStyle =
            "rgba(128,128,128,0.17)";

        ctx.fillStyle =
            "rgba(100,116,139,0.90)";

        ctx.font =
            "11px sans-serif";


        const yTicks = 5;


        for (
            let i = 0;
            i <= yTicks;
            i++
        ) {

            const fraction =
                i / yTicks;

            const y =
                plotTop
                + fraction
                * plotHeight;

            const value =
                yMax
                - fraction
                * (
                    yMax - yMin
                );


            ctx.beginPath();

            ctx.moveTo(
                plotLeft,
                y
            );

            ctx.lineTo(
                plotRight,
                y
            );

            ctx.stroke();


            ctx.textAlign =
                "right";

            ctx.textBaseline =
                "middle";

            ctx.fillText(
                value.toFixed(2),
                plotLeft - 8,
                y
            );
        }


        // ----------------------------------------------------
        // X grid
        // ----------------------------------------------------

        const xTicks = 5;


        for (
            let i = 0;
            i <= xTicks;
            i++
        ) {

            const fraction =
                i / xTicks;

            const x =
                plotLeft
                + fraction
                * plotWidth;

            const time =
                leftTime
                + fraction
                * (
                    rightTime
                    - leftTime
                );


            ctx.beginPath();

            ctx.moveTo(
                x,
                plotTop
            );

            ctx.lineTo(
                x,
                plotBottom
            );

            ctx.stroke();


            ctx.textAlign =
                "center";

            ctx.textBaseline =
                "top";

            ctx.fillText(
                formatAxisTime(
                    time
                ),
                x,
                plotBottom + 9
            );
        }


        // ====================================================
        // Forecast band
        // ====================================================

        if (
            state.forecast
            && state.forecast.dates
        ) {

            const dates =
                state.forecast.dates;

            const q10 =
                state.forecast.q10;

            const q50 =
                state.forecast.q50;

            const q90 =
                state.forecast.q90;


            const valid = [];


            for (
                let i = 0;
                i < dates.length;
                i++
            ) {

                const time =
                    Number(
                        dates[i]
                    );


                // Only show future prediction.
                if (
                    time
                    < currentTime
                ) {
                    continue;
                }


                if (
                    time
                    > rightTime
                ) {
                    break;
                }


                valid.push(i);
            }


            // ------------------------------------------------
            // P10-P90 band
            // ------------------------------------------------

            if (
                valid.length >= 2
            ) {

                ctx.beginPath();


                for (
                    let k = 0;
                    k < valid.length;
                    k++
                ) {

                    const i =
                        valid[k];

                    const x =
                        xOf(
                            Number(
                                dates[i]
                            )
                        );

                    const y =
                        yOf(
                            Number(
                                q90[i]
                            )
                        );


                    if (k === 0) {

                        ctx.moveTo(
                            x,
                            y
                        );

                    } else {

                        ctx.lineTo(
                            x,
                            y
                        );
                    }
                }


                for (
                    let k =
                        valid.length - 1;
                    k >= 0;
                    k--
                ) {

                    const i =
                        valid[k];

                    const x =
                        xOf(
                            Number(
                                dates[i]
                            )
                        );

                    const y =
                        yOf(
                            Number(
                                q10[i]
                            )
                        );

                    ctx.lineTo(
                        x,
                        y
                    );
                }


                ctx.closePath();

                ctx.fillStyle =
                    "rgba(239,68,68,0.22)";

                ctx.fill();


                // --------------------------------------------
                // P50
                // --------------------------------------------

                ctx.beginPath();

                ctx.strokeStyle =
                    "#ef4444";

                ctx.lineWidth =
                    2;


                for (
                    let k = 0;
                    k < valid.length;
                    k++
                ) {

                    const i =
                        valid[k];

                    const x =
                        xOf(
                            Number(
                                dates[i]
                            )
                        );

                    const y =
                        yOf(
                            Number(
                                q50[i]
                            )
                        );


                    if (k === 0) {

                        ctx.moveTo(
                            x,
                            y
                        );

                    } else {

                        ctx.lineTo(
                            x,
                            y
                        );
                    }
                }


                ctx.stroke();
            }
        }
        
        // ====================================================
        // Future Ground Truth
        //
        // Only used for replay / evaluation.
        // In a real online system, future truth is unavailable.
        // ====================================================

        if (
            state.showFutureTruth
        ) {

            const truthStart =
                state.currentCursor;

            const truthEnd =
                Math.min(
                    state.currentCursor
                    + state.horizon,
                    state.segmentEnd
                );


            ctx.save();

            ctx.beginPath();

            ctx.strokeStyle =
                "#16a34a";

            ctx.lineWidth =
                1.8;

            ctx.setLineDash([
                7,
                5,
            ]);


            let truthStarted =
                false;


            for (
                let index = truthStart;
                index < truthEnd;
                index++
            ) {

                const value =
                    valueAt(
                        state,
                        state.targetName,
                        index
                    );


                if (
                    value === null
                ) {
                    continue;
                }


                const time =
                    timestampAt(
                        state,
                        index
                    );


                // Future truth should only be drawn
                // to the right of the current-time line.
                if (
                    time < currentTime
                ) {
                    continue;
                }


                if (
                    time > rightTime
                ) {
                    break;
                }


                const x =
                    xOf(
                        time
                    );

                const y =
                    yOf(
                        value
                    );


                if (
                    !truthStarted
                ) {

                    ctx.moveTo(
                        x,
                        y
                    );

                    truthStarted =
                        true;

                } else {

                    ctx.lineTo(
                        x,
                        y
                    );
                }
            }


            if (
                truthStarted
            ) {

                ctx.stroke();
            }


            ctx.restore();
        }


        // ====================================================
        // Actual observations
        // ====================================================

        ctx.beginPath();

        ctx.strokeStyle =
            "#2563eb";

        ctx.lineWidth =
            1.8;


        let started =
            false;


        for (
            let index = historyStart;
            index < state.currentCursor;
            index++
        ) {

            const value =
                valueAt(
                    state,
                    state.targetName,
                    index
                );

            if (
                value === null
            ) {
                continue;
            }


            const time =
                timestampAt(
                    state,
                    index
                );


            const x =
                xOf(time);

            const y =
                yOf(value);


            if (!started) {

                ctx.moveTo(
                    x,
                    y
                );

                started = true;

            } else {

                ctx.lineTo(
                    x,
                    y
                );
            }
        }


        ctx.stroke();


        // ====================================================
        // Current time line
        // ====================================================

        const nowX =
            xOf(
                currentTime
            );


        ctx.save();

        ctx.setLineDash([
            5,
            5,
        ]);

        ctx.strokeStyle =
            "rgba(71,85,105,0.75)";

        ctx.lineWidth =
            1;


        ctx.beginPath();

        ctx.moveTo(
            nowX,
            plotTop
        );

        ctx.lineTo(
            nowX,
            plotBottom
        );

        ctx.stroke();

        ctx.restore();


        // ====================================================
        // Axis labels
        // ====================================================

        ctx.fillStyle =
            "rgba(100,116,139,0.9)";

        ctx.font =
            "12px sans-serif";


        ctx.save();

        ctx.translate(
            14,
            (
                plotTop
                + plotBottom
            ) / 2
        );

        ctx.rotate(
            -Math.PI / 2
        );

        ctx.textAlign =
            "center";

        ctx.fillText(
            state.targetName,
            0,
            0
        );

        ctx.restore();


        state.needsDraw =
            false;
    }


    // ========================================================
    // Advance stream
    // ========================================================

    function advanceOnePoint(
        state
    ) {

        if (
            state.currentCursor
            >= state.segmentEnd
        ) {

            state.running =
                false;

            state.finished =
                true;

            return;
        }


        state.currentCursor += 1;


        // Newly arrived actual point.
        const actualIndex =
            state.currentCursor - 1;


        evaluateNewPoint(
            state,
            actualIndex
        );


        maybeRequestInference(
            state
        );


        updateMetrics(
            state
        );


        updateStateGrid(
            state
        );


        state.needsDraw =
            true;
    }


    // ========================================================
    // Animation loop
    // ========================================================

    function animationFrame(
        now
    ) {

        if (!rootConnected()) {
            return;
        }


        const state =
            root.__industrialState;


        if (!state) {
            return;
        }


        const deltaSeconds =
            Math.min(
                (
                    now
                    - state.lastFrameTime
                )
                / 1000,
                0.25
            );


        state.lastFrameTime =
            now;


        if (
            state.running
            && !state.finished
        ) {

            state.virtualCursor += (
                state.playbackSpeed
                * deltaSeconds
            );


            // ------------------------------------------------
            // Convert continuous cursor to discrete
            // sensor arrivals.
            // ------------------------------------------------

            const targetCursor =
                Math.floor(
                    state.virtualCursor
                );


            while (
                state.currentCursor
                < targetCursor
            ) {

                advanceOnePoint(
                    state
                );


                if (
                    state.finished
                ) {
                    break;
                }
            }


            // Always redraw while running:
            //
            // virtualCursor changes continuously, giving the
            // smooth left-moving effect.
            state.needsDraw =
                true;
        }


        if (
            state.needsDraw
        ) {

            draw(
                state
            );
        }


        state.rafId =
            requestAnimationFrame(
                animationFrame
            );
    }


    // ========================================================
    // State initialization
    // ========================================================

    function createState(
        incoming
    ) {

        const state = {

            segmentStart:
                Number(
                    incoming.segment_start
                ),

            segmentEnd:
                Number(
                    incoming.segment_end
                ),

            timestamps:
                incoming.timestamps,

            series:
                incoming.series,

            features:
                incoming.features,

            targetName:
                incoming.target_name,

            modelName:
                incoming.model_name,
                
            showFutureTruth:
                Boolean(
                    incoming.show_future_truth
                ),

            currentCursor:
                Number(
                    incoming.initial_cursor
                ),

            virtualCursor:
                Number(
                    incoming.initial_cursor
                ),

            historyPoints:
                Number(
                    incoming.history_points
                ),

            horizon:
                Number(
                    incoming.horizon
                ),

            intervalMs:
                Number(
                    incoming.interval_ms
                ),

            playbackSpeed:
                Number(
                    incoming.playback_speed
                ),

            inferenceEvery:
                Number(
                    incoming.inference_every
                ),

            running:
                Boolean(
                    incoming.running
                ),

            finished:
                false,

            resetToken:
                Number(
                    incoming.reset_token
                ),

            forecast:
                null,

            forecastSeq:
                -1,

            lastForecastCursor:
                Number(
                    incoming.initial_cursor
                ),

            requestPending:
                false,

            requestSeq:
                0,

            pendingPredictions:
                new Map(),

            errors:
                [],

            latestLatency:
                null,

            yMin:
                null,

            yMax:
                null,

            baseTimestamp:
                Number(
                    incoming.timestamps[0]
                ),

            lastFrameTime:
                performance.now(),

            needsDraw:
                true,

            rafId:
                null,
        };


        applyForecast(
            state,
            incoming.forecast
        );


        buildStateGrid(
            state
        );


        updateMetrics(
            state
        );


        updateStateGrid(
            state
        );


        return state;
    }


    // ========================================================
    // First mount
    // ========================================================

    if (
        !root.__industrialState
    ) {

        root.__industrialState =
            createState(
                data
            );


        const state =
            root.__industrialState;


        state.rafId =
            requestAnimationFrame(
                animationFrame
            );


        return;
    }


    // ========================================================
    // Existing component update
    //
    // Streamlit rerun does NOT recreate the chart when the
    // same component key is used.
    // ========================================================

    let state =
        root.__industrialState;


    // --------------------------------------------------------
    // Reset / structural configuration change
    // --------------------------------------------------------

    if (
        Number(
            data.reset_token
        )
        !== state.resetToken
    ) {

        root.__industrialState =
            createState(
                data
            );

        state =
            root.__industrialState;


        // The old RAF loop reads root.__industrialState,
        // therefore it automatically switches to the new
        // state object.

        return;
    }


    // ========================================================
    // Dynamic updates
    // ========================================================

    state.targetName =
        data.target_name;

    state.modelName =
        data.model_name;

    state.playbackSpeed =
        Number(
            data.playback_speed
        );
        
    state.showFutureTruth =
        Boolean(
            data.show_future_truth
        );

    state.inferenceEvery =
        Number(
            data.inference_every
        );

    state.historyPoints =
        Number(
            data.history_points
        );

    state.horizon =
        Number(
            data.horizon
        );


    const wasRunning =
        state.running;


    state.running =
        Boolean(
            data.running
        );


    if (
        !wasRunning
        && state.running
    ) {

        state.lastFrameTime =
            performance.now();
    }


    applyForecast(
        state,
        data.forecast
    );


    updateMetrics(
        state
    );


    updateStateGrid(
        state
    );


    state.needsDraw =
        true;
}
"""


# ============================================================
# Register V2 component
# ============================================================

_realtime_component = (
    st.components.v2.component(
        name="industrial_realtime_chart",
        html=HTML,
        css=CSS,
        js=JS,
    )
)


# ============================================================
# Public wrapper
# ============================================================

def render_realtime_chart(
    *,
    data,
    key,
    on_inference_request_change,
):

    return _realtime_component(
        data=data,

        # Required because JS uses:
        # setTriggerValue("inference_request", ...)
        on_inference_request_change=(
            on_inference_request_change
        ),

        key=key,

        width="stretch",
        height="content",
    )
