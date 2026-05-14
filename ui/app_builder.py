import gradio as gr
from domain.calculator import Calculator
from services.handwriting_math_service import HandwritingMathService
from ui.clear_controller import ClearController
from config import CANVAS_SIZE

class AppBuilder:
    def __init__(
        self,
        service: HandwritingMathService,
        calculator: Calculator,
        clear_controller: ClearController
    ):
        self._service = service
        self._calculator = calculator
        self._clear_controller = clear_controller

    def build(self):
        with gr.Blocks(title="MNIST Handwriting Calculator") as demo:
            gr.Markdown("# MNIST Handwriting Calculator")

            with gr.Row():
                editor1 = gr.Sketchpad(
                    type="numpy",
                    label="first",
                    height=CANVAS_SIZE,
                    width=CANVAS_SIZE
                )
                editor2 = gr.Sketchpad(
                    type="numpy",
                    label="second",
                    height=CANVAS_SIZE,
                    width=CANVAS_SIZE
                )

            operator = gr.Radio(
                choices=self._calculator.supported_symbols(),
                value="+",
                label="operator"
            )

            with gr.Row():
                calc_btn = gr.Button("Calculate", variant="primary")
                clear_btn = gr.Button("Clear")

            with gr.Row():
                pred1 = gr.Textbox(label="First number prediction result")
                pred2 = gr.Textbox(label="Second number prediction result")

            expression = gr.Textbox(label="Recognized expression")
            result = gr.Textbox(label="Final result")

            with gr.Row():
                preview1 = gr.Image(label="Preprocessed first image", type="pil")
                preview2 = gr.Image(label="Preprocessed second image", type="pil")

            calc_btn.click(
                fn=self._service.calculate,
                inputs=[editor1, editor2, operator],
                outputs=[pred1, pred2, expression, result, preview1, preview2]
            )

            clear_btn.click(
                fn=self._clear_controller.clear_all,
                inputs=[],
                outputs=[editor1, editor2, pred1, pred2, expression, result, preview1, preview2]
            )

        return demo