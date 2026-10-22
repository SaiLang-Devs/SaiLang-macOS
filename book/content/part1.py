"""Book content, part 1: front matter and chapters 1 to 5.

Block types:
  p        paragraph (supports <b>, <i>; write &amp; and &lt; for symbols)
  h        small coloured heading
  bubble   speech bubble from Sai the robot
  code     SaiLang program. Keys: src, out (expected output), input (answers
           for ask), error (expected error text, when the program should fail),
           gui (True for window programs), files (extra files for imports)
  try      'Try it!' challenge box. Keys: title, steps
  tip      'Top tip' box
  watch    'Watch out!' box for common mistakes
  fun      'Did you know?' box
  list     bullet list of items
  table    simple two-column table. Keys: rows (list of [left, right])
"""

FRONT_WELCOME = {
    "title": "Welcome aboard!",
    "blocks": [
        {"type": "p", "text": "Hello, and welcome to <b>Learn to Code with SaiLang</b>! Coding is a way of giving clear instructions to a computer. Computers do exactly what they are told, so learning to code means learning to explain things very clearly."},
        {"type": "bubble", "text": "Hi! I'm Sai, your robot guide. I'll be with you on every page. Ready to start?"},
        {"type": "p", "text": "In this book you will write real programs. You will make a computer say things, do sums, make decisions, repeat actions, build your own commands, open windows and even make a game. Every program in this book has been tested, so if you type it in exactly, it will work."},
    ],
}

FRONT_HOWTO = {
    "title": "How to use this book",
    "blocks": [
        {"type": "p", "text": "Each chapter introduces a few new ideas. Read the text, then type in the examples and see what happens. Changing the examples is the best way to learn."},
        {"type": "table", "rows": [
            ["Code boxes", "Programs to type in. The colours help you see keywords, text and numbers."],
            ["Output", "What the program should show on screen when it runs."],
            ["Try it!", "Challenges for you to solve. Answers are not given, because finding them is the fun part!"],
            ["Top tip", "Helpful hints that save time."],
            ["Watch out!", "Common mistakes, and how to fix them."],
            ["Did you know?", "Extra facts to surprise your friends."],
        ]},
        {"type": "p", "text": "Typing code yourself, rather than copying and pasting it, helps your brain remember what each part does."},
    ],
}

FRONT_SETUP = {
    "title": "Get ready to code",
    "blocks": [
        {"type": "p", "text": "You need two things before you start: <b>Python 3.9 or newer</b> and the <b>SaiLang</b> folder. Ask a grown-up to help you with the installation if you need to."},
        {"type": "list", "items": [
            "Go to python.org/downloads and install Python for Windows. Tick <b>tcl/tk and IDLE</b> during setup, and choose <b>Install for me only</b>.",
            "Run <b>SaiLang-Setup</b> from the website. It asks a few questions, installs SaiLang and puts an icon on your desktop.",
            "Open <b>SaiLang IDLE</b> from your desktop or Start Menu. A window opens. This is your coding workshop.",
        ]},
        {"type": "tip", "text": "To start a new program, choose <b>File &gt; New</b>. To save it, choose <b>File &gt; Save As</b> and give it a name ending in <b>.sai</b>, such as <b>hello.sai</b>. Press <b>F5</b> to run it."},
    ],
}

