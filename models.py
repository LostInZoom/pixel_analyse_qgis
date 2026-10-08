

SCREEN_MODELS = {
    "dong2012": {

        "id": "dong2012",
        "name": "Dong & Zhong (2012)",
        "type": "OLED",
        "method": "dong2012",
        "screen": {
            "technology": "OLED"
        },
        "source": {
            "authors": "Mian Dong, Lin Zhong",
            "year": 2012,
            "title": "Power Modeling and Optimization for OLED Displays"
        },
        "equation": "rgb_gamma",
        "gamma": 2.2,
        "coefficients": {
            "red": 0.3,
            "green": 0.25,
            "blue": 0.45,
            "p_base_watts": 0.1,
            "p_max_watts": 2.0
        },
        "output": {
            "type": "power",
            "unit": "watts"
        },
        "calibrated": False
    },
    "hoarauHDR": {
        "id": "hoarauHDR",
        "name": "Hoarau (2011) - HDR",
        "type": "indicator",
        "method": "hoarau",
        "source": {
            "authors": "Charlotte Hoarau",
            "year": 2011,
            "title": "Reaching a Compromise between Contextual Constraints and Cartographic Rules: Application to Sustainable Maps"
        },
        "equation": "hoarau_hdr",
        "output": {
            "type": "indicator",
            "unit": None,
            "min": 0,
            "max": 1
        }
    },
    "hoarauOLED": {
        "id": "hoarauOLED",
        "name": "Hoarau (2011) - OLED",
        "type": "indicator",
        "method": "hoarau",

        "source": {
            "authors": "Charlotte Hoarau",
            "year": 2011,
            "title": "Reaching a Compromise between Contextual Constraints and Cartographic Rules: Application to Sustainable Maps"
        },

        "equation": "hoarau_oled",

        "output": {
            "type": "indicator",
            "unit": None,
            "min": 0,
            "max": 3
        }
        }
}