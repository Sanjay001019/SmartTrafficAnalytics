import os
import tempfile

import cv2
import pandas as pd
import streamlit as st
from ultralytics import YOLO


st.title("Smart Traffic Analytics")
st.write(
    "Upload a short traffic video for vehicle detection, "
    "or enter counts below to simulate traffic signal timings."
)


@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")


def get_density(count):
    if count <= 5:
        return "Low"
    elif count <= 15:
        return "Medium"
    return "High"


# Vehicle detection from video
st.header("Vehicle detection from video")

uploaded_video = st.file_uploader(
    "Choose a traffic video",
    type=["mp4", "avi", "mov", "mkv"],
)

if uploaded_video is None:
    st.info("Upload a short traffic video to check vehicle detections.")
else:
    file_suffix = os.path.splitext(uploaded_video.name)[1]
    temp_path = None
    video = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_suffix,
        ) as temp_file:
            temp_file.write(uploaded_video.getbuffer())
            temp_path = temp_file.name

        video = cv2.VideoCapture(temp_path)

        if not video.isOpened():
            st.error("Could not open this video. Please try another video.")
        else:
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            if total_frames <= 0:
                st.error("No readable frames were found in the video.")
            else:
                st.write(f"Total video frames: {total_frames}")
                st.write("Up to 10 frames will be checked.")

                sample_count = min(total_frames, 10)
                frame_numbers = sorted(
                    set(
                        int(i * (total_frames - 1) / max(sample_count - 1, 1))
                        for i in range(sample_count)
                    )
                )

                model = load_model()
                vehicle_names = {"car", "motorcycle", "bus", "truck"}
                frame_results = []
                preview_image = None
                progress = st.progress(0)

                for index, frame_number in enumerate(frame_numbers):
                    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    success, frame = video.read()

                    if not success:
                        continue

                    result = model(frame, verbose=False)[0]
                    vehicle_count = 0

                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        object_name = model.names[class_id]

                        if object_name in vehicle_names:
                            vehicle_count += 1

                    frame_results.append({
                        "Frame": frame_number,
                        "Vehicles": vehicle_count,
                        "Traffic density": get_density(vehicle_count),
                    })

                    if preview_image is None:
                        preview_image = result.plot()

                    progress.progress((index + 1) / len(frame_numbers))

                if frame_results:
                    st.subheader("Results by frame")
                    st.dataframe(
                        pd.DataFrame(frame_results),
                        use_container_width=True,
                        hide_index=True,
                    )

                    average_count = sum(
                        item["Vehicles"] for item in frame_results
                    ) / len(frame_results)

                    st.metric(
                        "Average vehicles per checked frame",
                        f"{average_count:.1f}",
                    )
                    st.write(
                        "Average traffic density: "
                        f"**{get_density(round(average_count))}**"
                    )

                    if preview_image is not None:
                        st.subheader("Example detected frame")
                        st.image(
                            cv2.cvtColor(preview_image, cv2.COLOR_BGR2RGB),
                            caption="Detected vehicles are outlined with boxes",
                        )
                else:
                    st.warning("No readable frames were found in the video.")

    finally:
        if video is not None:
            video.release()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# Simulated signal timing
st.header("Traffic signal timing simulation")
st.write(
    "Enter the vehicle count for each direction. "
    "Higher counts receive a longer simulated green light."
)

directions = ["North", "South", "East", "West"]
counts = {}
columns = st.columns(2)

for index, direction in enumerate(directions):
    with columns[index % 2]:
        counts[direction] = st.number_input(
            f"{direction} vehicles",
            min_value=0,
            max_value=500,
            value=10,
            step=1,
            key=f"count_{direction}",
        )

highest_count = max(counts.values())
timing_rows = []

for direction, count in counts.items():
    if highest_count == 0:
        green_seconds = 15
    else:
        # Demo green time ranges from 15 to 45 seconds.
        green_seconds = round(15 + (30 * count / highest_count))

    timing_rows.append({
        "Direction": direction,
        "Vehicles": count,
        "Traffic density": get_density(count),
        "Simulated green (seconds)": green_seconds,
        "Yellow (seconds)": 3,
        "All-red (seconds)": 1,
    })

st.subheader("Simulated signal plan")
st.dataframe(
    pd.DataFrame(timing_rows),
    use_container_width=True,
    hide_index=True,
)

chart_data = pd.DataFrame(timing_rows).set_index("Direction")

st.subheader("Vehicle count by direction")
st.bar_chart(chart_data["Vehicles"])

st.subheader("Simulated green time by direction")
st.bar_chart(chart_data["Simulated green (seconds)"])

st.caption(
    "Simulation only. These timings are for a student project demo "
    "and must not be used to control real traffic signals."
)