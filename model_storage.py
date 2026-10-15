
import json

from qgis.PyQt.QtCore import QSettings


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

    return [
        model
        for model in models
        if isinstance(model, dict)
        and model.get("built_in") is False
        and isinstance(model.get("id"), str)
        and model["id"].startswith("custom_")
    ]


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

    if output.get("type") not in ("indicator", "power"):
        raise ValueError("The output type must be indicator or power.")

    if output["type"] == "power" and not model.get("output_formula"):
        raise ValueError("A power model requires an output formula.")

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