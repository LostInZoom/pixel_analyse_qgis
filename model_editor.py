
import uuid

from qgis.PyQt.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QHBoxLayout,QLabel,QLineEdit,
    QComboBox,QDoubleSpinBox,QTableWidget,QTableWidgetItem,QPushButton,QDialogButtonBox,
    QMessageBox,QHeaderView,
)

from .formula import evaluate_formula, FormulaError
from .model_storage import save_custom_model


class ModelEditorDialog(QDialog):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)

        self.model = model or {}
        self.model_id = self.model.get("id","custom_" + uuid.uuid4().hex)

        self.setWindowTitle(self.tr("Custom screen model"))
        self.resize(650, 650)

        self.build_ui()
        self.load_model()

    def build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

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



        # layout.addWidget(QLabel(self.tr("Pixel formula:")))

        # self.pixel_formula_edit = QLineEdit()
        # self.pixel_formula_edit.setPlaceholderText("0.3 * r^2 + 0.25 * g^2 + 0.45 * b^2")
        # layout.addWidget(self.pixel_formula_edit)

        # layout.addWidget(QLabel(self.tr("Insert an allowed element:")))
        # layout.addLayout(
        #     self.create_token_buttons(
        #         self.pixel_formula_edit,
        #         ["r", "g", "b", "+", "-", "*", "/", "^",
        #          "(", ")", "min(", "max("]
        #     )
        # )

        # layout.addWidget(QLabel(self.tr("Pixel formula constants:")))
        # self.pixel_constants_table = self.create_constants_table()
        # layout.addWidget(self.pixel_constants_table)
        # layout.addLayout(self.create_constant_buttons(self.pixel_constants_table))



        pixel_group = QVBoxLayout()

        pixel_group.addWidget(QLabel(self.tr("Pixel formula:")))

        self.pixel_formula_edit = QLineEdit()
        self.pixel_formula_edit.setPlaceholderText("a_r * r^gamma + a_g * g^gamma + a_b * b^gamma")
        pixel_group.addWidget(self.pixel_formula_edit)

        pixel_group.addWidget(QLabel(self.tr("Insert an allowed element:")))
        pixel_group.addLayout(
            self.create_token_buttons(
                self.pixel_formula_edit,
                [
                    "r", "g", "b", "+", "-", "*", "/", "^",
                    "(", ")", "min(", "max("
                ]
            )
        )

        pixel_group.addWidget(QLabel(self.tr("Constants used in this formula:")))

        self.pixel_constants_table = self.create_constants_table()
        self.pixel_constants_table.setMaximumHeight(130)
        pixel_group.addWidget(self.pixel_constants_table)

        pixel_group.addLayout(self.create_constant_buttons(self.pixel_constants_table))
        layout.addLayout(pixel_group)



        layout.addWidget(QLabel(self.tr("Optional output formula:")))

        self.output_formula_edit = QLineEdit()
        self.output_formula_edit.setPlaceholderText("P_base + index * (P_max - P_base)")
        layout.addWidget(self.output_formula_edit)


        layout.addWidget(QLabel(self.tr("Output variables: index, pixel_count, width, height")))
        layout.addLayout(
            self.create_token_buttons(
                self.output_formula_edit,
                ["index", "pixel_count", "width", "height",
                 "+", "-", "*", "/", "^", "(", ")",
                 "min(", "max("]
            )
        )

        layout.addWidget(QLabel(self.tr("Output formula constants:")))
        self.output_constants_table = self.create_constants_table()
        layout.addWidget(self.output_constants_table)
        layout.addLayout(self.create_constant_buttons(self.output_constants_table))

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

    def create_token_buttons(self, line_edit, tokens):
        layout = QHBoxLayout()

        for token in tokens:
            button = QPushButton(token)
            button.setMaximumWidth(90)
            button.clicked.connect(
                lambda checked=False, value=token, target=line_edit:
                target.insert(value)
            )
            layout.addWidget(button)

        return layout

    def create_constants_table(self):
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels([self.tr("Name"),self.tr("Value")])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def create_constant_buttons(self, table):
        layout = QHBoxLayout()

        add_button = QPushButton(self.tr("Add a constant"))
        add_button.clicked.connect(
            lambda checked=False, target=table:
            self.add_constant_row(target)
        )

        remove_button = QPushButton(self.tr("Remove selected constant"))
        remove_button.clicked.connect(
            lambda checked=False, target=table:
            self.remove_constant_row(target)
        )

        layout.addWidget(add_button)
        layout.addWidget(remove_button)

        return layout

    def add_constant_row(self, table):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem("constant"))
        table.setItem(row, 1, QTableWidgetItem("1.0"))

    def remove_constant_row(self, table):
        row = table.currentRow()

        if row >= 0:
            table.removeRow(row)

    def read_constants(self, table):
        constants = {}

        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            value_item = table.item(row, 1)

            if name_item is None or value_item is None:
                raise ValueError(self.tr("Every constant needs a name and a value."))

            name = name_item.text().strip()
            value_text = value_item.text().strip()

            if not name or not value_text:
                raise ValueError(self.tr("Constant names and values cannot be empty."))

            try:
                value = float(value_text)
            except ValueError as error:
                raise ValueError(self.tr("Constant values must be numbers.")) from error

            if name in constants:
                raise ValueError(self.tr("Duplicate constant: ") + name)

            constants[name] = value

        return constants

    def load_constants(self, table, constants):
        table.setRowCount(0)

        for name, value in constants.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(str(value)))

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
        self.load_constants(self.pixel_constants_table,pixel_formula.get("constants", {}))

        output_formula = self.model.get("output_formula") or {}
        self.output_formula_edit.setText(output_formula.get("expression", ""))
        self.load_constants(self.output_constants_table,output_formula.get("constants", {}))

        self.update_output_controls()

    def update_output_controls(self):
        is_indicator = (self.output_type_combo.currentData() == "indicator")
        self.indicator_min.setEnabled(is_indicator)
        self.indicator_max.setEnabled(is_indicator)
        self.unit_edit.setEnabled(True)

    def validate_formulas(self):
        pixel_constants = self.read_constants(self.pixel_constants_table)
        output_constants = self.read_constants(self.output_constants_table)

        evaluate_formula(
            self.pixel_formula_edit.text(),
            variables={"r": 0.2, "g": 0.4, "b": 0.6},
            constants=pixel_constants
        )

        output_expression = self.output_formula_edit.text().strip()
        output_type = self.output_type_combo.currentData()

        if output_expression:
            evaluate_formula(
                output_expression,
                variables={
                    "index": 0.5,
                    "pixel_count": 100,
                    "width": 10,
                    "height": 10
                },
                constants=output_constants
            )

        if output_type == "power" and not output_expression:
            raise ValueError(self.tr("A power model requires an output formula."))

        if (output_type == "indicator" and self.indicator_max.value() < self.indicator_min.value()):
            raise ValueError(self.tr("The indicator maximum must be at least its minimum."))
        return pixel_constants, output_constants

    def test_formulas(self):
        try:
            pixel_constants, output_constants = self.validate_formulas()

            pixel_value = evaluate_formula(
                self.pixel_formula_edit.text(),
                variables={"r": 0.2, "g": 0.4, "b": 0.6},
                constants=pixel_constants
            )

            message = (
                self.tr("Pixel formula is valid.\n")
                + self.tr("Example result: ")
                + str(pixel_value)
            )

            output_expression = self.output_formula_edit.text().strip()

            if output_expression:
                output_value = evaluate_formula(
                    output_expression,
                    variables={
                        "index": pixel_value,
                        "pixel_count": 100,
                        "width": 10,
                        "height": 10
                    },
                    constants=output_constants
                )

                message += (
                    "\n"
                    + self.tr("Example output: ")
                    + str(output_value)
                )

            QMessageBox.information(
                self,
                self.tr("Formula test"),
                message
            )

        except (FormulaError, ValueError, ArithmeticError) as error:
            QMessageBox.warning(
                self,
                self.tr("Invalid formula"),
                str(error)
            )

    def save_model(self):
        try:
            pixel_constants, output_constants = self.validate_formulas()

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
                    "constants": output_constants
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
                    "constants": pixel_constants
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
