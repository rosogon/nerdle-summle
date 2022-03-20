# nerdle-summe

Just two python scripts to solve
* summle - https://summle.net
* instant and classic nerdle - https://nerdlegame.com/

## Playing summle

summle.py target a,b,c,d,e,f

Example:

    $ python3 summle.py 268 2,2,7,50,100
    Target=268
    Numbers=[2, 2, 7, 50, 100]
    Found solution: (7+2=9, 100+9=109, 109*2=218, 218+50=268)
    Found solution: (50-2=48, 48*7=336, 336/2=168, 168+100=268)
    Found solution: (50-2=48, 48/2=24, 24*7=168, 168+100=268)
    Found solution: (100+2=102, 102+7=109, 109*2=218, 218+50=268)
    Found solution: (100+7=107, 107+2=109, 109*2=218, 218+50=268)
    N solutions = 5



## Playing instant nerdle

Pass the hint as parameter, prefixing the guessed green squares with '_'

    $ python nerdle.py 14=+6_78/
    Template:
         _
    14=+678/

    Solutions:
    6+14/7=8


## Playing classic nerdle

Enter an initial guess in the game (e.g.: 12+35=47)
Then pass the result as parameter, replacing the failed squares for '?',
and prefixing the guesses with '\_'.
The last argument is the set of discarded values (at the bottom)

You will get 5 results at most. Only 100 results are calculated and then sorted
by the number of different used characters.

Run `nerdle.py` again passing the new try as nth parameter and the new set 
of discarded values as last parameter, until you win the game.

Example:

    $ python nerdle.py 12+??=?? 3547
    Tries:
    12+??=??

    Solutions:
    0+16/8=2    <-- entered
    0+16/2=8
    0+18/2=9
    0+18/9=2
    0/61+2=2

    $ python nerdle.py 12+??=?? ?_+_16?_8_=2 35470/
    Tries:
    12+??=??
     __  __
    ?+16?8=2

    Solutions:
    2+12-8=6


