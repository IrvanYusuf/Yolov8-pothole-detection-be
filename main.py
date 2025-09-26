import cv2
import json
import tempfile
import os
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import bisect
from fastapi.middleware.cors import CORSMiddleware
import uuid
from controllers.detection_controller import DetectionController


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

output_dir = "frames_output"
os.makedirs(output_dir, exist_ok=True)


def find_nearest_location(locations, ts):
    timestamps = [loc["timestamp"] for loc in locations]
    pos = bisect.bisect_left(timestamps, ts)
    if pos == 0:
        return locations[0]
    if pos == len(timestamps):
        return locations[-1]
    before, after = locations[pos-1], locations[pos]
    return before if abs(before["timestamp"] - ts) < abs(after["timestamp"] - ts) else after


@app.get("/api/")
def hello():
    return JSONResponse({"message": "success"})


@app.post("/api/upload")
async def upload(video: UploadFile, coords: str = Form(...), startTime: int = Form(...)):
    video_path = None
    try:
        if not coords or not startTime:
            raise ValueError("Data 'coords' and 'startTime' are required.")

        coords_data = json.loads(coords)
        if not isinstance(coords_data, list) or not all(isinstance(d, dict) for d in coords_data):
            raise TypeError("'coords' must be a list of dictionaries.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            contents = await video.read()
            tmp.write(contents)
            video_path = tmp.name

        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            raise IOError(
                "Failed to save the video file or the file is empty.")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError("Could not open the video file.")

        frames_with_coords = []

        fps_in = cap.get(cv2.CAP_PROP_FPS)
        # ambil jumlah (misal 10 atau 5) frame tiap X frame asli
        fps_out = 5
        index_in = -1
        index_out = -1

        index = 1

        frames_with_coords = []

        while True:
            success = cap.grab()
            if not success:
                break
            index_in += 1

            out_due = int(index_in / fps_in * fps_out)
            if out_due > index_out:
                success, frame = cap.retrieve()
                if not success:
                    break
                frame_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                frame_time = startTime + int(frame_msec)

                nearest_loc = find_nearest_location(coords_data, frame_time)
                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                # frame_filename = f"frame_{uuid.uuid4()}_{frame_time}.jpg"
                frame_filename = f"frame_0{index}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                cv2.imwrite(frame_path, frame)
                frames_with_coords.append({
                    "frame": frame_number,
                    "frame_time": frame_time,
                    "latitude": nearest_loc["latitude"],
                    "longitude": nearest_loc["longitude"],
                    "image_path": frame_path
                })
                index_out += 1
                index += 1
        # for frame_idx in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        #     ret, frame = cap.read()
        #     if not ret:
        #         break

        #     frame_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        #     if frame_msec - last_capture_time >= interval_ms:
        #         # simpan frame
        #         frame_time = startTime + int(frame_msec)
        #         nearest_loc = find_nearest_location(coords_data, frame_time)
        #         frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        #         frame_filename = f"frame_{uuid.uuid4()}_{frame_number}_{frame_time}.jpg"
        #         frame_path = os.path.join(output_dir, frame_filename)
        #         cv2.imwrite(frame_path, frame)
        #         frames_with_coords.append({
        #             "frame": frame_number,
        #             "frame_time": frame_time,
        #             "latitude": nearest_loc["latitude"],
        #             "longitude": nearest_loc["longitude"],
        #             "image_path": frame_path
        #         })
        #         last_capture_time = frame_msec

        cap.release()
        return JSONResponse(content=frames_with_coords)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format for 'coords' parameter.")
    except (ValueError, TypeError, IOError) as e:
        raise HTTPException(
            status_code=422, detail=f"Data processing error: {e}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@app.post("/api/detection/image")
async def detection_image(image: UploadFile,
                          latitude: float = Form(...),
                          longitude: float = Form(...),):
    return await DetectionController.detection_image(image, latitude, longitude)
