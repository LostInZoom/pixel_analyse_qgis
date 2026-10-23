
import json

from qgis.PyQt.QtCore import QSettings
import math

SETTINGS_KEY = "PixelEnergy/custom_models"


def load_custom_models():
    """Load custom models saved in the current QGIS profile."""
    settings = QSettings()
    raw_models = settings.value(SETTINGS_KEY, "[]")

    try:
        models = json.loads(raw_models)
    except (TypeError, json.JSONDecodeError):
        return []

    if not isinstance(models, list):
        return []

    valid_models = []

    # return [
    #     model
    #     for model in models
    #     if isinstance(model, dict)
    #     and model.get("built_in") is False
    #     and isinstance(model.get("id"), str)
    #     and model["id"].startswith("custom_")
    # ]

    for model in models:
        if not isinstance(model, dict):
            continue

        if model.get("built_in") is not False:
            continue

        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id.startswith("custom_"):
            continue

        name = model.get("name")
        if not isinstance(name, str) or not name.strip():
            continue

        pixel_formula = model.get("pixel_formula")
        if not isinstance(pixel_formula, dict):
            continue

        expression = pixel_formula.get("expression")
        if not isinstance(expression, str) or not expression.strip():
            continue

        output = model.get("output")
        if not isinstance(output, dict):
            continue

        if output.get("type") not in ("indicator", "power"):
            continue

        if output["type"] == "power":
            output_formula = model.get("output_formula")
            if not isinstance(output_formula, dict):
                continue

            output_expression = output_formula.get("expression")
            if not isinstance(output_expression, str) or not output_expression.strip():
                continue

        valid_models.append(model)

    return valid_models


def save_custom_model(model):
    """Create or update a custom model."""
    if not isinstance(model, dict):
        raise ValueError("The model must be a dictionary.")

    model_id = model.get("id")
    if not isinstance(model_id, str) or not model_id.startswith("custom_"):
        raise ValueError("Invalid custom model ID.")

    name = model.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("The model must have a name.")

    pixel_formula = model.get("pixel_formula")
    if not isinstance(pixel_formula, dict):
        raise ValueError("The pixel formula is missing.")

    expression = pixel_formula.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("The pixel formula cannot be empty.")

    output = model.get("output")
    if not isinstance(output, dict):
        raise ValueError("The output configuration is missing.")

    output_type = output.get("type")
    if output_type not in ("indicator", "power"):
        raise ValueError("The output type must be indicator or power.")

    output_formula = model.get("output_formula")

    if output_type == "power":
        if not isinstance(output_formula, dict):
            raise ValueError("A power model requires an output formula.")

        output_expression = output_formula.get("expression")
        if not isinstance(output_expression, str) or not output_expression.strip():
            raise ValueError("The output formula cannot be empty.")

    if output_type == "indicator":
        minimum = output.get("min")
        maximum = output.get("max")

        if (
            isinstance(minimum, bool)
            or not isinstance(minimum, (int, float))
        ):
            raise ValueError("The indicator minimum must be a number.")

        if (
            isinstance(maximum, bool)
            or not isinstance(maximum, (int, float))
        ):
            raise ValueError("The indicator maximum must be a number.")

        if not math.isfinite(minimum) or not math.isfinite(maximum):
            raise ValueError("Indicator bounds must be finite numbers.")

        if maximum < minimum:
            raise ValueError("The indicator maximum must be greater than or equal to the minimum.")

    model_to_save = dict(model)
    model_to_save["name"] = name.strip()
    model_to_save["built_in"] = False

    models = load_custom_models()

    for index, existing in enumerate(models):
        if existing["id"] == model_id:
            models[index] = model_to_save
            break
    else:
        models.append(model_to_save)

    settings = QSettings()
    settings.setValue(SETTINGS_KEY, json.dumps(models, ensure_ascii=False))
    settings.sync()

    if settings.status() != QSettings.Status.NoError:
        raise OSError("Could not save the custom models in QGIS settings.")

def delete_custom_model(model_id):
    """Delete a custom model by its ID."""
    if not isinstance(model_id, str) or not model_id.startswith("custom_"):
        raise ValueError("Built-in models cannot be deleted.")

    models = load_custom_models()
    remaining = [
        model for model in models
        if model["id"] != model_id
    ]

    settings = QSettings()
    settings.setValue(SETTINGS_KEY, json.dumps(remaining, ensure_ascii=False))
    settings.sync()

    if settings.status() != QSettings.Status.NoError:
        raise OSError("Could not update the saved custom models.")