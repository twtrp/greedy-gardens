Windows:

    Dependencies:
    - python -m venv venv
    - venv\Scripts\Activate
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt

    To run:
    - venv\Scripts\Activate
    - python main.py

    To build:
    - venv\Scripts\Activate
    - pyinstaller --onefile --noconsole --name PlayGreedyGardens-[Version] main.py


Linux:

    Dependencies:
    - python3 -m venv venvlinux
    - source venvlinux/bin/activate
    - python3 -m pip install --upgrade pip setuptools wheel
    - pip install -r requirements.txt

    To run:
    - source venvlinux/bin/activate
    - python3 main.py

    To build:
    - source venvlinux/bin/activate
    - pyinstaller --onefile --noconsole --name PlayGreedyGardens-[Version] main.py


Mac:

    Dependencies:
    - python3 -m venv venvmac
    - source venvmac/bin/activate
    - python3 -m pip install --upgrade pip setuptools wheel
    - pip install -r requirements.txt

    To run:
    - source venvmac/bin/activate
    - python3 main.py

    To build:
    - source venvmac/bin/activate
    - pyinstaller --onefile --noconsole --name PlayGreedyGardens-[Version] main.py