CHAPTERS_1_5 = [
    {
        "num": 1,
        "title": "Hello, SaiLang!",
        "colour": "#FF8A00",
        "learn": ["Make SaiLang say things with <b>say</b>", "Write text in double quotes", "Add notes with comments", "Run your first program"],
        "blocks": [
            {"type": "p", "text": "Every programmer starts with a \"Hello, world!\" program. It is the first thing many coders ever make a computer do, and it is a great way to check that everything works."},
            {"type": "bubble", "text": "Let's say hello to the world!"},
            {"type": "h", "text": "Your very first line of code"},
            {"type": "code", "src": 'say "Hello, world!"', "out": "Hello, world!"},
            {"type": "p", "text": "<b>say</b> tells SaiLang to show something on the screen. The words inside the double quotes are called <b>text</b>. The quotes themselves do not appear on the screen."},
            {"type": "h", "text": "Saying more than one thing"},
            {"type": "code", "src": 'say "Hello, world!"\nsay "My name is Sai"\nsay "I can count:", 1, 2, 3',
             "out": "Hello, world!\nMy name is Sai\nI can count: 1 2 3"},
            {"type": "p", "text": "Separate the things you want to say with commas. SaiLang puts a space between each one. Each <b>say</b> line starts a new line on the screen."},
            {"type": "h", "text": "Notes for humans"},
            {"type": "p", "text": "A <b>#</b> starts a comment. A comment is a note for people reading the code. SaiLang skips over it completely."},
            {"type": "code", "src": '# This line is a comment. SaiLang ignores it.\nsay "Comments help people read code"  # so do these words',
             "out": "Comments help people read code"},
            {"type": "try", "title": "Try it!", "steps": [
                "Make SaiLang say your favourite animal in a sentence, such as: My favourite animal is a fox.",
                "Make it say three lines about yourself, using three say lines.",
            ]},
            {"type": "watch", "text": "If you forget the closing quote, SaiLang stops and tells you. Here is what that looks like:"},
            {"type": "code", "src": 'say "Hello', "error": "missing its closing quote"},
            {"type": "fun", "text": "The code in this book was tested by running it, so the outputs you see are the real results."},
        ],
    },
    {
        "num": 2,
        "title": "Words that hold values",
        "colour": "#22B573",
        "learn": ["Store values with <b>make</b>", "Use numbers, text and true/false", "Change a value with <b>=</b>", "Ask the user questions"],
        "blocks": [
            {"type": "p", "text": "A <b>variable</b> is a labelled box that holds a value. You make a box with <b>make</b>, then give the box a name. Whenever you use the name, SaiLang looks inside the box."},
            {"type": "bubble", "text": "Think of a variable as a box with a label on the front. The label is the name, and the box holds the value!"},
            {"type": "code", "src": 'make name = "Sai"\nmake age = 10\nsay name\nsay age',
             "out": "Sai\n10"},
            {"type": "h", "text": "Numbers can do sums"},
            {"type": "code", "src": 'make apples = 3\nmake more = apples + 2\nsay more\nsay 10 - 4 * 2\nsay 7 / 2\nsay 17 % 5',
             "out": "5\n2\n3.5\n2"},
            {"type": "p", "text": "The signs are <b>+</b> (add), <b>-</b> (take away), <b>*</b> (times), <b>/</b> (divide) and <b>%</b> (remainder). Multiplication and division happen before adding and taking away, just like in maths class. <b>17 % 5</b> is 2, because 5 fits into 17 three times with 2 left over."},
            {"type": "h", "text": "Text can be joined together"},
            {"type": "code", "src": 'make first = "Sai"\nmake last = "Robot"\nsay first + " " + last\nsay "Age: " + 10',
             "out": "Sai Robot\nAge: 10"},
            {"type": "tip", "text": "When you use <b>+</b> with text, SaiLang joins the pieces together. A number next to text is turned into text first."},
            {"type": "h", "text": "True, false and nothing"},
            {"type": "p", "text": "A <b>truth value</b> is either <b>true</b> or <b>false</b>. You will use these a lot when you make decisions in the next chapter. <b>nothing</b> means there is no value at all."},
            {"type": "code", "src": 'make sunny = true\nsay sunny\nsay sunny and false\nsay nothing',
             "out": "true\nfalse\nnothing"},
            {"type": "h", "text": "Changing a value"},
            {"type": "p", "text": "Use <b>make</b> to create a variable the first time. After that, use a plain <b>=</b> to change it. This is how a score goes up in a game."},
            {"type": "code", "src": 'make score = 0\nscore = score + 5\nscore = score + 5\nsay "Score:", score',
             "out": "Score: 10"},
            {"type": "watch", "text": "You cannot change a variable that does not exist yet. SaiLang will tell you so. Always use <b>make</b> first."},
            {"type": "h", "text": "Asking questions"},
            {"type": "p", "text": "The <b>ask</b> command pauses the program and waits for the user to type something. The text they type is stored in a variable."},
            {"type": "code", "src": 'make name = ask("What is your name? ")\nsay "Nice to meet you,", name',
             "out": "What is your name? Sai\nNice to meet you, Sai", "input": ["Sai"]},
            {"type": "p", "text": "What the user types is always text. To use it as a number, wrap it in <b>number(...)</b>."},
            {"type": "code", "src": 'make age = number(ask("How old are you? "))\nsay "Next year you will be", age + 1',
             "out": "How old are you? 10\nNext year you will be 11", "input": ["10"]},
            {"type": "try", "title": "Try it!", "steps": [
                "Make a variable called favourite_number and say it doubled.",
                "Ask the user for their favourite colour and say a sentence about it.",
            ]},
            {"type": "fun", "text": "The command <b>type_of(value)</b> tells you what kind of value you have. Try <b>say type_of(10)</b>."},
        ],
    },
    {
        "num": 3,
        "title": "Making decisions",
        "colour": "#2B7BEA",
        "learn": ["Choose between two paths with <b>when</b>", "Compare values", "Combine conditions with <b>and</b>, <b>or</b> and <b>not</b>", "Give more than two choices"],
        "blocks": [
            {"type": "p", "text": "Computers are very good at making decisions, as long as you tell them the rules. A <b>when</b> block runs only if its <b>condition</b> is true. A condition is a question that has a yes or no answer."},
            {"type": "bubble", "text": "If it is raining, take an umbrella. Otherwise, wear a hat! Let's make a computer do that."},
            {"type": "code", "src": 'make age = 10\nwhen age >= 10 {\n    say "You can join the club!"\n} otherwise {\n    say "Come back when you are 10."\n}',
             "out": "You can join the club!"},
            {"type": "p", "text": "Look closely at the shape. The code inside the first pair of braces <b>{ }</b> runs when the condition is true. The code after <b>otherwise</b> runs when it is false. Every line inside the braces is indented, which means it is pushed in by four spaces. Indenting makes the code easier to read."},
            {"type": "h", "text": "Comparing values"},
            {"type": "table", "rows": [
                ["==", "is equal to"], ["!=", "is not equal to"], ["&lt;", "is less than"],
                ["&lt;=", "is less than or equal to"], ["&gt;", "is greater than"], ["&gt;=", "is greater than or equal to"],
            ]},
            {"type": "p", "text": "Each of these gives <b>true</b> or <b>false</b>. Try <b>say 5 == 5</b> in your own program."},
            {"type": "h", "text": "Joining conditions"},
            {"type": "code", "src": 'make sunny = true\nmake warm = false\nwhen sunny and not warm {\n    say "Let\'s go to the park!"\n}\nwhen sunny or warm {\n    say "Pack some sunscreen."\n}',
             "out": "Let's go to the park!\nPack some sunscreen."},
            {"type": "p", "text": "<b>and</b> needs both sides to be true. <b>or</b> needs at least one side to be true. <b>not</b> turns true into false and false into true."},
            {"type": "h", "text": "More than two choices"},
            {"type": "code", "src": 'make score = 72\nwhen score >= 90 {\n    say "Excellent!"\n} otherwise when score >= 70 {\n    say "Well done!"\n} otherwise {\n    say "Keep practising."\n}',
             "out": "Well done!"},
            {"type": "p", "text": "SaiLang checks each condition in order. As soon as one is true, it runs that block and skips the rest."},
            {"type": "watch", "text": "A condition must be exactly <b>true</b> or <b>false</b>. A program that says <b>when 5 { }</b> will stop with an error, because 5 is not a yes or no answer. Use a comparison such as <b>when 5 &gt; 0</b> instead."},
            {"type": "try", "title": "Try it!", "steps": [
                "Make a variable called temperature. Say \"Hot\" if it is above 25, and \"Cool\" otherwise.",
                "Ask the user for a number and say whether it is even. Hint: a number is even when <b>number % 2</b> is 0.",
            ]},
        ],
    },
    {
        "num": 4,
        "title": "Doing things again",
        "colour": "#FF4FA3",
        "learn": ["Repeat actions with <b>repeat</b>", "Keep going while something is true with <b>while</b>", "Visit every item with <b>for each</b>", "Skip and stop loops"],
        "blocks": [
            {"type": "p", "text": "Humans get bored doing the same thing many times. Computers never do. A <b>loop</b> is a block of code that repeats. SaiLang has three kinds of loops, and you can choose the one that fits your job best."},
            {"type": "bubble", "text": "Clap your hands three times with me. Clap! Clap! Clap!"},
            {"type": "h", "text": "Repeat a set number of times"},
            {"type": "code", "src": 'repeat 3 times {\n    say "Clap!"\n}', "out": "Clap!\nClap!\nClap!"},
            {"type": "code", "src": 'make total = 0\nrepeat 4 times {\n    total = total + 10\n}\nsay "Total:", total',
             "out": "Total: 40"},
            {"type": "h", "text": "Keep going while it is true"},
            {"type": "p", "text": "A <b>while</b> loop checks its condition before every pass. As long as the condition is true, the loop keeps going."},
            {"type": "code", "src": 'make count = 3\nwhile count > 0 {\n    say count\n    count = count - 1\n}\nsay "Blast off!"',
             "out": "3\n2\n1\nBlast off!"},
            {"type": "watch", "text": "If the condition never becomes false, the loop never ends. Make sure something inside the loop changes the condition. Press <b>Esc</b> in SaiLang IDLE to stop a program that is stuck."},
            {"type": "h", "text": "Visit every item"},
            {"type": "code", "src": 'for each colour in ["red", "green", "blue"] {\n    say "The colour is", colour\n}',
             "out": "The colour is red\nThe colour is green\nThe colour is blue"},
            {"type": "p", "text": "<b>range(1, 4)</b> makes the numbers 1, 2 and 3. It stops <i>before</i> the second number, so it never includes 4. Use it with <b>for each</b> to count."},
            {"type": "code", "src": 'for each number in range(1, 4) {\n    say number\n}', "out": "1\n2\n3"},
            {"type": "h", "text": "Skip and stop"},
            {"type": "p", "text": "<b>skip</b> jumps straight to the next pass of the loop. <b>stop</b> leaves the loop completely. This program prints the odd numbers and stops after 6."},
            {"type": "code", "src": 'make n = 0\nwhile true {\n    n = n + 1\n    when n > 6 {\n        stop\n    }\n    when n % 2 == 0 {\n        skip\n    }\n    say n\n}',
             "out": "1\n3\n5"},
            {"type": "try", "title": "Try it!", "steps": [
                "Write a times table: make a variable called number, set it to 7, then use repeat to say 7 times 1, 2, 3 up to 10.",
                "Use a loop to say \"I love coding\" five times, numbering each line.",
            ]},
            {"type": "fun", "text": "Your computer can repeat a loop millions of times in the blink of an eye. That is why loops are so useful for games."},
        ],
    },
    {
        "num": 5,
        "title": "Lists",
        "colour": "#8A4FFF",
        "learn": ["Keep many values in one list", "Read, change, add and remove items", "Loop through a list", "Build a list while you loop"],
        "blocks": [
            {"type": "p", "text": "A <b>list</b> keeps many values together in one variable. Think of it as a row of lockers. Each locker has a number, called its <b>position</b>, and the first locker is number 0."},
            {"type": "code", "src": 'make pets = ["cat", "dog", "fish"]\nsay pets\nsay pets[0]\nsay length(pets)',
             "out": '["cat", "dog", "fish"]\ncat\n3'},
            {"type": "table", "rows": [
                ["pets[0]", "the first item, which is \"cat\""],
                ["pets[1]", "the second item, which is \"dog\""],
                ["length(pets)", "how many items there are: 3"],
            ]},
            {"type": "watch", "text": "Positions start at 0, not 1. The last item of a three-item list is at position 2. Asking for position 3 causes an error, because that locker is empty."},
            {"type": "h", "text": "Adding, changing and removing"},
            {"type": "code", "src": 'make items = ["sword", "map"]\nappend(items, "key")\nitems[0] = "shiny sword"\nremove_at(items, 1)\nsay items\nsay contains(items, "key")',
             "out": '["shiny sword", "key"]\ntrue'},
            {"type": "p", "text": "<b>append</b> adds to the end. <b>items[0] = ...</b> changes one item. <b>remove_at</b> takes one item out. <b>contains</b> tells you whether an item is in the list."},
            {"type": "h", "text": "Adding up a list"},
            {"type": "code", "src": 'make scores = [5, 8, 3, 9]\nmake total = 0\nfor each s in scores {\n    total = total + s\n}\nsay "Total:", total\nsay "Best:", max(scores)',
             "out": "Total: 25\nBest: 9"},
            {"type": "h", "text": "Building a list while you loop"},
            {"type": "code", "src": 'make squares = []\nfor each n in range(1, 5) {\n    append(squares, n * n)\n}\nsay squares',
             "out": "[1, 4, 9, 16]"},
            {"type": "p", "text": "The empty square brackets <b>[]</b> make a list with nothing in it yet. Each pass of the loop adds a new square to the end."},
            {"type": "tip", "text": "Joining a list into text is easy with <b>join</b>. Try <b>say join([\"a\", \"b\", \"c\"], \"-\")</b>. It prints a-b-c."},
            {"type": "try", "title": "Try it!", "steps": [
                "Make a shopping list with four items. Remove one, add a new one, and say the list.",
                "Make a list of five numbers. Say the largest and the smallest, using max and min.",
            ]},
            {"type": "fun", "text": "Lists can hold other kinds of values too, such as numbers and true or false. A list can even hold a mix of them."},
        ],
    },
]
