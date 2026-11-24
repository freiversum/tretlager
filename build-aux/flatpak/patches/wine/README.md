# Wine patches

Applied on top of Wine 11.20 in the Flatpak build. They make `IMFSinkWriter` write H.264 MP4
files, which Zwift needs for its video clips (F9, *Video Screenshots*). Without them the first
clip fails with `IMFSinkWriter::Finalize failed, hr=0x80004001`, the file stays at 0 bytes and
after ten failures Zwift turns the feature off.

| Patch | Origin |
|---|---|
| 0001, 0002 | Wine merge request [!10298](https://gitlab.winehq.org/wine/wine/-/merge_requests/10298) by Ziqing Hui (open as of 2026-11-24): run samples through converter and encoder |
| 0003 | Tretlager: `wg_muxer` announces its input streams with a time segment, otherwise mp4mux writes DTS 0 and a bogus PTS |
| 0004 | Tretlager: the winegstreamer media sink sends `MEStreamSinkRequestSample` after starting and after each sample, like native sinks |
| 0005 | Tretlager: `IMFSinkWriter::Finalize()` drains the transforms, waits for the sink, finalizes and shuts it down |
| 0006 | Tretlager: transform output buffers get headroom and 64-byte alignment; with an odd window height (two monitors, 1440×843) the ffmpeg video processor overran the buffer and Zwift crashed |
| 0007 | Tretlager: the video processor (msvproc) scales when input and output sizes differ (bilinear); it used to force the output to the input size, so Zwift's 1440×843 → 1230×720 overran the frame and crashed |
| 0008 | Tretlager: winegstreamer packs unpadded I420/YV12 input like Windows (gst rounded strides to 4 and the luma height to 2, which sheared 1230-wide frames) |

Test: a small MinGW program writes 30–90 frames through `MFCreateSinkWriterFromURL` and calls
`Finalize()`, with NV12 and RGB32 input at 1280×720, 1440×843, 1235×701 and Zwift's case
(RGB32 1440×843 in, H.264 1230×720 out); repeated runs with NVENC (`nvh264enc`) on tinytin produce
valid files with correct duration, timestamps and image (a column gradient stays vertical).

When moving to a newer Wine: check whether upstream merged !10298 or implemented `Finalize`,
then drop the matching patches.
