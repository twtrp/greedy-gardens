### How to setup
1. Enter in terminal: `python -m venv venv`
2. Enter in terminal: `.\venv\Scripts\activate`
3. When prompted if you want to select the new environment for the workspace folder, click Yes.
4. Enter in terminal: `pip install -r .\requirements.txt` when terminal is in (venv)
5. Enter in terminal: `python .\main.py` when terminal is in (venv)
6. If the code can't run because of missing file or directory Enter in terminal: `mkdir data` and try step 5 again

### Coding tips and guides
- This project uses pygame-ce (community edition), a better fork of pygame. All of original pygame functions are still usable, the fork just provides more functions. Documentation: https://pyga.me/docs/
- Use utils.py functions. Most common pygame functions have been bundled and put into it for ease of use.
    - Use dir.xxx to access directories. Example: utils.get_image(dir=**dir.menu_bg**, name='1_sky.png', mode='colorkey')
- Use explicit parameter names when calling functions for readability, unless they produce errors. Example: Example: utils.get_image(**dir**=dir.menu_bg, **name**='1_sky.png', **mode**='colorkey')
- Follow PEP-8 code styling guide: https://peps.python.org/pep-0008/
- Tween library guide: https://pypi.org/project/tween/
- Performance optimization guide: https://www.codeproject.com/Articles/5298051/Improving-Performance-in-Pygame-Speed-Up-Your-Game
- "iconfont-preview" vscode extension is recommended to preview the font
