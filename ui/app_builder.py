import gradio as gr
import datetime
from domain.calculator import Calculator
from services.handwriting_math_service import HandwritingMathService
from ui.clear_controller import ClearController
from config import CANVAS_SIZE

CUSTOM_CSS = """
.gradio-container {
    background: #f5f7fa !important;
    min-height: 100vh;
}
.header-card {
    text-align: center;
    padding: 28px 24px;
    background: #ffffff;
    border-radius: 16px;
    margin-bottom: 4px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
footer { visibility: hidden; }
"""

_PRED_IDLE_HTML = """
<div style="
    background: #f9fafb;
    border: 1.5px dashed #d1d5db;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    color: #9ca3af;
    font-style: italic;
    margin-top: 8px;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9em;
">✏️ 숫자를 그린 뒤 계산하세요</div>
"""

_RESULT_IDLE_HTML = """
<div style="
    background: #f9fafb;
    border: 1.5px dashed #d1d5db;
    border-radius: 16px;
    padding: 40px 20px;
    text-align: center;
    color: #9ca3af;
    font-size: 0.9em;
    font-style: italic;
">
    <div style="font-size: 2em; margin-bottom: 10px;">🧮</div>
    두 숫자를 그리고 계산 버튼을 눌러주세요
</div>
"""


def _confidence_color(pct: float) -> str:
    if pct >= 90:
        return "#16a34a"
    elif pct >= 70:
        return "#ca8a04"
    else:
        return "#dc2626"


def _pred_html(msg: str) -> str:
    if not msg or "Handwriting" in msg:
        return _PRED_IDLE_HTML

    try:
        left, right = msg.split("(probability:")
        digit = int(left.replace("Prediction:", "").strip())
        confidence = float(right.replace(")", "").strip()) * 100
        color = _confidence_color(confidence)
        bar_w = min(confidence, 100)
        bg_color = {"#16a34a": "#f0fdf4", "#ca8a04": "#fefce8", "#dc2626": "#fef2f2"}.get(color, "#f9fafb")
        border_color = {"#16a34a": "#bbf7d0", "#ca8a04": "#fde68a", "#dc2626": "#fecaca"}.get(color, "#e5e7eb")

        return f"""
        <div style="
            background: {bg_color};
            border: 1.5px solid {border_color};
            border-radius: 12px;
            padding: 18px 20px;
            margin-top: 8px;
        ">
            <div style="
                font-size: 2.8em;
                font-weight: 900;
                color: {color};
                text-align: center;
                line-height: 1;
                margin-bottom: 8px;
            ">{digit}</div>
            <div style="
                color: #6b7280;
                font-size: 0.82em;
                text-align: center;
                margin-bottom: 8px;
                font-family: monospace;
            ">신뢰도 {confidence:.1f}%</div>
            <div style="
                background: #e5e7eb;
                border-radius: 4px;
                height: 6px;
                overflow: hidden;
            ">
                <div style="
                    width: {bar_w}%;
                    height: 100%;
                    background: {color};
                    border-radius: 4px;
                "></div>
            </div>
        </div>
        """
    except Exception:
        return f"""
        <div style="
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            color: #374151;
            text-align: center;
            margin-top: 8px;
        ">{msg}</div>
        """


def _result_html(expr: str, result_msg: str) -> str:
    has_error = (
        not expr
        or "not enough" in expr.lower()
        or "error" in expr.lower()
        or "Write" in expr
    )
    if has_error:
        err_text = result_msg if result_msg else "양쪽에 숫자를 그려주세요"
        return f"""
        <div style="
            background: #fef2f2;
            border: 1.5px solid #fecaca;
            border-radius: 16px;
            padding: 36px 20px;
            text-align: center;
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">⚠️</div>
            <div style="color: #b91c1c; font-size: 0.95em;">{err_text}</div>
        </div>
        """

    raw_val = result_msg.replace("result:", "").strip()
    try:
        fval = float(raw_val)
        display = str(int(fval)) if fval == int(fval) else f"{fval:.4f}".rstrip("0").rstrip(".")
    except Exception:
        display = raw_val

    return f"""
    <div style="
        background: #ffffff;
        border: 1.5px solid #c7d2fe;
        border-radius: 16px;
        padding: 36px 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(99,102,241,0.1);
    ">
        <div style="
            color: #6b7280;
            font-size: 1em;
            letter-spacing: 4px;
            margin-bottom: 12px;
            font-family: monospace;
        ">{expr}</div>
        <div style="
            font-size: 3.8em;
            font-weight: 900;
            color: #4f46e5;
            line-height: 1;
        ">= {display}</div>
    </div>
    """


