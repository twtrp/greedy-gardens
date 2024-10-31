### How to setup
1. Enter in terminal: `python -m venv venv`
2. Enter in terminal: `.\venv\Scripts\activate`
3. When prompted if you want to select the new environment for the workspace folder, click Yes.
4. Enter in terminal: `pip install -r .\requirements.txt` when terminal is in (venv)
5. Enter in terminal: `python .\main.py` when terminal is in (venv)

### Coding tips and guides
- This project uses pygame-ce (community edition), a better fork of pygame. All of original pygame functions are still usable, the fork just provides more functions. Documentation: https://pyga.me/docs/
- Use utils.py functions. Most common pygame functions have been bundled and put into it for ease of use.
    - Use dir.xxx to access directories. Example: utils.load_image(dir=**dir.menu_bg**, name='1_sky.png', mode='colorkey')
- Use explicit parameter names when calling functions for readability, unless they produce errors. Example: Example: utils.load_image(**dir**=dir.menu_bg, **name**='1_sky.png', **mode**='colorkey')
- Follow PEP-8 code styling guide: https://peps.python.org/pep-0008/
- Tween library guide: https://pypi.org/project/tween/
- Performance optimization guide: https://www.codeproject.com/Articles/5298051/Improving-Performance-in-Pygame-Speed-Up-Your-Game
- Do not instantiate template classes directly. They are abstract classes and must be implemented as other classes.
- "iconfont-preview" vscode extension is recommended to preview the font

### Credits
- Main menu music:
    - https://youtu.be/TFmNW8lMITk?si=m1rsfmZrYmwVY0nk
    - https://youtu.be/B1zg9b4L88Q?si=K6Zwds-xZUdMJflR
- Farm Ambience
    - https://youtu.be/LFEGXjJhryY?si=TTUe2R5A281_xcYV
- End music
    - https://youtu.be/29QaQuQnOqQ?si=8WHmnpmR2BA4yZ-4
- Fonts
    - https://takwolf.itch.io/retro-pixel-font
    - https://lazy-fox.itch.io/lazy-pixel-fonts
- Fruit sprites
    - https://ninjikin.itch.io/fruit
- Menu background
    - https://free-game-assets.itch.io/free-summer-pixel-art-backgrounds
    - https://free-game-assets.itch.io/nature-landscapes-free-pixel-art
    - https://free-game-assets.itch.io/free-sky-with-clouds-background-pixel-art-set
    - https://robson.plus/white-noise-image-generator/ (noise texture generator: 320x180, 4x, grey, verylight)
- Falling leaves sprite
    - https://rs-pixel-store.itch.io/falling-leaf-fx
- Wind particles
    - https://nyknck.itch.io/wind
- Sprite sheet maker
    - https://www.finalparsec.com/tools/sprite_sheet_maker
- Sound effects
    - https://drive.google.com/drive/folders/1gkcY1atqp7wWKw-owWr6D_-aerRKtIyI (extracted stardew valley sounds)