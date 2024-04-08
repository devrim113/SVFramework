#!/usr/bin/env python
import ffmpeg

if __name__ == "__main__":
    video = ffmpeg.input("in.mp4")
    video = ffmpeg.filter(video, "select", "gte(n,5)")
    out_filename = "out.mp4"
    ffmpeg.output(video, out_filename).run()
    print("Output file is " + out_filename)
