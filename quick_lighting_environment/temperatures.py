# SPDX-License-Identifier: GPL-3.0-or-later

"""Built-in color-temperature choices."""


PRESETS = {
    "SUNRISE_SUNSET": (1850.0, "Sunrise / Sunset", "Warm natural light near the horizon"),
    "MOONLIGHT": (4150.0, "Moonlight", "Approximate apparent moonlight temperature"),
    "HORIZON_DAYLIGHT": (5000.0, "Horizon Daylight", "Daylight near the horizon"),
    "DAYLIGHT": (5600.0, "Daylight", "Daylight-balanced continuous studio light"),
    "OVERCAST_DAYLIGHT": (6500.0, "Overcast Daylight", "Cool overcast daylight"),
    "NORTH_SKY": (7500.0, "North Sky", "Cool indirect north-sky daylight"),
    "BLUE_SKY": (10000.0, "Blue Sky", "Strongly cool blue-sky illumination"),
    "STUDIO_TUNGSTEN": (3200.0, "Studio Tungsten", "Studio tungsten and photoflood balance"),
    "CP_PHOTOFLOOD": (3350.0, "CP Photoflood", "CP studio photoflood balance"),
    "ELECTRONIC_FLASH": (5800.0, "Electronic Flash", "Modern electronic flash tube"),
    "XENON_ARC": (6200.0, "Xenon Arc", "Cool xenon short-arc illumination"),
    "CANDLE": (1850.0, "Candle", "Candle-flame approximation"),
    "WARM_INCANDESCENT": (2400.0, "Warm Incandescent", "Warm household incandescent lamp"),
    "SOFT_WHITE_CFL": (2700.0, "Soft White / CFL", "Soft-white practical lamp"),
    "STANDARD_INCANDESCENT": (2856.0, "Standard Incandescent", "Standard incandescent reference"),
    "WARM_LED": (3000.0, "Warm LED", "Warm-white LED lamp"),
    "WHITE_FLUORESCENT": (3450.0, "White Fluorescent", "Approximate white fluorescent CCT"),
    "NEUTRAL_FLUORESCENT": (4150.0, "Neutral Fluorescent", "Approximate neutral fluorescent CCT"),
    "DAYLIGHT_FLUORESCENT": (
        5000.0,
        "Daylight Fluorescent",
        "Approximate daylight fluorescent CCT",
    ),
}

GROUPS = (
    (
        "Natural Light",
        (
            "SUNRISE_SUNSET",
            "MOONLIGHT",
            "HORIZON_DAYLIGHT",
            "DAYLIGHT",
            "OVERCAST_DAYLIGHT",
            "NORTH_SKY",
            "BLUE_SKY",
        ),
    ),
    (
        "Studio & Flash",
        (
            "STUDIO_TUNGSTEN",
            "CP_PHOTOFLOOD",
            "ELECTRONIC_FLASH",
            "XENON_ARC",
        ),
    ),
    (
        "Practical Lights",
        (
            "CANDLE",
            "WARM_INCANDESCENT",
            "SOFT_WHITE_CFL",
            "STANDARD_INCANDESCENT",
            "WARM_LED",
            "WHITE_FLUORESCENT",
            "NEUTRAL_FLUORESCENT",
            "DAYLIGHT_FLUORESCENT",
        ),
    ),
)
