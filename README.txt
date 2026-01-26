Windows

Dependencies:
    python -m venv venv
    venv\Scripts\Activate
    pip install -r requirements.txt

To run:
    venv\Scripts\Activate
    python main.py

To build:
    venv\Scripts\Activate
    python build.py


Linux

Dependencies:
    python3 -m venv venvlinux
    source venvlinux/bin/activate
    pip install -r requirements.txt

To run:
    source venvlinux/bin/activate
    python3 main.py

To build:
    source venvlinux/bin/activate
    python3 build.py


macOS

Dependencies:
    brew install python-tk
    python3 -m venv venvmacos
    source venvmacos/bin/activate
    pip install -r requirements.txt

To run:
    source venvmacos/bin/activate
    python3 main.py

To build:
    source venvmacos/bin/activate
    python3 build.py


Developer Mode Controls
(Enable by setting debug_developer_mode = 1 in src/library/resources/debug.py)

Global Controls:
    /           - Print cursor position to console
    Arrow Keys  - Move window (windowed mode only)

Play State Controls:
    Event Cards (Letters):
        F - Add Event Free to top of deck
        M - Add Event Merge to top of deck
        O - Add Event Move to top of deck
        P - Add Event Point to top of deck
        R - Add Event Redraw to top of deck
        D - Add Event Remove to top of deck
        V - Add Event Reveal to top of deck
        S - Add Event Swap to top of deck
    
    Path Cards (Numbers):
        1       - Add Path WS to top of deck
        Shift+1 - Add Path Strike WS to top of deck
        2       - Add Path ES to top of deck
        Shift+2 - Add Path Strike ES to top of deck
        3       - Add Path WE to top of deck
        Shift+3 - Add Path Strike WE to top of deck
        4       - Add Path NS to top of deck
        Shift+4 - Add Path Strike NS to top of deck
        5       - Add Path NW to top of deck
        Shift+5 - Add Path Strike NW to top of deck
        6       - Add Path NE to top of deck
        Shift+6 - Add Path Strike NE to top of deck
        7       - Add Path WES to top of deck
        Shift+7 - Add Path Strike WES to top of deck
        8       - Add Path NWS to top of deck
        Shift+8 - Add Path Strike NWS to top of deck
        9       - Add Path NES to top of deck
        Shift+9 - Add Path Strike NES to top of deck
        0       - Add Path NWE to top of deck
        Shift+0 - Add Path Strike NWE to top of deck
    
    Strike Management:
        Enter     - Add a strike (max 3)
        Backspace - Remove a strike (min 0)
    
    Misc:
        -         - Place 4-way path on hovered tile

Tutorial State Controls:
    ]         - Skip to next tutorial step
    \         - Toggle auto-skip mode
