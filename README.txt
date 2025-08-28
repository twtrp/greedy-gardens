Windows

Dependencies:
-> python -m venv venv
-> venv\Scripts\Activate
-> pip install -r requirements.txt

To run:
-> venv\Scripts\Activate
-> python main.py

To build:
-> venv\Scripts\Activate
-> python build.py

Linux

Dependencies:
-> python3 -m venv venvlinux
-> source venvlinux/bin/activate
-> pip install -r requirements.txt

To run:
-> source venvlinux/bin/activate
-> python3 main.py

To build:
-> source venvlinux/bin/activate
-> python3 build.py

macOS

Dependencies:
-> brew install tcl-tk
-> brew install python@3.12 --with-tcl-tk
-> $(brew --prefix)/bin/python3.12 -m venv venvmacos
-> source venvmacos/bin/activate
-> python -m pip install --upgrade pip setuptools wheel
-> pip install -r requirements.txt

To run:
-> source venvmacos/bin/activate
-> python main.py

To build:
-> source venvmacos/bin/activate
-> python build.py