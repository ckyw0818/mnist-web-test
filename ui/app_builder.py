import gradio as gr
from services.height_prediction_service import HeightPredictionService

DIGIT_SIZE = 160  # 각 자리 캔버스 크기

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
.digit-label {
    text-align: center;
    font-size: 0.78em;
    color: #9ca3af;
    margin-top: 4px;
    font-family: monospace;
    letter-spacing: 1px;
}
footer { visibility: hidden; }
"""

_RESULT_IDLE_HTML = """
<div style="
    background: #f9fafb;
    border: 1.5px dashed #d1d5db;
    border-radius: 16px;
    padding: 36px 20px;
    text-align: center;
    color: #9ca3af;
    font-size: 0.9em;
    font-style: italic;
">
    <div style="font-size: 2em; margin-bottom: 10px;">📏</div>
    엄마·아빠 키를 모두 그린 뒤<br>예측 버튼을 눌러주세요
</div>
"""


def _conf_color(pct: float) -> str:
    if pct >= 90:
        return "#16a34a"
    elif pct >= 70:
        return "#ca8a04"
    return "#dc2626"


def _digit_chip_html(digit, confidence) -> str:
    if digit is None:
        return '<span style="color:#d1d5db;font-size:1.6em;">?</span>'
    pct = confidence * 100
    color = _conf_color(pct)
    return (
        f'<span style="font-size:1.8em;font-weight:900;color:{color};">{digit}</span>'
        f'<span style="font-size:0.7em;color:#9ca3af;margin-left:2px;">{pct:.0f}%</span>'
    )


def _height_row_html(label: str, digits, height) -> str:
    chips = "  ".join(_digit_chip_html(d, c) for d, c in digits)
    height_str = f"<b>{height} cm</b>" if height is not None else "?"
    return f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px 20px;
        display:flex;
        align-items:center;
        gap:16px;
        margin-bottom:8px;
    ">
        <span style="color:#6b7280;font-weight:600;min-width:60px;">{label}</span>
        <span style="font-family:monospace;font-size:1.1em;">{chips}</span>
        <span style="margin-left:auto;color:#111827;font-size:1.1em;">{height_str}</span>
    </div>
    """


def _result_html(mom_digits, dad_digits, mom_h, dad_h, predicted, gender, error) -> str:
    if error:
        return f"""
        <div style="
            background:#fef2f2;border:1.5px solid #fecaca;
            border-radius:16px;padding:32px 20px;text-align:center;
        ">
            <div style="font-size:1.8em;margin-bottom:8px;">⚠️</div>
            <div style="color:#b91c1c;">{error}</div>
        </div>
        """

    formula = "(아빠키 + 엄마키 + 13) ÷ 2" if gender == "남자아이" \
              else "(아빠키 + 엄마키 − 13) ÷ 2"
    icon = "👦" if gender == "남자아이" else "👧"

    rows = _height_row_html("엄마 키", mom_digits, mom_h) + \
           _height_row_html("아빠 키", dad_digits, dad_h)

    pred_int = int(predicted)
    pred_dec = int((predicted - pred_int) * 10)

    return f"""
    <div style="background:#ffffff;border:1.5px solid #c7d2fe;border-radius:16px;
                padding:24px 20px;box-shadow:0 2px 12px rgba(99,102,241,0.08);">
        {rows}
        <div style="border-top:1px solid #e5e7eb;margin:16px 0;"></div>
        <div style="text-align:center;">
            <div style="color:#6b7280;font-size:0.85em;margin-bottom:6px;">
                {icon} {gender} 예측 공식 &nbsp;·&nbsp; <code style="background:#f3f4f6;padding:2px 6px;border-radius:4px;">{formula}</code>
            </div>
            <div style="font-size:3.4em;font-weight:900;color:#4f46e5;line-height:1.1;">
                {pred_int}<span style="font-size:0.45em;color:#6b7280;">.{pred_dec} cm</span>
            </div>
        </div>
    </div>
    """


