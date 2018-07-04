import argparse
import datetime
import os
import re
import subprocess
import ass
import gpxpy


def get_met_stream(filename):
    outs = subprocess.check_output(['ffprobe', filename], stderr=subprocess.STDOUT).split(b'\n')
    stream = list(filter(lambda s: b'gpmd' in s, outs))[0]
    return re.search(b'\d:\d', stream).group().decode('utf-8')


def extract_met(filename, basename, m):
    subprocess.Popen(['ffmpeg', '-y', '-i', filename, '-codec', 'copy',
        '-map', m, '-f', 'rawvideo', f'{basename}.bin']).wait()


def met_to_gpx(basename):
    subprocess.Popen(['gopro2gpx', '-i', f'{basename}.bin',
        '-o', f'{basename}.gpx']).wait()


def gpx_to_srt(basename):
    with open(f'{basename}.gpx') as f:
        gpx = gpxpy.parse(f)

    date = gpx.tracks[0].segments[0].points[0].time.strftime("%Y-%m-%d")
    subprocess.Popen(['gpsbabel', '-t', '-i', 'gpx', '-f', f'{basename}.gpx',
        '-x', 'track,speed', '-o', f'subrip,format=%s km/h %e m\n{date} %t %l',
        '-F', f'{basename}.srt']).wait()


def srt_to_ssa(basename):
    subprocess.Popen(['ffmpeg', '-y', '-i', f'{basename}.srt', f'{basename}.ssa']).wait()


def fix_ssa_start_end(basename):
    with open(f'{basename}.ssa') as f:
        d = ass.parse(f)
        prev = d.events[0]
        for i in d.events[1:]:
            i.start = prev.end + datetime.timedelta(seconds=2)
            prev = i

    with open(f'{basename}.ssa', 'w') as f:
        d.dump_file(f)


def cleanup(basename):
    subprocess.Popen(['rm', f'{basename}.srt', f'{basename}.bin'])


def cut(filename, ss, to, output_filename, quality=20, encoder='libx264'):
    basename = os.path.splitext(os.path.basename(filename))[0]
    subprocess.Popen(['ffmpeg', '-y', '-ss', ss,
        '-i', f'{basename}.ssa', f'{basename}_seek.ssa']).wait()


    h264_vaapi = ['ffmpeg', '-y', '-init_hw_device',  'vaapi=foo:/dev/dri/renderD128',
        '-hwaccel', 'vaapi', '-hwaccel_output_format', 'vaapi', '-hwaccel_device', 'foo',
        '-ss', ss, '-t', str(to), '-i', f'{basename}.MP4', '-filter_hw_device', 'foo',
        '-vf', f'scale_vaapi=w=1280:h=720  ,hwmap=derive_device=vaapi,format=nv12|vaapi,ass={basename}_seek.ssa,hwmap',
        '-c:v', 'h264_vaapi', '-qp', str(quality), f'{output_filename}.mp4']

    libx264 = ['ffmpeg', '-y' , '-init_hw_device',  'vaapi=foo:/dev/dri/renderD128',
        '-hwaccel', 'vaapi', '-hwaccel_output_format', 'vaapi', '-hwaccel_device', 'foo',
        '-ss', ss, '-t', str(to), '-i', f'{basename}.MP4', '-filter_hw_device', 'foo',
        '-vf', f'deinterlace_vaapi,scale_vaapi=w=1280:h=720,hwdownload,format=nv12,ass={basename}_seek.ssa',
        '-c:v', 'libx264', f'{output_filename}.mp4']

    encoders = {
        'h264': h264_vaapi,
        'libx264': libx264
    }

    subprocess.Popen(encoders[encoder]).wait()


def main(filename):
    basename = os.path.splitext(os.path.basename(filename))[0]
    met = get_met_stream(filename)
    extract_met(filename, basename, met)
    met_to_gpx(basename)
    gpx_to_srt(basename)
    srt_to_ssa(basename)
    fix_ssa_start_end(basename)
    cleanup(basename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', '-i', type=str, nargs='+')
    parser.add_argument('--starttimes', '-ss', type=str, nargs='+')
    parser.add_argument('--to', '-t', type=str , nargs='+')
    parser.add_argument('--output', '-o', type=str, nargs='+')
    args = parser.parse_args()


    if not args.starttimes and not args.to:
        for file in args.inputs:
            main(file)
    else:
        for file, ss, to, filename in zip(args.inputs, args.starttimes, args.to, args.output):
            main(file)
            cut(file, ss, to, filename)

