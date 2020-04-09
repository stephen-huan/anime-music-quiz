# anime-music-quiz
A bot which automatically plays [animemusicquiz](https://animemusicquiz.com/).
Based off the [Fast Fourier Transform](https://gist.github.com/stephen-huan/aa609965c86d750736398c28b025f9be#fast-fourier-transform),
and minimizes the L2 norm between the given clip and each song in its database.
Future work: make it based off fingerprints, like Shazam.

[Sample run](https://www.youtube.com/watch?v=7fUicc_lIGA)

### Dejavu

This branch uses [DejaVu](https://github.com/worldveil/dejavu) for audio fingerprinting 
and identification, specifically the [fork](https://github.com/mauriciorepetto/dejavu/tree/dejavu_python_3.6.6) 
that uses Python 3.
To initialize DejaVu, run the command
```sql 
CREATE DATABASE IF NOT EXISTS dejavu;
```
In order to clear the database, run 
```sql
DROP DATABASE dejavu;
```
