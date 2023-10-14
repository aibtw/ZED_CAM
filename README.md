# ZED_CAM

This is a collection of code snippets grouped in one place to make finding it easier. 

Most of the code snippets are inspired from the [ZED API documentation](https://www.stereolabs.com/docs/), with little modifications. except for [Record/zed_gui_recorder.py](https://github.com/aibtw/ZED_CAM/blob/b4241fe79cd24adda6d291c71785fe32c4ef5f85/Record/zed_gui_recorder.py) which is written from scratch using both ZED API and TK library to facilitate data collection for Smart-Tap project.


|      Directory  | Purpose                      |
|----------------|-------------------------------|
|Record 		 |`code snippets for recording (single camera, multiple cameras, GUI interface)`            |
|Stream          |`code snippets for footage streaming (Sender and receiver, or multiple recievers)`            |
|playback          |`Code snippets for viewing an SVO file (normal viewer, skeleton viewer). This includes some helping functions from the ZED Documentation`|
|Skeleton          |`This directory is mainly for human body tracking related code`            |
|postprocessing          |`This directory is mainly for extracting timestamps from multiple (3) svo files and aligning them.`            |




# Recording

To record a video using a single ZED camera: 
```
python3 Record/zed_recorder.py <output/path/.svo> --> Single camera recording
```

To record a video using multiple ZED cameras:
```
python3 Record/zed_multi_recorder.py <output/path/.svo> --> Multiple cameras recording

# Note that you need to provide one path only, and all recordings will share the same name postfixed with a different number to differentiate between it.
```

For data collection for the Smart-Tap project, we use the following script:
```
python3 Record/zed_gui_recorder.py <output/path/>
```

# Post-Processing
To extract timestamps for each frame into csv files, we use:
```
python3 postprocessing/timestamp_extract.py <svo/first/file/path/.svo> <svo/nth/file/path/.svo>
```

Then the output csv files can be aligned using:
```
python3 postprocessing/timestamp_align.py <svo/first/file/path/.csv> <svo/nth/file/path/.csv>
```
