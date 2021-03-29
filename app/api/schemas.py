POST_COURIER_SCHEMA = {
    "type": "object",
    "title": "The root schema of delivery",
    "default": {},
    "examples": [
        {
            "courier_id": 0,
            "courier_type": "foot",
            "regions": [
                1
            ],
            "working_hours": [
                "12:00-18:00"
            ]
        }
    ],
    "required": [
        "courier_id",
        "courier_type",
        "regions",
        "working_hours"
    ],
    "properties": {
        "courier_id": {
            "type": "integer",
            "title": "The courier_id schema",
        },
        "regions": {
            "type": "array",
            "additionalItems": True,
            "items": {
                "anyOf": [
                    {
                        "type": "integer",
                        "minimum": 0
                    }
                ]
            }
        },
        "courier_type": {
            "examples": [
                "foot"
            ],
            "title": "The courier_type schema",
            "enum": [
                "foot",
                "car",
                "bike"
            ],
            "type": "string"
        },
        "working_hours": {
            "type": "array",
            "default": [],
            "examples": [
                [
                    "08:00-09:00"
                ]
            ],
            "additionalItems": True,
            "items": {
                "anyOf": [
                    {
                        "type": "string",
                        "default": "",
                        "examples": [
                            "08:00-09:00"
                        ]
                    }
                ]
            }
        }
    },
    "additionalProperties": False
}

PATCH_COURIER_SCHEMA = {
    "type": "object",
    "title": "The patch courier schema",
    "properties": {
        "regions": {
            "type": "array",
            "additionalItems": True,
            "items": {
                "anyOf": [
                    {
                        "type": "integer",
                        "minimum": 0
                    }
                ]
            }
        },
        "courier_type": {
            "examples": [
                "foot"
            ],
            "title": "The courier_type schema",
            "enum": [
                "foot",
                "car",
                "bike"
            ],
            "type": "string"
        },
        "working_hours": {
            "type": "array",
            "default": [],
            "examples": [
                [
                    "08:00-09:00"
                ]
            ],
            "additionalItems": True,
            "items": {
                "anyOf": [
                    {
                        "type": "string",
                        "default": "",
                        "examples": [
                            "08:00-09:00"
                        ]
                    }
                ]
            }
        }
    },
    "additionalProperties": False
}

POST_ORDER_SCHEMA = {
    "type": "object",
    "title": "The root schema of delivery",
    "default": {},
    "required": [
        "order_id",
        "weight",
        "region",
        "delivery_hours"
    ],
    "properties": {
        "order_id": {
            "type": "integer",
            "minimum": 0
        },
        "region": {
                "type": "integer",
                "minimum": 0
        },
        "weight": {
            "type": "number",
            "minimum": 0.01,
            "maximum": 50
        },
        "delivery_hours": {
            "type": "array",
            "default": [],
            "examples": [
                [
                    "08:00-09:00"
                ]
            ],
            "additionalItems": True,
            "items": {
                "anyOf": [
                    {
                        "type": "string",
                        "default": "",
                        "examples": [
                            "08:00-09:00"
                        ]
                    }
                ]
            }
        }
    },
    "additionalProperties": False
}

POST_COMPLETE_ORDER_SCHEMA = {
    "required": [
        "courier_id"
    ],
    "properties": {
        "courier_id": {
            "type": "integer"
        }
    },
    "additionalProperties": False
}