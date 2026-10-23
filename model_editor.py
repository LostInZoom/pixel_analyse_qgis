
import uuid

from qgis.PyQt.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QHBoxLayout,QLabel,QLineEdit,
    QComboBox,QDoubleSpinBox,QTableWidget,QTableWidgetItem,QPushButton,QDialogButtonBox,
    QMessageBox,QHeaderView,
)

from qgis.gui import QgsExpressionBuilderDialog
from qgis.core import QgsExpression,QgsExpressionContext, QgsExpressionContextScope
from qgis.PyQt.QtWidgets import QLayout
from .formula import FormulaError, check_number
from .model_storage import save_custom_model
from qgis.PyQt.QtWidgets import QToolButton
class ModelEditorDialog(QDialog):

    def __init__(self, parent=None, model=None):
        super().__init__(parent)

        self.model = model or {}
        self.model_id = self.model.get("id","custom_" + uuid.uuid4().hex)

        self.setWindowTitle(self.tr("Custom screen model"))
        self.resize(650, 450)

        self.build_ui()
        self.load_model()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        form = QFormLayout()
        form.setVerticalSpacing(6)
        form.setHorizontalSpacing(10)

        self.name_edit = QLineEdit()
        form.addRow(self.tr("Model name:"), self.name_edit)

        self.technology_combo = QComboBox()
        self.technology_combo.addItems(["OLED" ,"LCD","HDR",self.tr("Other")])
        form.addRow(self.tr("Screen technology:"),self.technology_combo)

        self.output_type_combo = QComboBox()
        self.output_type_combo.addItem(self.tr("Relative indicator"),"indicator")
        self.output_type_combo.addItem(self.tr("Power"),"power")
        self.output_type_combo.currentIndexChanged.connect(self.update_output_controls)
        form.addRow(self.tr("Output type:"),self.output_type_combo)

        self.indicator_min = QDoubleSpinBox()
        self.indicator_min.setRange(-1e9, 1e9)
        self.indicator_min.setDecimals(6)
        self.indicator_min.setValue(0)

        self.indicator_max = QDoubleSpinBox()
        self.indicator_max.setRange(-1e9, 1e9)
        self.indicator_max.setDecimals(6)
        self.indicator_max.setValue(1)

        form.addRow(self.tr("Indicator minimum:"),self.indicator_min)
        form.addRow(self.tr("Indicator maximum:"),self.indicator_max)

        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText(self.tr("For example: W"))
        form.addRow(self.tr("Output unit:"), self.unit_edit)

        layout.addLayout(form)

        self.add_info_label(
                layout,
                "Pixel formula:",
                "Applied to every pixel. Use @r, @g and @b for normalized "
                "red, green and blue values between 0 and 1."
            )

        self.pixel_formula_edit = QLineEdit()
        self.pixel_formula_edit.setPlaceholderText("0.3 * @r ^ 2.2 + 0.25 * @g ^ 2.2 + 0.45 * @b ^ 2.2")

        pixel_row = QHBoxLayout()
        pixel_row.addWidget(self.pixel_formula_edit, 1)

        builder_button = QPushButton(self.tr("Build expression..."))
        builder_button.clicked.connect(self.open_pixel_expression_builder)
        pixel_row.addWidget(builder_button)
        layout.addLayout(pixel_row)

        self.add_info_label(
            layout,
            "Output formula (optional):",
            "Calculates the final output from @pixel_value, @pixel_count, "
            "@width and @height. For power models, it calculates total power."
        )

        self.output_formula_edit = QLineEdit()
        self.output_formula_edit.setPlaceholderText("0.1 + @pixel_value * (2.0 - 0.1)")

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_formula_edit, 1)

        output_builder_button = QPushButton(self.tr("Build expression..."))
        output_builder_button.clicked.connect(self.open_output_expression_builder)
        output_row.addWidget(output_builder_button)

        layout.addLayout(output_row)

        buttons_layout = QHBoxLayout()

        self.test_button = QPushButton(self.tr("Test formulas"))
        self.test_button.clicked.connect(self.test_formulas)
        buttons_layout.addWidget(self.test_button)

        self.save_button = QPushButton(self.tr("Save model"))
        self.save_button.clicked.connect(self.save_model)
        buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

        self.update_output_controls()
       

    def open_pixel_expression_builder(self):
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope("Pixel Energy")

        # Valeurs de test pour la prévisualisation de l'expression
        scope.setVariable("r", 0.5, True)
        scope.setVariable("g", 0.5, True)
        scope.setVariable("b", 0.5, True)

        context.appendScope(scope)

        dialog = QgsExpressionBuilderDialog(
            None,
            self.pixel_formula_edit.text(),
            self,
            "PixelEnergyPixelFormula",
            context
        )
        dialog.setWindowTitle(self.tr("Pixel formula builder"))

        if dialog.exec_():
            self.pixel_formula_edit.setText(dialog.expressionText())


    def open_output_expression_builder(self):
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope("Pixel Energy")

        # Valeurs d'exemple pour la prévisualisation
        scope.setVariable("pixel_value", 0.5, True)
        scope.setVariable("pixel_count", 100, True)
        scope.setVariable("width", 10, True)
        scope.setVariable("height", 10, True)

        context.appendScope(scope)

        dialog = QgsExpressionBuilderDialog(
            None,
            self.output_formula_edit.text(),
            self,
            "PixelEnergyOutputFormula",
            context
        )
        dialog.setWindowTitle(self.tr("Output formula builder"))

        if dialog.exec_():
            self.output_formula_edit.setText(dialog.expressionText())

    def add_info_label(self, layout, label_text, tooltip_text):
        row = QHBoxLayout()

        label = QLabel(self.tr(label_text))

        info_button = QToolButton()
        info_button.setText("ⓘ")
        info_button.setAutoRaise(True)
        info_button.setToolTip(self.tr(tooltip_text))
        info_button.setAccessibleName(
            self.tr("Information: ") + self.tr(label_text)
        )

        row.addWidget(label)
        row.addWidget(info_button)
        row.addStretch()

        layout.addLayout(row)

    def load_model(self):
        if not self.model:
            return

        self.name_edit.setText(self.model.get("name", ""))

        technology = self.model.get(
            "screen", {}
        ).get("technology", "OLED")

        index = self.technology_combo.findText(technology)

        if index >= 0:
            self.technology_combo.setCurrentIndex(index)

        output = self.model.get("output", {})
        output_type = output.get("type", "indicator")

        index = self.output_type_combo.findData(output_type)

        if index >= 0:
            self.output_type_combo.setCurrentIndex(index)

        self.indicator_min.setValue(output.get("min", 0))
        self.indicator_max.setValue(output.get("max", 1))
        self.unit_edit.setText(output.get("unit") or "")

        pixel_formula = self.model.get("pixel_formula", {})
        self.pixel_formula_edit.setText(
            pixel_formula.get("expression", "")
        )

        output_formula = self.model.get("output_formula") or {}
        self.output_formula_edit.setText(output_formula.get("expression", ""))

        self.update_output_controls()

    def update_output_controls(self):
        is_indicator = (self.output_type_combo.currentData() == "indicator")
        self.indicator_min.setEnabled(is_indicator)
        self.indicator_max.setEnabled(is_indicator)
        self.unit_edit.setEnabled(True)

    
    def evaluate_pixel_expression(self, expression_text, constants):
        expression = QgsExpression(expression_text)
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope("Pixel Energy")

        scope.setVariable("r", 0.2)
        scope.setVariable("g", 0.4)
        scope.setVariable("b", 0.6)

        for name, value in constants.items():
            scope.setVariable(name, value)

        context.appendScope(scope)

        if not expression.prepare(context):
            raise ValueError(expression.parserErrorString())

        result = expression.evaluate(context)

        if expression.hasEvalError():
            raise ValueError(expression.evalErrorString())

        return check_number(result)


    def evaluate_output_expression(self, expression_text, constants, pixel_value=0.5):
        expression = QgsExpression(expression_text)
        context = QgsExpressionContext()
        scope = QgsExpressionContextScope("Pixel Energy")

        scope.setVariable("pixel_value", pixel_value)
        scope.setVariable("pixel_count", 100)
        scope.setVariable("width", 10)
        scope.setVariable("height", 10)

        for name, value in constants.items():
            scope.setVariable(name, value)

        context.appendScope(scope)

        if not expression.prepare(context):
            raise ValueError(expression.parserErrorString())

        result = expression.evaluate(context)

        if expression.hasEvalError():
            raise ValueError(expression.evalErrorString())

        return check_number(result)



    def validate_formulas(self):
        self.evaluate_pixel_expression(self.pixel_formula_edit.text(),{})

        output_expression = self.output_formula_edit.text().strip()
        output_type = self.output_type_combo.currentData()

        if output_expression:
            self.evaluate_output_expression(output_expression,{})

        if output_type == "power" and not output_expression:
            raise ValueError(self.tr("A power model requires an output formula."))

        if (output_type == "indicator"and self.indicator_max.value() < self.indicator_min.value()):
            raise ValueError(self.tr("The indicator maximum must be at least its minimum."))

        return {}, {}


    def test_formulas(self):
        try:
            pixel_value = self.evaluate_pixel_expression(self.pixel_formula_edit.text(),{})

            message = (
                self.tr("Pixel formula is valid.\n")
                + self.tr("Example result: ")
                + str(pixel_value)
            )

            output_expression = self.output_formula_edit.text().strip()

            if output_expression:
                output_value = self.evaluate_output_expression(output_expression,{},pixel_value=pixel_value)
                message += (
                    "\n"
                    + self.tr("Example output: ")
                    + str(output_value)
                )

            output_type = self.output_type_combo.currentData()

            if output_type == "power" and not output_expression:
                raise ValueError(self.tr("A power model requires an output formula."))

            QMessageBox.information(self,self.tr("Formula test"),message)

        except (FormulaError, ValueError, ArithmeticError) as error:
            QMessageBox.warning(self,self.tr("Invalid formula"),str(error))


    def save_model(self):
        try:
            self.validate_formulas()

            output_type = self.output_type_combo.currentData()
            output_formula_expression = (
                self.output_formula_edit.text().strip()
            )

            output = {
                "type": output_type,
                "unit": self.unit_edit.text().strip() or None
            }

            if output_type == "indicator":
                output["min"] = self.indicator_min.value()
                output["max"] = self.indicator_max.value()

            output_formula = None

            if output_formula_expression:
                output_formula = {
                    "expression": output_formula_expression,
                    "constants": {}
                }

            model = {
                "id": self.model_id,
                "name": self.name_edit.text().strip(),
                "screen": {
                    "technology": self.technology_combo.currentText()
                },
                "source": {
                    "authors": "",
                    "year": None,
                    "title": self.tr("Custom model"),
                    "reference": ""
                },
                "pixel_formula": {
                    "expression": self.pixel_formula_edit.text().strip(),
                    "constants": {}
                },
                "output": output,
                "output_formula": output_formula,
                "calibrated": False,
                "built_in": False
            }

            if not model["name"]:
                raise ValueError(
                    self.tr("Enter a model name.")
                )

            save_custom_model(model)

            self.model = model

            QMessageBox.information(
                self,
                self.tr("Model saved"),
                self.tr("The custom model has been saved.")
            )

            self.accept()

        except (FormulaError, ValueError, ArithmeticError, OSError) as error:
            QMessageBox.warning(
                self,
                self.tr("Could not save model"),
                str(error)
            )
