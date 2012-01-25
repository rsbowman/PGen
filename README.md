A Simple Parser Generator For Python
====================================

In 1998 I wrote this simple parser generator which takes as input an LL(1) attributed grammar
and outputs a recursive descent parser in python.  I got really excited when I realized
that I could write a description of the input grammar and use the parser generator to generate itself.
To try this cool trick:

> python PGenParser.py < ELL1AttributedGrammar.txt > output_parser1.py
> python output_parser1.py < ELL1AttributedGrammar.txt > output_parser2.py
> diff output_parser1.py output_parser2.py

Diff reports no differences, thus showing that the parser has
generated itself.  This could be made into a very complicated Quine with a little work.  Ha!

This code is licensed under the GPLv3.
