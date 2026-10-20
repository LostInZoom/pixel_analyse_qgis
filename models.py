
SCREEN_MODELS = {
    "dong2012": {
        "id": "dong2012",
        "name": "Dong & Zhong (2012)",
        "screen": {
            "technology": "OLED"
        },
        "source": {
            "authors": "Mian Dong, Lin Zhong",
            "year": 2012,
            "title": "Power Modeling and Optimization for OLED Displays",
            "reference": ""
        },
        "pixel_formula": {
            "expression": (
                "@a_r * @r ^ @gamma + "
                "@a_g * @g ^ @gamma + "
                "@a_b * @b ^ @gamma"
            ),
            "constants": {
                "a_r": 0.3,
                "a_g": 0.25,
                "a_b": 0.45,
                "gamma": 2.2
            }
        },
        "output": {
            "type": "power",
            "unit": "W"
        },
        "output_formula": {
            "expression": "@P_base + @pixel_value * (@P_max - @P_base)",
            "constants": {
                "P_base": 0.1,
                "P_max": 2.0
            }
        },
        "calibrated": False,
        "built_in": True
    },

    "hoarauHDR": {
        "id": "hoarauHDR",
        "name": "Hoarau (2011) - HDR",
        "screen": {
            "technology": "HDR"
        },
        "source": {
            "authors": "Charlotte Hoarau",
            "year": 2011,
            "title": (
                "Reaching a Compromise between Contextual Constraints and Cartographic Rules: Application to Sustainable Maps"
            ),
            "reference": ""
        },
        "pixel_formula": {
            "expression": "max(@r, @g, @b)",
            "constants": {}
        },
        "output": {
            "type": "indicator",
            "unit": None,
            "min": 0,
            "max": 1
        },
        "output_formula": None,
        "calibrated": False,
        "built_in": True
    },

    "hoarauOLED": {
        "id": "hoarauOLED",
        "name": "Hoarau (2011) - OLED",
        "screen": {
            "technology": "OLED"
        },
        "source": {
            "authors": "Charlotte Hoarau",
            "year": 2011,
            "title": (
                "Reaching a Compromise between Contextual Constraints and Cartographic Rules: Application to Sustainable Maps"
            ),
            "reference": ""
        },
        "pixel_formula": {
            "expression": "@r + @g + @b",
            "constants": {}
        },
        "output": {
            "type": "indicator",
            "unit": None,
            "min": 0,
            "max": 3
        },
        "output_formula": None,
        "calibrated": False,
        "built_in": True
    }
}