# Formal spec

Script files will be plain text documents (.txt) -- in order to attach formatting (e.g. make certain text be bold or different color) and logic (e.g. check if player has done something in order to present certain text, or set some progress indicator once player has made a decision) to the scripts, we need to define a markup language. The goal of this language is to be expressive for writers and unambiguous for programmers to interpret.

## Text formatting

We will want to add styles or colors to our text, to add flavor as well as meaning (e.g. hints for the player).

Use at (`@`) followed by configuration (some word, called a "formatter") followed by text to be formatted wrapped in curly braces (`{}`). Multiple formatters cannot be nested (e.g. `@bold{@blue{some text}}`); however, they can still be combined by joining the formatters with an underscore (e.g. `@bold_blue{some text}`). Do not combine multiple colors.

Examples:
```
There appears to be a bucket Kipp can @blue{pour} something into.
Concerned citizen: I @italic_red{deplore} the state of our society.
```

All possible formatters:
```
@bold
@italic
@underline
@red
@green
@blue
@yellow
@purple
@orange
@cyan
@pink
```

**Note: our game has a black background and white foreground (text) by default.**

## Variable interpolation

In the game there may be values that the player has entered previously that we want to echo back (imagine the player names something), or there may simply be numbers/strings that our game keeps track of that are reflected through the script.

Wrap the variable name in square brackets (`[]`) and it will be replaced with its value.

Examples:
```
Kipp had already tilled the field [numberOfTills] time(s).
```

