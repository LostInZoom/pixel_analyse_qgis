import math

from .formula import evaluate_formula

# def pixel_power_index(r, g, b, model):

#     if model["equation"] == "rgb_gamma":
#         gamma = model["gamma"]
#         red = r ** gamma
#         green = g ** gamma
#         blue = b ** gamma
#         return (
#             model["coefficients"]["red"] * red
#             + model["coefficients"]["green"] * green
#             + model["coefficients"]["blue"] * blue
#         )

#     if model["equation"] == "rgb_linear":

#         return (
#             model["coefficients"]["red"] * r
#             + model["coefficients"]["green"] * g
#             + model["coefficients"]["blue"] * b
#         )
#     if model["equation"] == "hoarau_hdr":
#         return (math.max(r,g,b))
#     if model["equation"] == "hoarau_oled":
#         return r+g+b

#     print(
#         "Unknown model equation:",
#         model["equation"]
#     )
#     return 0

def pixel_power_index(r, g, b, model):
    formula = model["pixel_formula"]

    return evaluate_formula(
        formula["expression"],
        variables={
            "r": r,
            "g": g,
            "b": b
        },
        constants=formula.get("constants", {})
    )

def average(values):

    if not values:
        return 0
    return sum(values) / len(values)


def standard_deviation(values):

    if not values:
        return 0
    mean = average(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def analyze_pixels(image, model):

    width = image.width()
    height = image.height()
    pixel_count = width * height

    R = []
    G = []
    B = []
    L = []

    total_power_index = 0

    for y in range(height):
        for x in range(width):

            color = image.pixelColor(x, y)

            r = color.red()
            g = color.green()
            b = color.blue()

            R.append(r)
            G.append(g)
            B.append(b)

            luminance = 0.2126 * r+ 0.7152 * g+ 0.0722 * b

            L.append(luminance)

            normalized_r = r / 255
            normalized_g = g / 255
            normalized_b = b / 255

            total_power_index += pixel_power_index(normalized_r,normalized_g,normalized_b,model)
    if pixel_count > 0:
        mean_ratio = total_power_index / pixel_count
    else :
        mean_ratio = 0
    output = model["output"]
    output_formula = model.get("output_formula")
    if output["type"] == "power":
            
        if output_formula is None:
            raise ValueError("A power model requires an output formula.")

        total_power = evaluate_formula(
            output_formula["expression"],
            variables={
                "index": mean_ratio,
                "pixel_count": pixel_count,
                "width": width,
                "height": height
            },
            constants=output_formula.get("constants", {})
        )
        power_per_pixel = (
            total_power / pixel_count
            if pixel_count > 0
            else 0
        )
        model_result = {
            "type": "power",
            "p_total_ecran": total_power,
            "p_pixel": power_per_pixel,
            "mean_ratio": mean_ratio,
            "model": model["name"],
            "unit": output.get("unit")
        }

    elif output["type"] == "indicator":
            if output_formula is not None:
                indicator = evaluate_formula(
                    output_formula["expression"],
                    variables={
                        "index": mean_ratio,
                        "pixel_count": pixel_count,
                        "width": width,
                        "height": height
                    },
                    constants=output_formula.get("constants", {})
                )
            else:
                indicator = mean_ratio
    
            model_result = {
                "type": "indicator",
                "indicator": indicator,
                "model": model["name"],
                "unit": output.get("unit"),
                "min": output.get("min"),
                "max": output.get("max")
            }
    
    else:
        raise ValueError(f"Unknown output type: {output['type']}")
    
    return {
        "pixelCount": pixel_count,
        "rgb": {
            "red": {
                "mean": average(R),
                "std": standard_deviation(R)
            },
            "green": {
                "mean": average(G),
                "std": standard_deviation(G)
            },
            "blue": {
                "mean": average(B),
                "std": standard_deviation(B)
            }
        },

        "luminance": {
            "mean": average(L),
            "std": standard_deviation(L)
        },

        "energy": model_result
    }