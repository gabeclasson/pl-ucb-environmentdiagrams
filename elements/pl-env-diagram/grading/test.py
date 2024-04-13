import grading
import autoeval

student_input = {
    "heap": {
        "func": [
            {"name": "f", "parent": "f1", "funcIndex": "0", "nameWidth": 2},
            {"name": "g", "parent": "Global", "funcIndex": "1", "nameWidth": 2},
        ],
        "sequence": [
            {
                "item": [
                    {"val": "#heap-sequence-1", "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": '"goo"', "valWidth": 6, "itemIndex": "2"},
                    {"val": "4.56", "valWidth": 5, "itemIndex": "3"},
                    {"val": "2.0", "valWidth": 4, "itemIndex": "4"},
                    {"val": "True", "valWidth": 5, "itemIndex": "5"},
                    {"val": "False", "valWidth": 6, "itemIndex": "6"},
                ],
                "type": "list",
                "sequenceIndex": "0",
            },
            {
                "item": [
                    {"val": "3", "valWidth": 2, "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": "#heap-func-1", "itemIndex": "2"},
                ],
                "type": "tuple",
                "sequenceIndex": "1",
            },
        ],
    },
    "frame": [
        {
            "var": [
                {"val": "#heap-func-0", "name": "x", "varIndex": "0", "nameWidth": 2},
                {
                    "val": "7",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "#heap-sequence-0",
                    "name": "g",
                    "varIndex": "0",
                    "nameWidth": 2,
                }
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "#heap-func-1"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
        {
            "var": [
                {
                    "val": "5",
                    "name": "f",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "",
                    "name": "lst",
                    "valWidth": 1,
                    "varIndex": "1",
                    "nameWidth": 4,
                },
            ],
            "name": "g",
            "parent": "Global",
            "return": {"val": "#heap-sequence-1"},
            "nameWidth": 2,
            "frameIndex": "3",
        },
        {
            "var": [
                {
                    "val": "False",
                    "name": "y",
                    "valWidth": 6,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "5",
                    "name": "p",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "f3",
            "return": {"val": "True", "valWidth": 5},
            "nameWidth": 2,
            "frameIndex": "4",
        },
    ],
    "pointer": [
        {
            "d": "M 0, 15.593754768371582 L 125.94375610351562 0",
            "raw": '{"d":"M 0, 15.593754768371582 L 125.94375610351562 0","width":"125.94375610351562","height":"15.593754768371582","top":"72.5938px","left":"171.994px"}',
            "top": "72.5938px",
            "left": "171.994px",
            "width": "125.94375610351562",
            "height": "15.593754768371582",
            "origin": "frame-0-var-0-val",
            "destination": "heap-func-0",
        },
        {
            "d": "M 0, 65.59376239776611 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 65.59376239776611 L 121.60000610351562 0","width":"121.60000610351562","height":"65.59376239776611","top":"264.356px","left":"176.338px"}',
            "top": "264.356px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "65.59376239776611",
            "origin": "frame-1-return-val",
            "destination": "heap-func-1",
        },
        {
            "d": "M 0, 126.67501926422119 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 126.67501926422119 L 121.60000610351562 0","width":"121.60000610351562","height":"126.67501926422119","top":"168.475px","left":"176.338px"}',
            "top": "168.475px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "126.67501926422119",
            "origin": "frame-1-var-0-val",
            "destination": "heap-sequence-0",
        },
        {
            "d": "M 0, 208.6749963760376 L 121.60000610351562 0",
            "raw": '{"d":"M 0, 208.6749963760376 L 121.60000610351562 0","width":"121.60000610351562","height":"208.6749963760376","top":"360.238px","left":"176.338px"}',
            "top": "360.238px",
            "left": "176.338px",
            "width": "121.60000610351562",
            "height": "208.6749963760376",
            "origin": "frame-3-return-val",
            "destination": "heap-sequence-1",
        },
        {
            "d": "M 29.79998779296875, 0 L 0 179.07499599456787",
            "raw": '{"d":"M 29.79998779296875, 0 L 0 179.07499599456787","width":"29.79998779296875","height":"179.07499599456787","top":"181.162px","left":"297.938px"}',
            "top": "181.162px",
            "left": "297.938px",
            "width": "29.79998779296875",
            "height": "179.07499599456787",
            "origin": "heap-sequence-0-item-0-val",
            "destination": "heap-sequence-1",
        },
        {
            "d": "M 133.39996337890625, 108.56876850128174 L 0 0",
            "raw": '{"d":"M 133.39996337890625, 108.56876850128174 L 0 0","width":"133.39996337890625","height":"108.56876850128174","top":"264.356px","left":"297.938px"}',
            "top": "264.356px",
            "left": "297.938px",
            "width": "133.39996337890625",
            "height": "108.56876850128174",
            "origin": "heap-sequence-1-item-2-val",
            "destination": "heap-func-1",
        },
    ],
}

student_input_modified = {
    "heap": {
        "func": [
            {"name": "g", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
            {"name": "f", "parent": "f1", "funcIndex": "1", "nameWidth": 2},
        ],
        "sequence": [
            {
                "item": [
                    {"val": "#heap-sequence-1", "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": '"goo"', "valWidth": 6, "itemIndex": "2"},
                    {"val": "4.56", "valWidth": 5, "itemIndex": "3"},
                    {"val": "2.0", "valWidth": 4, "itemIndex": "4"},
                    {"val": "True", "valWidth": 5, "itemIndex": "5"},
                    {"val": "False", "valWidth": 6, "itemIndex": "6"},
                ],
                "type": "list",
                "sequenceIndex": "0",
            },
            {
                "item": [
                    {"val": "3", "valWidth": 2, "itemIndex": "0"},
                    {"val": "2", "valWidth": 2, "itemIndex": "1"},
                    {"val": "#heap-func-0", "itemIndex": "2"},
                ],
                "type": "tuple",
                "sequenceIndex": "1",
            },
        ],
    },
    "frame": [
        {
            "var": [
                {"val": "#heap-func-1", "name": "x", "varIndex": "0", "nameWidth": 2},
                {
                    "val": "7",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "#heap-sequence-0",
                    "name": "g",
                    "varIndex": "0",
                    "nameWidth": 2,
                }
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "#heap-func-0"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
        {
            "var": [
                {
                    "val": "5",
                    "name": "f",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "",
                    "name": "lst",
                    "valWidth": 1,
                    "varIndex": "1",
                    "nameWidth": 4,
                },
            ],
            "name": "g",
            "parent": "Global",
            "return": {"val": "#heap-sequence-1"},
            "nameWidth": 2,
            "frameIndex": "3",
        },
        {
            "var": [
                {
                    "val": "False",
                    "name": "y",
                    "valWidth": 6,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "5",
                    "name": "p",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "f3",
            "return": {"val": "True", "valWidth": 5},
            "nameWidth": 2,
            "frameIndex": "4",
        },
    ],
}

student_input_correct_intsonly = {
    "heap": {
        "func": [
            {"name": "f", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
        ],
    },
    "frame": [
        {
            "var": [
                {
                    "val": "5",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "6",
                    "name": "y",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
                {
                    "val": "'7'",
                    "name": "d",
                    "valWidth": 2,
                    "varIndex": "2",
                    "nameWidth": 2,
                },
                {"val": "#heap-func-0", "name": "f", "varIndex": "3", "nameWidth": 2},
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "10",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "20",
                    "name": "z",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "f",
            "parent": "Global",
            "return": {"val": "5"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
    ],
}

student_input_correct_testfunccode = {
    "heap": {
        "func": [
            {"name": "g", "parent": "Global", "funcIndex": "0", "nameWidth": 2},
        ],
    },
    "frame": [
        {
            "var": [
                {
                    "val": "5",
                    "name": "x",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {"val": "#heap-func-0", "name": "g", "varIndex": "1", "nameWidth": 2},
            ],
            "frameIndex": "0",
        },
        {
            "var": [
                {
                    "val": "'hello'",
                    "name": "h",
                    "valWidth": 2,
                    "varIndex": "0",
                    "nameWidth": 2,
                },
                {
                    "val": "12",
                    "name": "t",
                    "valWidth": 2,
                    "varIndex": "1",
                    "nameWidth": 2,
                },
            ],
            "name": "g",
            "parent": "Global",
            "return": {"val": "'hello12'"},
            "nameWidth": 2,
            "frameIndex": "1",
        },
    ],
}

testfunccode = """
x = 5
def g(h):
    t = 7 + x
    return h + str(t)
print(g("hello"))"""

#ft = autoeval.FrameTree(testfunccode)
#print(grading.grading(ft.generate_html_json(), student_input_correct_testfunccode, partial_credit="by_frame"))

if True:

    if 0:
        print("hi")
    t =[5,9]
    k = t[0] + [9]