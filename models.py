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

        "unit": "watts",
        "calibrated": False
    },

    "anotherModel": {

        "id": "anotherModel",
        "name": "Autre modèle",
        "type": "OLED",
        "equation": "rgb_linear",
        "coefficients": {
            "red": 0.3,
            "green": 0.5,
            "blue": 0.2,
            "p_base_watts": 0.1,
            "p_max_watts": 2.0
        },

        "unit": "watts",
        "calibrated": False
    }
}