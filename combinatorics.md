## How many Reflect puzzles are there?

### Counting Reflect boards

The number of ways of placing $p$ identical blocks on an $N = n*n$ board is

$${N \choose p} = \frac{N!}{p!(N - p)!}$$

If there are $b$ types of block, then there are $b^p$ ways of choosing $p$ blocks (where order matters), and then the number of ways of placing $p$ blocks on the board is

$$\frac{{b^p}N!}{p!(N - p)!}$$

Take the following example. On an $N = 4*4 = 16$ board, with $p=3$ blocks, and $b=3$ types (represented by `/`, `\`, and `o`), the number of possible placements is

$$
\frac{{b^p}N!}{p!(N - p)!} = \frac{3^3 \cdot 16!}{3!13!}
                           = \frac{27 \cdot 16 \cdot 15 \cdot 14}{6}
                           = 15120
$$

| Number of blocks ($p$) | Number of 4x4 boards |
| ---------------------- | -------------------- |
| 1                      | 48                   |
| 2                      | 1,080                |
| 3                      | 15,120               |
| 4                      | 147,420              |
| 5                      | 1,061,424            |
| 6                      | 5,837,832            |
| 7                      | 25,019,280           |

### Symmetries and equivalence classes

The previous formula for placements counts all boards, even those that would be considered the same under a transformation. For example, the second board below is the first board rotated through 180&deg;:

```
/../  ...\
....  ....
....  ....
\...  /../
```

A typical board belongs to an equivalence class of size eight (the symmetries are those of a square, called the dihedral group $D_4$). However, some have fewer in the class, such as this pair:

```
....  ....
./..  ..\.
../.  .\..
....  ....
```

The following board is an equivalence class of size one, since it in unchanged under the eight transformations:

```
....
./\.
.\/.
....
```

Since it is not easy to count these different cases, we just give the following lower bound for the number of distinct placements:

$$\frac{{b^p}N!}{8p!(N - p)!}$$

For the example above, there are therefore at least 1890 distinct 4x4 boards with 3 blocks.

Using a program to enumerate the different cases, and taking board symmetries into account we get the following:

| Number of blocks ($p$) | Number of 4x4 boards | Number of distinct 4x4 boards |
| ---------------------- | -------------------- | ----------------------------- |
| 1                      | 48                   | 9                             |
| 2                      | 1,080                | 162                           |
| 3                      | 15,120               | 1,971                         |
| 4                      | 147,420              | 18,822                        |
| 5                      | 1,061,424            | 133,569                       |
| 6                      | 5,837,832            | 732,618                       |
| 7                      | 25,019,280           | 3,132,675                     |

### Counting Reflect puzzles

So far, we've only considered block placement, and have ignored beams. A Reflect puzzle has a number of beams around the edges of the board, which may be chosen by the puzzle setter. This means that each board can correspond to a potentially large number of puzzles.

To simplify things, imagine that all beams have been arranged around the edge of the board. The question then becomes, does the puzzle have a unique solution? The answer is not always yes, as the following counterexample shows:

```
.EFBH.  .EFBH.
A....A  A....A
B../\H  B../.H
C.../G  C..\/G
D....D  D....D
.EFCG.  .EFCG.
```

It's also clear that _removing_ beams won't make the puzzle have a unique solution.

To count the number of Reflect puzzles with a unique solution isn't possible using simple formulas like the ones above. It's not even possible to give a lower bound. This question can only really be answered by writing a program to enumerate all the cases, which is what I did to get the following numbers:

| Number of blocks ($p$) | Number of 4x4 boards | Number of distinct 4x4 boards | Number of distinct 4x4 puzzles |
| ---------------------- | -------------------- | ----------------------------- | ------------------------------ |
| 1                      | 48                   | 9                             | 9                              |
| 2                      | 1,080                | 162                           | 156                            |
| 3                      | 15,120               | 1,971                         | 1,572                          |
| 4                      | 147,420              | 18,822                        | 11,172                         |
| 5                      | 1,061,424            | 133,569                       | 49,731                         |
| 6                      | 5,837,832            | 732,618                       | 135,960                        |
| 7                      | 25,019,280           | 3,132,675                     | 217,292                        |
