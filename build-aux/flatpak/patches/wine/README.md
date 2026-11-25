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
| 0009 | Tretlager: `IMFByteStream::Close()` closes the file; with the stub the finished clip stayed locked, Zwift could not reopen it with a source reader (`SaveMovieReader`) and every next clip failed with a sharing violation |
| 0010 | Tretlager: a sink writer shuts down the media sink it created itself when released; a writer that failed early (Zwift's save with an audio stream Wine cannot encode) kept the file locked |
| 0011 | Tretlager: the GStreamer parser hands out packed 4:2:0 frames like Windows; Zwift reads its 1230×720 clip back for the thumbnail and rejected 1330560-byte frames (expected 1328400) |
| 0012 | Tretlager: an AAC encoder MFT in winegstreamer on top of `avenc_aac` (16-bit PCM or float in, raw AAC-LC out, AudioSpecificConfig in `MF_MT_USER_DATA`); `avenc_aac` has no rank, so `wg_transform` falls back to it by name. Zwift saves every clip with an AAC audio stream |
| 0013 | Tretlager: `msauddecmft` registers that encoder as `CLSID_AACMFTEncoder` in `MFT_CATEGORY_AUDIO_ENCODER`, where the sink writer looks for it (an existing DLL, so the build needs no `configure` change) |
| 0014 | Tretlager: AAC types reach the MPEG-4 muxer with `codec_data`, rate and channels (the codec data lost its `HEAACWAVEINFO` prefix on the way, so mp4mux got none) |
| 0015 | Tretlager: each muxer input stream gets a `queue`; mp4mux waits for data on every pad, so the first video sample blocked the thread that also delivers the audio samples (deadlock in `Finalize`) |
| 0016 | Tretlager: each muxed stream starts at its first sample; GStreamer video encoders offset timestamps by 1000 hours, which mp4mux hides with video alone but not next to an audio stream starting at 0 (the video track started 20860 s into the file) |
| 0017 | Tretlager: H.264 encoders run without B-frames, like the native encoder by default. Media Foundation samples carry no decoding timestamp, so with B-frames (x264enc on mostly static content) the muxer got reordered timestamps and stretched the timeline; Zwift clips played at about 11 of 24 frames per second |

Test: a small MinGW program writes 30–90 frames through `MFCreateSinkWriterFromURL` and calls
`Finalize()`, with NV12 and RGB32 input at 1280×720, 1440×843, 1235×701 and Zwift's case
(RGB32 1440×843 in, H.264 1230×720 out); repeated runs with NVENC (`nvh264enc`) on tinytin produce
valid files with correct duration, timestamps and image (a column gradient stays vertical);
like Zwift, the test then reopens the clip with `MFCreateSourceReaderFromURL` and writes the next
clip to the same path.

Audio test: the same program adds an AAC stream (48 kHz stereo, 16-bit PCM or float, a 440 Hz tone
or no samples at all); ffprobe shows H.264 and AAC tracks of equal length starting at 0, and the
decoded tone is 440 Hz. With the real Zwift (2026-11-25, tinytin) `SaveMovieSuccess` and playable
clips in `Videos/Zwift`. The registration happens when Wine updates the prefix (`wineboot`), which it
does on its own after a Wine update.

When the patches change, raise the patch level in the manifest (`post-install` of the wine module
writes `/app/wine/share/tretlager-wine-build`, for example `patches 17`). Tretlager adds it to the
Wine version and runs `wineboot -u` on existing environments; Wine cannot notice the update itself
because all Flatpak files have the timestamp 0.

When moving to a newer Wine: check whether upstream merged !10298 or implemented `Finalize`,
then drop the matching patches.
