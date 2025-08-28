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
-> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
)"
-> brew install xz zlib bzip2 openssl readline tcl-tk
-> brew install pyenv
-> touch ~/.zshrc
-> Add the following lines to ~/.zshrc:
-> export PYENV_ROOT="$HOME/.pyenv"
-> command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
-> eval "$(pyenv init -)"
-> source ~/.zshrc
-> export TK_PREFIX="$(brew --prefix tcl-tk)"
-> export PATH="$TK_PREFIX/bin:$PATH"
-> export LDFLAGS="-L$TK_PREFIX/lib"
-> export CPPFLAGS="-I$TK_PREFIX/include"
-> export PKG_CONFIG_PATH="$TK_PREFIX/lib/pkgconfig"
-> pyenv install 3.12.0
-> pyenv global 3.12.0
-> python -m venv venvmac
-> source venvmac/bin/activate
-> pip install -r requirements.txt

To run:
-> source venvmac/bin/activate
-> python main.py

To build:
-> source venvmac/bin/activate
-> python build.py