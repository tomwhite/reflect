A trivial one block puzzle. Basically just an introduction to the notation. (puzzle-001)

....A.
......
A.../.
......
......
......

Two blocks. Again, trivial. (puzzle-002)

...BA.
......
......
B../\A
......
......

Same solution, different clues. This one is harder as you have to use A first, then B. (puzzle-003)

....A.
......
......
.../\A
......
...BB.

Decoy (beam C gives no extra info)

....A.
......
......
.../\A
C....C
...BB.

Three blocks, //\. Hmm, can't distinguish these two! And there's no way to give
extra information to distinguish them (e.g. another beam).

....B.  ....B.
......  ......
.../\B  .../.B
A.../.  A..\/.
......  ......
...A..  ...A..

OK, another go. \\\ This one seems unique. Not trivial, but pretty easy? (puzzle-004)
(How can we find if a solution is unique? For 5 symbols there are 16*15*14*13*12 = 5*10^5 possibilities - may be possible to check them.)

....A.
......
B..\..
C..\\A
......
...CB.

Spacing. \\\ (puzzle-2023-04-03)

..CDA.
B\....
......
.\..\A
......
..CDB.

Note presence of C and D makes the puzzle easier. (But leaving them out makes it not unique, so need to include them.)

More blocks - add a ball. /\o
Interesting thing is that now A and B reflect onto themselves. But not in an obvious way! (puzzle-006)

...DA.
......
D../.C
...o\A
......
....B.

Another one, which this time is *not* unique. The ball (o) can move down one square.
(This was found with a brute force solver.) I can't see a way of making this unique by specifying more
beams, so it's an example of a puzzle that we can't use.

..B...
......
Do\..B
C./...
......
.A....

Four blocks, ////. Not sure how easy this is (I set it!).
I originally set it with just A-C, and had to add D and E to make it unique, after running
through a solver.

.D.C..
..//.E
D//..B
A....A
......
.CBE..

Four blocks //\\. Beam A is tricky.
(What does uniqueness mean? We could put the blocks from the A row in the row below,
and be consistent with all the beams. Hmm. Also could move to row B - puzzle is not unique!)

...C..
./.\.C
B....B
A/.\.A
......
......

Better version? (2023-04-05, was puzzle-008)

...C..
./.\.C
B....B
A/...D
...\.A
.D....

(I need a program to test uniqueness that can run quickly! Update: I wrote one, and confirmed
that this last one is unique.)

Five blocks

.A.CA.
B.\...
B./..D
.\../.
E.\..D
..EC..

.AAC..
B.\.\.
B./..D
.\../F
E....E
..DCF.

But last one has two solutions, and can't be made unique.

Six blocks, ///\oo

Based on the a puzzle from my original ST game. See the image:
colour changer dropped, rotate pieces changed to mirrors, and
the horizontal mirror to a ball. Not sure how easy it is,
or if it's unique.

.DE...
H..\o.
D//..G
C..o..
A.../B
.EGFB.

Update: it's not unique, and can't be made so, due to the multiple balls:

.DEIL.
H..\oJ
D//..G
C..o.K
A.../B
.EGFB.
