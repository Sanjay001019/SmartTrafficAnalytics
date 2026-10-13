\# Smart Traffic Analytics



A student project prototype that analyzes selected frames from an uploaded traffic video and simulates traffic signal timings using manually entered vehicle counts.



\## Features



\- Upload a short traffic video.

\- Check up to 10 frames for cars, motorcycles, buses, and trucks.

\- Show detected vehicle counts and estimated traffic density for checked frames.

\- Enter vehicle counts for North, South, East, and West.

\- Simulate green-light timing based on the entered counts.

\- Display vehicle-count and green-time charts.



\## Requirements



\- Python 3.10 or newer

\- The packages listed in `requirements.txt`



\## Setup on Windows



Open PowerShell in this project folder and run:



```powershell

py -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