**Note: See [Setter Logic](#setter-logic) for how to create variables**

## Conditional logic

Sometimes certain text should only appear when a condition has been fulfilled. For example, if a player has an item in his inventory, then an NPC might respond differently.

Use `$if_` followed by the text wrapped in curly brackets (`{}`). An `$if_` statement can be followed by 0 or more `$elif_` statements, which can optionally be followed by an `$else` statement. These statements can be nested.

Examples:
```
$if_inventory_steak{
  Hungry kid: Mmm, I could really go for some fresh meat.
}$elif_inventory_apple{
  Hungry kid: Do you have a snack to spare?
}$else{
  Hungry kid: I'm so hungry...
}
```

## Choices

Sometimes we will present the player a list of choices (particularly for dialogue) to proceed with a certain interaction. For example, an NPC can ask the player how they feel, to which there might be two responses: "Great" and "Terrible."

To create a choice, use `$choice` followed by a list of "choice elements" within curly brackets (`{}`). Each choice element will have the text presented to the player ("option") and the text presented in the feedback window ("result"), separated by a vertical pipe (`|`). The choice elements themselves are also separated by a pipe. Each option should not be very long, nor should they have markup -- it will need to be repeated in the result, so if you'd prefer you can write shortened text in the option (e.g. "Terrible") and the full length text in the result (e.g. "Kipp: I feel like I got trampled on by a herd of buffalo").

Examples:
```
Bill: How are you feeling today?
$choice{
  | Great |
  Kipp: I feel a boundless energy inside of me.
  Bill: Ah, to be young and energetic.

  | Terrible |
  Kipp: I feel like I got trampled on by a herd of buffalo.
  Bill: Yeah, you don't look too hot.
}
```

## Random events

Sometimes we might want events/behaviors to happen randomly to add some nondeterministic flavor. Use `$random` followed by the different events wrapped in curly braces (`{}`) -- each event will be separated by a vertical pipe (`|`). When evaluated, one event will be selected randomly -- each event will be given equal probability.

Examples:
```
$random{
  |Bill: Greetings! Nice weather out today.
  |Bill: Hey there, Kipp. Haven't seen you around lately.
  |Bill: Hi. What did you think of the game yesterday?
   Kipp: Pretty crazy finish.
  |Bill: Hey, I'm in a bit of a hurry. Catch you later.
}
```

## Setter logic

In order for our game to have branching opportunities, we need to keep track of things the player has done, which requires "setting variables."

To create variables within the script, use `$set_` followed by variable name followed by the initial value, all separated by underscores. To only create the variable if it doesn't exist, use `$init_` followed by variable name instead.

Examples:
```
$set_uniClassroomsVisited_0
```

To increment an integer variable, use `$inc_` followed by variable name followed by the delta amount as an integer, all separated by underscores. This amount can be negative to decrease the count as well.

Examples:
```
$inc_uniClassroomsVisited_1
```

To create a variable and allow the player to enter its value, use `$input_` followed by the variable name.

Examples:
```
Bill: What is your name?
$input_KippFakeName
Kipp: [KippFakeName].
Bill: Ah, ok. Hello, [KippFakeName]!
```

## Inventory

Inventory items can be referred to with the same conventions as variables -- to differentiate it in the game logic, though, use "inventory_" followed by the item ID (some unique string).

Examples:
```
$set_inventory_medicine_1
```

The "inventory" and item ID separated by underscores indicates that the game should treat this differently from other variables (e.g. so it will appear in the inventory menu).

## Reactive behaviors

These scripts will be written in text files such that one object (room, person, or thing) will have a corresponding script. Within each file, several "behaviors" are attached to the corresponding object. These behaviors are exposed in the game (i.e. text gets shown) when the player acts by typing some verb through the command window. Therefore, you can think of the game as a series of rooms containing a series of objects that each have a series of reactions.

To define a behavior for an object, at the top level of the file (i.e. outside of any curly braces from other commands) use the verb name, and then within curly braces define the behavior (using everything else from above).

Examples:
```
inspect{
  Bill was a middle-aged man. Kipp knew he had a few stories to tell.
}

talk to{
  Bill: What is your name?
  $input_KippFakeName
  Kipp: [KippFakeName].
  Bill: Ah, ok. Hello, [KippFakeName]!
  Bill: How are you feeling today?
  $choice{
    | Great |
    Kipp: I feel a boundless energy inside of me.
    Bill: Ah, to be young and energetic.

	| Terrible |
	Kipp: I feel like I got trampled on by a herd of buffalo.
	Bill: Yeah, you don't look too hot.
  }
}

pick up{
  Kipp considered lifting Bill up. But that would have been kind of weird.
}
```

Some possible verbs (and what type of objects they'd be attached to) are:
* go to - room ("go to laboratory")
* talk to - NPC ("talk to Bill")
* inspect - NPC, thing ("inspect lamppost")
* pick up - thing ("pick up cigar")
* use `<thing>` on - NPC, thing ("use match on grill")
* use - thing (not specifically applied to anything, like "use torch")
* drop - thing ("drop match")
* look around - room ("look around" -- describes room)
* wait - room ("wait" -- could allow for more description, or event)
* show `<thing>` to - NPC ("show axe to Bob")

Other verbs can be used as need be!
* look at
* listen to
* give <thing> to
* think
* sleep

For an object script, the player can invoke the behavior by typing <verb name> <object name> (e.g. for a "book" object, a "read { ... }" behavior is invoked with "read book"). For a room script, the player invokes the behavior simply with <verb name> (e.g. for a "bedroom" room, the "look around { ... }" behavior is invoked with "look around").

There may be some circumstances in which a verb should not be visible (not be executable) unless certain conditions are fulfilled. In that case, the verb name should be followed with a pipe character (`|`) followed by a underline delimited condition string (see "Conditional Logic" -- the part after `$if_` or `$elif_` is the condition string). For example, suppose there is a "door" object with "open" and "close" verb behaviors defined, and we only want one of them to be executable at a time (i.e. you can only open a door if it is closed, and vice versa). The script may look like:

```
open | doorClosed_eq_0{
  Kipp opened the door.
  $set_doorClosed_1
}

close | doorClosed_eq_1{
  Kipp closed the door.
  $set_doorClosed_0
}
```

## Comments

To add "comments" -- lines that will not be seen in-game but are used to document what the purpose of certain lines of script are for our team -- start a new line with `#`

Examples:
```
#set the number of classroom visit occurrences to zero
$set_uniClassroomsVisited_0
```

## Spacing

Leading and trailing spaces on each line will be ignored. Line breaks will be preserved. Please use indenting to indicate the level of nesting (`{}`) that is occurring, so script is easier to read.

To preserve leading spaces on a line (e.g. to format lines in a specific way for art), use one forward slash character (`\`) at the beginning of the line. This character will not actually be displayed in game. For example:

```
\    3
\ +  2
\-----
\    5
```

## Reserved characters

Because certain characters are reserved for the markup language, do not use them in the actual writing. These characters are: `@, #, $, {, }, [, ], |, _, \`

## Function summary

Note that when angle brackets are used, (i.e. `<something>`, the writer is intended to replace it with the appropriate value.

* `$if_<condition>{<body>}` -- executes `<body>` if the `<condition>` is fulfilled.
  * If checking for the existence of a variable, `<condition>` can just be the variable name.
  * If checking if variable is equal to some value, use `<variable>_eq_<value>`.
    * If variable does not exist when checking value, it will be created and initialized to 0, and then the `<condition>` will be evaluated.
  * If an integer variable exists, `<variable>_lt_<value>` and `<variable>_gt_<value>` will also work for less than and greater than some value, respectively.
  * If checking for existence of inventory item, use `inventory_itemid` -- the above points regarding integer comparisons also apply.
* `$elif_<condition>{<body>}` -- (short for else if) follows an `$if` or `$elif`, and executes `<body>` if `<condition>` is fulfilled and the condition(s) of the preceding if(s) is not. Same condition rules apply.
* `$else{<body>}` -- follows an `$if` or `$elif`, and executes `<body>` if condition(s) for preceding if(s) was not fulfilled.
* `$choice{<option1> | <result1> | <option2> | <result2> | ... | <optionn> | <resultn>}` -- displays n options to the player and executes the corresponding result depending on the selection. The option cannot contain logic (but can contain formatters), while the result can include formatters and functions. There can at most 5 option/result pairs specified in one `$choice`.
* `$random{<result1> | <result2> | ... | <resultn>}` -- executes one of the n results randomly, applying equal weight to each possibility.
* `$set_<variable>_<value>` -- creates a variable (named `<variable>`) that can be accessed from any script file and sets it to value. The value can be a string or an integer. The variable continues to exist after execution of the current script, so it can be accessed later, and in other files.
  * If modifying the user inventory, use `inventory_<itemid>` in place of `<variable>`.
* `$init_<variable>` -- creates `<variable>` if it does not exist and initializes it to a default value (0).
* `$inc_<variable>_<deltaValue>` -- modifies an existing `<variable>` by setting it to `<variable> + <deltaValue>`. If `<variable>` does not exist, the function creates the variable and sets its value to `<deltaValue>`. The `<deltaValue>` and the existing variable must be integers (`<deltaValue>` can be positive or negative).
    * `$add` is an alias for `$inc`
* `$dec_<variable>_<deltaValue>` -- modifies an existing `<variable>` by setting it to `<variable> - <deltaValue>`. If `<variable>` does not exist, the function creates the variable and sets its value to `-<deltaValue>`. The `<deltaValue>` and existing variable must be integers (`<deltaValue>` can be positive or negative).
    * `$sub` is an alias for `$dec`
* `$input_<variable>` -- creates a variable that the player must initialize through keyboard input.
* `$goto_<roomid>` -- sets the player location directly to the room addressed by `<roomid>`. Only use rooms that are in the same area as where the player currently is -- do not switch areas or outer/inner worlds. This function will not trigger the "go to" behavior of the target room.
* `$unset_<variable>` -- removes an existing variable from the game state.
* `$gameover` -- kicks the player out of the game and into the title screen. The player will not have their progress saved so use sparingly, and with appropriate warnings beforehand. The current script execution will be terminated.
* `$switchcharacter` -- switches the storyline to the other protagonist. The current script execution will be terminated.
* `$fragment_<fragmentid>` -- imports and executes a script fragment located in `assets/scripts/fragments` identified by some `fragmentid`; useful when needing to reuse portions of code in a script.
* `$exit` -- terminates execution of the currently running script; no statements after this function will execute.

## Common variables

Several variables will need to be used across different scripts that different people are writing. To maintain consistency, we need to use the same names for these variables.

* `loreMorality` -- represents Lore's friendliness and ethics, and influences the branch in her story arc as well as end of game decision. Positive is more "good" and negative is more "evil."
* `kippMorality` -- represents Kipp's friendliness and ethics, and influences the end of game decision. Positive is more "good" and negative is more "evil."
* `derelictPts` -- points toward Kipp getting the derelict companion
* `brotherPts` -- points toward Kipp getting the brother companion
* `fugitivePts` -- points toward Kipp getting the fugitive companion

## Style guidelines

Some guidelines for writing consistency:

* Narration is in third person. When the player takes action Y using some character X, the narration that appears in the main window will say something like "X did Y" (not "you did Y" or "I did Y").
* Narration is in past tense. "X did Y", not "X does Y." This should work for most cases, but if other tenses must be used to make sense, then go ahead. (Imagine you're reading a book as you play the game... most narration would be in past tense)
* To describe some game related mechanic in narration, use italics. This should mainly be for inventory, but can also indicate some other type of progress made.

```
@italic{Added potion to inventory.}
@italic{The cellar is accessible.}
```

* To directly speak to the player in narration, use bold. Use this for hints or explanation of gameplay. Refer to player as "you."

```
@bold{You may wish to save now.}
```

* Dialogue takes the form "Speaker: some line" Example below.

```
Kipp: Hello there.
Bill: Nice to meet you, sir.
```

* Dialogue may be in whatever tense is appropriate.
* To describe a nonvocal communication in dialogue, like a sigh or shrug, wrap the phrase in asterisks (*).

```
Kipp: *sigh*
```

* To describe a thought in dialogue (i.e. protagonist thinking to him/herself), wrap the phrase in parentheses. Try to use this only for the protagonists, and not for NPCs.

```
Kipp: (What to do now..?)
```

* To describe a soft vocal communication in dialogue (i.e. character whispering to him/herself), use italics. Italics can also be used for sarcasm or stress/emphasis.

```
Kipp: @italic{Wait a sec..}
```

* To describe a loud vocal communication in dialogue (i.e. character shouting), use bold. To go even louder, use all caps.

```
Kipp: @bold{Watch out!}
```

* When interleaving blocks of dialogue and narration, leave a blank line (i.e. double space) between the blocks so things follow more clearly. Use single spacing within the blocks.

```
Kipp walked into town.

Kipp: Hello there, Bill.
Bill: What's up?

Kipp and Bill exchanged their secret handshake.
```

* Do not hard wrap continuous lines or paragraphs (i.e. do not hit "Enter/Return" yourself to do word wrapping). In Notepad++ you can toggle soft word wrapping with View - Word Wrap, which lets you avoid scrolling horizontally when writing (this achieves an experience closer to MS Word or Google Doc).
* Avoid large blocks of text without interaction from the player. If you find yourself doing that, try inserting a trivial $choice or break up the single interaction into multiple interactions (e.g. if one character says a lot, break up his speech into multiple parts such that the player must talk to him multiple times).
* If making art (e.g. what player sees when inspecting a poster), restrict yourself to 90 columns (i.e. each line is 90 chars or less) and 25 rows (i.e. only 25 lines can be shown at once on screen). If leading spaces are needed in a line to format the art, use a forward slash (`\`) at the start of the line.
* Important info is highlighted with a certain color to give a hint to the player. The choices of color are somewhat arbitrary, but let's try this scheme.
  * People - green
  * Places - blue
  * Verbs (that player can enter as command) - red
  * Interactable objects - yellow
  * Game specific terms - underline (technically not a color)
    * We may want a "glossary" or "dictionary" feature in the game if we invent a lot of our own terminology, so underlined words would indicate things a player can then go look up with a certain command.
* The scripts will have proper indenting for legibility -- when a curly brace opens, increase the indent level, and when it closes, decrease the indent level
* Comment any complex portions of script
* All variables are global across areas in the game (i.e. can be accessed from anywhere), so we want to avoid giving two vars in different files the same name. To avoid that, the first word (three letters) of the variable can be an "area code" -- we will define different codes for each area below. Use these codes if a variable is "linked to" an area (e.g. only used within that area, or originates from that area).
  * Farm: farm
  * Aspire: aspire
  * Black Hills: hills
  * Kappallanoah Forest: forest
  * Meadows: meadows
  * Lake: lake
  * Badlands: badlands
  * Desert: desert
  * Ruins: ruins
  * Suburbs: suburbs
  * University: uni
  * Downtown: downtown
  * Research facility: research
* Variables are camelCase, meaning the first letter is lowercase, and following words start with uppercase. No spaces or underscores are used. Examples below.

```
uniClassroomsVisited
farmNumberCows
```

* We want to aim for quantity -- our game's appeal should be the sense of discovery a player gets when interacting with the world, so write up as many behaviors for as many objects as possible. There are plenty of opportunities to insert humor or wit, and even small behaviors are better than none (if no behavior is defined we will have some default text, like "Nothing happened.")
* Use a text editor with word wrap and some indenting support (i.e. once you indent, the following lines will also be indented). Consider Notepad++ or Atom (I do not recommend working straight off Google Docs).
