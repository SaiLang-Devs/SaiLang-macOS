"""Fun extras added to every chapter: a joke, a mission, and a quick quiz.

Missions have starter code, which the build checks with the SaiLang parser.
Quiz answers are printed on the Answers page at the back of the book.
"""

EXTRAS = {
    1: {
        "joke": "Why did the computer sneeze? It caught a virus!",
        "mission": {
            "title": "Mission 1: Introduce yourself",
            "goal": "Make Sai say three things about you, one per line, using say. Then add a comment above each line to explain it.",
            "starter": '# My first introduction\nsay "Hi, I am"\n',
        },
        "quiz": [
            ("What does <b>say</b> do?", "It shows text or values on the screen."),
            ("Which symbol starts a comment?", "The # symbol. SaiLang ignores everything after it on that line."),
        ],
    },
    2: {
        "joke": "Why do programmers hate nature? It has too many bugs!",
        "mission": {
            "title": "Mission 2: The robot's savings jar",
            "goal": "Make a variable called coins set to 0. Add 5 to it three times using =, then say the total.",
            "starter": "make coins = 0\n",
        },
        "quiz": [
            ("What is the difference between <b>make</b> and <b>=</b>?", "make creates a new variable. = changes one that already exists."),
            ("What does <b>ask</b> always give back?", "Text. Use number(...) to turn it into a number."),
        ],
    },
    3: {
        "joke": "Why did the if statement break up with the else? It needed more space!",
        "mission": {
            "title": "Mission 3: Traffic light",
            "goal": "Make a variable called light set to \"red\". Use when to say \"Stop!\" for red, \"Go!\" for green, and \"Slow down\" for anything else.",
            "starter": 'make light = "red"\n',
        },
        "quiz": [
            ("What kind of value must a condition give?", "true or false."),
            ("What does <b>otherwise when</b> let you do?", "Check another condition if the first one was false."),
        ],
    },
    4: {
        "joke": "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "mission": {
            "title": "Mission 4: Robot stair-climber",
            "goal": "Make Sai say \"Step\" followed by the step number, for steps 1 to 10. Skip step 7 by saying \"Wobble!\" instead.",
            "starter": "# Use for each with range(1, 11)\n",
        },
        "quiz": [
            ("Does <b>range(1, 4)</b> include the number 4?", "No. It stops before the second number."),
            ("What does <b>stop</b> do inside a loop?", "It leaves the loop straight away."),
        ],
    },
    5: {
        "joke": "Why was the list so calm? It knew how to keep its items in order!",
        "mission": {
            "title": "Mission 5: The pizza topping list",
            "goal": "Make a list of four toppings. Add one, remove one, and then say how many toppings you have.",
            "starter": 'make toppings = ["cheese", "ham"]\n',
        },
        "quiz": [
            ("What is the position of the first item in a list?", "0. Positions start at 0."),
            ("Which command adds an item to the end of a list?", "append(list, value)."),
        ],
    },
    6: {
        "joke": "What do you call a command that loves music? A function that can sing!",
        "mission": {
            "title": "Mission 6: The shout command",
            "goal": "Write a command called shout(word) that gives back the word in capitals and with three exclamation marks.",
            "starter": "command shout(word) {\n    # give the result here\n}\n",
        },
        "quiz": [
            ("What does <b>give</b> do?", "It sends a value back from a command and ends the command."),
            ("Can a command change a top-level variable?", "Yes, with plain = (without make)."),
        ],
    },
    7: {
        "joke": "Why did the programmer go broke? Too many bugs in the budget!",
        "mission": {
            "title": "Mission 7: The bug hunt",
            "goal": "This program has a bug. Find it, fix it, and then run the program. Use F6 to check the syntax first.",
            "starter": 'make score = 10\nsay "Score:", scroe\n',
        },
        "quiz": [
            ("What is the difference between a syntax error and a runtime error?", "A syntax error stops the program before it runs. A runtime error happens while it runs."),
            ("Which command lets a program keep going after an error?", "try, with on error."),
        ],
    },
    8: {
        "joke": "Why did the file break up with the folder? It felt like it was being stored too long!",
        "mission": {
            "title": "Mission 8: Secret diary",
            "goal": "Write a program that asks the user for a secret word and saves it to a file called secret.txt. Then read the file back and say it.",
            "starter": 'make word = ask("Secret word? ")\n',
        },
        "quiz": [
            ("What does <b>append_file</b> do that <b>write_file</b> does not?", "It adds to the end of the file instead of replacing it."),
            ("Why do we use <b>import</b>?", "To reuse commands and variables from another file."),
        ],
    },
    9: {
        "joke": "Why did the window get a job? It was great with views!",
        "mission": {
            "title": "Mission 9: Click counter",
            "goal": "Open a window with a button. Each time the button is pressed, add 1 to a counter and show the number in a label.",
            "starter": 'make clicks = 0\nmake win = open_window("Clicker", 260, 160)\n',
        },
        "quiz": [
            ("Which command starts the window and keeps it open?", "run_app()."),
            ("Why is the button's command name written in quotes?", "Because the button needs the name as text, so it knows which command to run."),
        ],
    },
    10: {
        "joke": "Why did the game developer bring a ladder? To reach the next level!",
        "mission": {
            "title": "Mission 10: Level up",
            "goal": "Change the coin game so the player needs 10 coins to win. Then make the coin move faster by changing the number in every.",
            "starter": 'make goal = 10\n',
        },
        "quiz": [
            ("What does <b>key_down(\"left\")</b> give back?", "true while the left arrow is held down, otherwise false."),
            ("Which command stops the repeating game loop?", "stop_timer()."),
        ],
    },
}

# A big 'pull quote' from Sai for each chapter, printed in large type.
QUOTES = {
    1: "Computers do exactly what you tell them. So tell them well!",
    2: "A variable is just a box with a name. Label your boxes clearly!",
    3: "Every decision is a question. Ask it carefully.",
    4: "Loops are how a computer does a million things without getting bored.",
    5: "A list is a row of lockers. Each locker has a number, starting at zero.",
    6: "Good commands do one job really well. Build them like LEGO bricks!",
    7: "Bugs are not failures. They are clues that point to the problem.",
    8: "Files remember things after the program stops. That is real power!",
    9: "A window is just a picture that listens. Give it buttons and let it talk!",
    10: "Every game you have ever played is a loop with some clever decisions inside.",
}
