# findFrame
Find the same frame in a video without spoiling yourself by skimming the video.

Built specifically for "slicing" a video after filtering out specific portions of it (works decently well for a TV/anime episode with openings or endings). 

You may have to carefully look at the target videos (footage you want to cut) because credits change often, which will affect the SSIM values a lot. Lower the SSIM values to account for this. While manual cutting is faster than using findFrame, findFrame runs in the background (it requires barely any manual attention) and doesn't force you to skim through the source video to look for the target videos.
