Windows:

    Dependencies:
    - python -m venv venv
    - venv\Scripts\Activate
    - pip install -r requirements.txt

    To run:
    - venv\Scripts\Activate
    - python main.py

    To build:
    - venv\Scripts\Activate
    - pyinstaller --onefile --noconsole --name PlayGreedyGardens-[Version] main.py


Linux/MacOS:

    Dependencies:
    - python3 -m venv venvlinux
    - source venvlinux/bin/activate
    - pip install -r requirements.txt

    To run:
    - source venvlinux/bin/activate
    - python3 main.py

    To build:
    - source venvlinux/bin/activate
    - pyinstaller --onefile --noconsole --name PlayGreedyGardens-[Version] main.py