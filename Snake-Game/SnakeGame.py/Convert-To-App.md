🧩 STEP 1 — Open Command Prompt
    Press Win + R → type cmd → hit Enter
    In Command Prompt, go to your folder : cd "Enter the path where you saved all the required file"

🧩 STEP 2 — Check Your Python Installation Path
    Run this command first in terminal(window command prompt) :  python --version

🧩 STEP 3 — Install PyInstaller (if not already)
    Run : pip install pyinstaller

🧩 STEP 4 — Create the Executable (.exe)
    Run this full command 👇
    pyinstaller --onefile --noconsole --icon="C:\Users\DELL\Desktop\Code To App\SnakeIcon.ico" "C:\Users\DELL\Desktop\Code To App\SnakeGames.py"

⚙️ What this does:
--onefile → packs everything into one .exe
--noconsole → hides the terminal window while the game runs
--icon=... → sets your game’s custom icon
"SnakeGames.py" → your main game script

🧩 STEP 5 — Find Your Game
    After the build completes, navigate to :  Path Where all the files are saved\dist\
    You’ll see : SnakeGames.exe

That’s your standalone game application 🎮
Double-click it — it should open your snake game with:
Custom icon 🐍
Background music
Sound effects
Fully working menu

🧩 (Optional) Rename it
    You can rename the file to something cleaner or whatever you want or like.....