class AppBuilder:
    def __init__(
        self,
        service: HandwritingMathService,
        calculator: Calculator,
        clear_controller: ClearController,
    ):
        self._service = service
        self._calculator = calculator
        self._history: list[list[str]] = []

    def _calculate(self, raw1, raw2, operator):
        p1, p2, expr, res, prev1, prev2 = self._service.calculate(raw1, raw2, operator)

        h1 = _pred_html(p1)
        h2 = _pred_html(p2)
        rh = _result_html(expr, res)

        if expr and "not enough" not in expr.lower() and "error" not in expr.lower() and "Write" not in expr:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            raw_val = res.replace("result:", "").strip()
            try:
                fval = float(raw_val)
                disp = str(int(fval)) if fval == int(fval) else f"{fval:.4f}".rstrip("0").rstrip(".")
            except Exception:
                disp = raw_val
            self._history.insert(0, [ts, expr, disp])
            if len(self._history) > 12:
                self._history = self._history[:12]

        hist = self._history if self._history else [["", "", ""]]
        return h1, h2, rh, prev1, prev2, hist

    def _clear(self):
        return None, None, _PRED_IDLE_HTML, _PRED_IDLE_HTML, _RESULT_IDLE_HTML, None, None

    def launch(self, **kwargs):
        self._demo.launch(theme=self._theme, css=CUSTOM_CSS, **kwargs)

    def build(self):
        self._theme = gr.themes.Base(
            primary_hue="indigo",
            secondary_hue="purple",
            neutral_hue="gray",
        ).set(
            body_background_fill="#f5f7fa",
            block_background_fill="#ffffff",
            block_border_color="#e5e7eb",
            block_label_text_color="#374151",
            block_title_text_color="#111827",
            input_background_fill="#ffffff",
            panel_background_fill="#f9fafb",
            button_primary_background_fill="#4f46e5",
            button_primary_background_fill_hover="#4338ca",
            button_primary_text_color="white",
            button_secondary_background_fill="#ffffff",
            button_secondary_background_fill_hover="#f3f4f6",
            button_secondary_text_color="#374151",
            button_secondary_border_color="#d1d5db",
        )

        with gr.Blocks(title="AI 손글씨 계산기") as demo:

            # ── 헤더 ────────────────────────────────────────────────────
            gr.HTML("""
            <div class="header-card">
                <div style="font-size:2.2em; font-weight:900; color:#111827; margin-bottom:6px;">
                    AI 손글씨 계산기
                </div>
                <div style="color:#6b7280; font-size:0.95em;">
                    CNN이 손글씨 숫자를 인식하고 실시간으로 계산합니다 &nbsp;·&nbsp; MNIST
                </div>
            </div>
            """)

            # ── 3단 레이아웃 ─────────────────────────────────────────────
            with gr.Row(equal_height=False):

                # 왼쪽
                with gr.Column(scale=5):
                    gr.HTML('<p style="color:#374151;font-weight:600;margin:0 0 6px;">✏️ 첫 번째 숫자</p>')
                    editor1 = gr.Sketchpad(
                        type="numpy",
                        label="첫 번째 숫자",
                        show_label=False,
                        height=CANVAS_SIZE,
                        width=CANVAS_SIZE,
                    )
                    pred_html1 = gr.HTML(_PRED_IDLE_HTML)

                # 중앙
                with gr.Column(scale=4, min_width=220):
                    gr.HTML('<p style="color:#374151;font-weight:600;margin:0 0 6px;text-align:center;">⚡ 연산자 선택</p>')
                    operator = gr.Radio(
                        choices=self._calculator.supported_symbols(),
                        value="+",
                        label="연산자",
                        show_label=False,
                    )
                    gr.HTML('<p style="color:#374151;font-weight:600;margin:16px 0 6px;text-align:center;">📊 계산 결과</p>')
                    result_html_comp = gr.HTML(_RESULT_IDLE_HTML)

                    with gr.Row():
                        calc_btn = gr.Button("🚀  계산하기", variant="primary", scale=3)
                        clear_btn = gr.Button("🗑️", scale=1)

                # 오른쪽
                with gr.Column(scale=5):
                    gr.HTML('<p style="color:#374151;font-weight:600;margin:0 0 6px;">✏️ 두 번째 숫자</p>')
                    editor2 = gr.Sketchpad(
                        type="numpy",
                        label="두 번째 숫자",
                        show_label=False,
                        height=CANVAS_SIZE,
                        width=CANVAS_SIZE,
                    )
                    pred_html2 = gr.HTML(_PRED_IDLE_HTML)

            # ── 전처리 미리보기 ──────────────────────────────────────────
            with gr.Accordion("🔬 AI가 실제로 보는 이미지 (28×28 전처리)", open=False):
                with gr.Row():
                    preview1 = gr.Image(
                        label="첫 번째 전처리 이미지",
                        type="pil",
                        height=140,
                    )
                    preview2 = gr.Image(
                        label="두 번째 전처리 이미지",
                        type="pil",
                        height=140,
                    )

            # ── 계산 기록 ────────────────────────────────────────────────
            with gr.Accordion("📜 계산 기록 (최근 12개)", open=True):
                history_table = gr.Dataframe(
                    headers=["시간", "수식", "결과"],
                    datatype=["str", "str", "str"],
                    value=[["", "", ""]],
                    interactive=False,
                    wrap=True,
                    col_count=(3, "fixed"),
                )

            # ── 이벤트 연결 ──────────────────────────────────────────────
            calc_btn.click(
                fn=self._calculate,
                inputs=[editor1, editor2, operator],
                outputs=[pred_html1, pred_html2, result_html_comp, preview1, preview2, history_table],
            )

            clear_btn.click(
                fn=self._clear,
                inputs=[],
                outputs=[editor1, editor2, pred_html1, pred_html2, result_html_comp, preview1, preview2],
            )

        self._demo = demo
        return self
