# Optical blocks game

## Notes

These are my notes on reconstructing the original code.

### Listing 1 (OPTICAL1.LST)

I generated [`OPTICAL1.LST`](OPTICAL1.LST) by taking photos of the original printout, and using my phone's covert to text function. I then fixed the indentation and did some cleanup in a text editor.

Find data lines that don't have 16 items:

```
grep Data OPTICAL1.LST | awk -F "," '{print NF-1}' | grep -v 15
```

When importing the capitalisation is changed, which suggests it was written with an earlier version of GFA Basic, possibly even version 2.

There is a bit of corruption in some of the images - hopefully other listings will iron that out.

The `solve` and `make_move` procedures have not been defined in this listing, even though they are called.

Sound works! (Simple beep)

When running you can click on a block then on the board to add it. Overwriting with another block works too. There's not much more than that in this version.

### Listing 2 (OPTICAL2.LST)

[`OPTICAL2.LST`](OPTICAL2.LST) is definitely after listing 1. Has `make_move`, but not `solve`.

Has some additions written in pencil. Might be interesting to see if they were implemented later.

Found where the corrupted data in listing 1 was and corrected it. Redundant printouts FTW.

### Listing 3 (OPTICAL3.LST)

The last listing, [`OPTICAL3.LST`](OPTICAL3.LST), and the longest. Has a lot more logic in it. Not all the data lines were printed, so assume they haven't changed.

The game works! (However, it is very difficult. I think it would be good to make a simpler version.)

![Optical blocks game running on the Hatari ST emulator](images/st_game.png)

### Running

```
unix2dos OPTICAL1.LST
cp OPTICAL1.LST disk/gfatt36/
```

- Hatari emulator
- Use mono screen in settings.
- Set up C drive as described in Mandelbrot-1989.
