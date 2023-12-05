# RandomThingsGenerator

Hi. Thankyou for checking out my project.
This project provides an easy syntax for randomized rolling tables for Games like D&D.
You can use an easy (and overkill) syntax to create referenses to other tables, or use local or global varaibles.

# Install

Please install the libraries through `pip install -r requirements.txt`.
Put your tables in a folder with the name `tables` (all tables have to be in the `.tex` format), and you can run the project using `python3 main.py`.

# Calling a table

A table can be called by typing it's name into the command prompt.

# Syntax

The comments (#...) are not part of the syntax!

## Table

```
$Tablename
10 # How many possible outcomes are there
1-9 Hallo # a branch with chance of 9 in 10
10 Welt # Chance of 1 in 10
```

## Table referenz

Referenzes can be uses in Table branches. A table referenze would look like this:

```
$a
1
1 $b$ #This rolls randomly on table b

$b
1
1 Hi!
```

## Quick roll

```
$a
2
1 §R,L,U,D§ # Chosses a random value from set R, L, U, D
2 §2d10§ calculates the result of 2 ten sided dice
```

## Constrains and multipliers

Valid constrains are `<, >, +, -`

```
$a
2
1 $b|>3,+5$ # rolls on table be, only values larger or equal to 3 are possible, and adds 5 to the result
2 $2|b$ # Rolls two different values of table b
```

## Variables

### Global

Global variables can be set with command `.set`, viewed with `.get` and cleared with `.clear`.

```
$a
1
1 $b|>x$ # Rolls on table b with values larger then x. If x is not set, the a user input is used
```

### Local variables

In the follwoing example all occurences of var are replaced.

```
$Tablename[var]
4
1 var # This is replced
2 fvar # This is not replced
3 $var$ # this called the table with the name of the value of var
4 $b|>var$ # var gets replaced by a value
```

Local variables can be set in the input using `Tablename;5` (var would equal 5 in this example).
Or they can be used form other tables like this:

```
$a
1
1 $Tablename;5$ # Sets var for tablename to 5
```