class AppBuilder:
    def __init__(self, service: HeightPredictionService):
        self._service = service

    def _predict(self, m1, m2, m3, d1, d2, d3, gender):
        mom_digits, dad_digits, mom_h, dad_h, predicted, error, \
            mom_prev, dad_prev = self._service.predict(m1, m2, m3, d1, d2, d3, gender)

        rh = _result_html(mom_digits, dad_digits, mom_h, dad_h, predicted, gender, error)
        return (rh,) + tuple(mom_prev) + tuple(dad_prev)

    def _clear(self):
        return (None,) * 6 + (_RESULT_IDLE_HTML,) + (None,) * 6

    def launch(self, **kwargs):
        self._demo.launch(theme=self._theme, css=CUSTOM_CSS, **kwargs)

    def build(self):
        self._theme = gr.themes.Base(
            primary_hue="indigo",
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

        with gr.Blocks(title="AI 예측 키 계산기") as demo:

            # ── 헤더 ────────────────────────────────────────────────────
            gr.HTML("""
            <div class="header-card">
                <div style="font-size:2.2em;font-weight:900;color:#111827;margin-bottom:6px;">
                    AI 예측 키 계산기
                </div>
                <div style="color:#6b7280;font-size:0.95em;">
                    엄마·아빠 키를 손글씨로 입력하면 자녀의 예측 키를 계산해드립니다
                </div>
            </div>
            """)

            # ── 입력 영역 ─────────────────────────────────────────────
            with gr.Row():

                # 엄마 키
                with gr.Column():
                    gr.HTML('<p style="color:#374151;font-weight:700;font-size:1em;margin:0 0 8px;">👩 엄마 키 (cm)</p>')
                    with gr.Row():
                        with gr.Column(min_width=DIGIT_SIZE):
                            m1 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">백의 자리</div>')
                        with gr.Column(min_width=DIGIT_SIZE):
                            m2 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">십의 자리</div>')
                        with gr.Column(min_width=DIGIT_SIZE):
                            m3 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">일의 자리</div>')

                # 아빠 키
                with gr.Column():
                    gr.HTML('<p style="color:#374151;font-weight:700;font-size:1em;margin:0 0 8px;">👨 아빠 키 (cm)</p>')
                    with gr.Row():
                        with gr.Column(min_width=DIGIT_SIZE):
                            d1 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">백의 자리</div>')
                        with gr.Column(min_width=DIGIT_SIZE):
                            d2 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">십의 자리</div>')
                        with gr.Column(min_width=DIGIT_SIZE):
                            d3 = gr.Sketchpad(type="numpy", show_label=False,
                                              height=DIGIT_SIZE, width=DIGIT_SIZE)
                            gr.HTML('<div class="digit-label">일의 자리</div>')

            # ── 성별 + 버튼 ──────────────────────────────────────────
            with gr.Row():
                gender = gr.Radio(
                    choices=["남자아이", "여자아이"],
                    value="남자아이",
                    label="자녀 성별",
                )
                with gr.Column(min_width=200):
                    predict_btn = gr.Button("📏  키 예측하기", variant="primary")
                    clear_btn   = gr.Button("🗑️  초기화")

            # ── 결과 ─────────────────────────────────────────────────
            result_comp = gr.HTML(_RESULT_IDLE_HTML)

            # ── 전처리 미리보기 (접기) ────────────────────────────────
            with gr.Accordion("🔬 AI가 실제로 보는 이미지 (28×28 전처리)", open=False):
                with gr.Row():
                    mp1 = gr.Image(label="엄마 백", type="pil", height=100)
                    mp2 = gr.Image(label="엄마 십", type="pil", height=100)
                    mp3 = gr.Image(label="엄마 일", type="pil", height=100)
                    dp1 = gr.Image(label="아빠 백", type="pil", height=100)
                    dp2 = gr.Image(label="아빠 십", type="pil", height=100)
                    dp3 = gr.Image(label="아빠 일", type="pil", height=100)

            # ── 이벤트 ───────────────────────────────────────────────
            predict_btn.click(
                fn=self._predict,
                inputs=[m1, m2, m3, d1, d2, d3, gender],
                outputs=[result_comp, mp1, mp2, mp3, dp1, dp2, dp3],
            )

            clear_btn.click(
                fn=self._clear,
                inputs=[],
                outputs=[m1, m2, m3, d1, d2, d3, result_comp, mp1, mp2, mp3, dp1, dp2, dp3],
            )

        self._demo = demo
        return self
