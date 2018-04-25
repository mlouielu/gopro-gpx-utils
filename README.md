GoPro GPX Utils
---------------

Dealing GPX data from GoPro Hero 6 / 5

Requirements
============

* [mlouielu/gopro-utils](https://github.com/mlouielu/gopro-utils)
* [mlouielu/gpxgo](https://github.com/mlouielu/gpxgo)
* [mlouielu/gpsbabel](https://github.com/mlouielu/gpsbabel)

Don't ask me why there have three fork......

HOWTO
=====

### Extract GPX from GoPro Video

```
$ go get -u github.com/mlouielu/gopro-utils/bin/gopro2gpx
$ ffmpeg -y -i GX010211.MP4 -codec copy -map 0:2 -f rawvideo GX010211.bin
$ gopro2gpx -i GX010211.bin -o GX010211.gpx
```

### Convert GPX to subrip (srt) file


Git clone down gpsbabel from mlouielu/gpsbabel:speed-up

```
$ git clone https://github.com/mlouielu/gpsbabel
$ cd gpsbabel
$ git checkout speed-up
$ ./configure
$ make -j8
$ ./gpsbabel
GPSBabel Version 1.5.4.  http://www.gpsbabel.org

Usage:
    ./gpsbabel [options] -i INTYPE -f INFILE [filter] -o OUTTYPE -F OUTFILE
    ./gpsbabel [options] -i INTYPE -o OUTTYPE INFILE [filter] OUTFILE
...
```

Convert .gpx to .srt

```
$ ./gpsbabel -t -i /path/to/input.gpx -o subrip -x track,speed -F /path/to/output.srt
$ cat /path/to/output.srt
1
00:00:00,379 --> 00:00:00,654
0.0 km/h   38 m
11:50:30 Lat=24.81410 Lon=120.96907

2
00:00:00,654 --> 00:00:03,459
3.4 km/h   38 m
11:50:30 Lat=24.81411 Lon=120.96907

3
00:00:03,459 --> 00:00:04,009
1.5 km/h   37 m
11:50:33 Lat=24.81411 Lon=120.96907

4
00:00:04,009 --> 00:00:04,979
1.5 km/h   37 m
11:50:34 Lat=24.81411 Lon=120.96907

5
00:00:04,979 --> 00:00:05,439
1.4 km/h   37 m
11:50:34 Lat=24.81411 Lon=120.96907
...
```

Less point in GPX (GoPro have ~18Hz of GPS data)

```
$ ./gpsbabel -t -i gpx -f /path/to/input.gpx -o subrip -x track,speed -x simplify,count=500 -F /path/to/output.srt
```

SCRIPTS
=======

## sub.py

This script will auto extrat gpx data from GoPro Videos. And generate `.ssa` subtitle, `.gpx` GPS data.

### Prerequirements

You should install all the stuff here metion before (3 fork version things, and ffmpeg), and `asspy`, `gpxpy` Python packages.

### HOWTO Use

```
usage: sub.py [-h] [--inputs INPUTS [INPUTS ...]]
$ python sub.py -i GX010010.MP4
...
$ ls
GX010010.MP4 GX010010.ssa GX010010.gpx
```

ffmpeg
======

## Common use (convert to 720p)

```
$ ffmpeg -i GX010010.MP4 -s hd720 -c:v libx264 -crf 23 -preset slow out.mp4
```

## Merge subtitle into the video

```
$ ffmpeg -i GX010010.MP4 -vf 'ass=GX010010.ssa' out.mp4
```

## Cut the video, and with subtitles (2 step)

```
$ ffmpeg -ss 100 -i GX010010.ssa GX010010_seek.ssa
$ ffmpeg -hwaccel vaapi -ss 100 -t 6 -i GX010010.MP4 -vf 'ass=GX010010_seek.ssa' -s hd720 -c:v libx264 -crf 23 -preset slow out.mp4
```
