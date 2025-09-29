# Patient Vitals API

A FastAPI application that provides access to patient vital signs data with index-based retrieval.

## Features

- Get the i-th vital point for all 8 patients
- Get the (i-1)-th vital point for all 8 patients  
- Increment the current index with automatic reset to 0 when reaching the end
- Status endpoint to check current state

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET `/`
- Returns basic API information and current index

### GET `/vitals/current`
- Returns the i-th vital point for all patients
- Response includes all patient information except the full vitals array (only the current vital point)

### GET `/vitals/previous` 
- Returns the (i-1)-th vital point for all patients
- Handles wraparound (when i=0, returns the last vital point)

### POST `/vitals/increment`
- Increments the current index by 1
- Automatically resets to 0 when reaching the end of vitals
- Returns the new index

### GET `/vitals/status`
- Returns current status including index, total vitals count, and patient count

## Usage Example

1. Start the server: `python main.py`
2. Get current vitals: `GET http://localhost:8000/vitals/current`
3. Increment index: `POST http://localhost:8000/vitals/increment`
4. Get new current vitals: `GET http://localhost:8000/vitals/current`
5. Get previous vitals: `GET http://localhost:8000/vitals/previous`

## Data Structure

Each patient response includes:
- Identifier: Patient ID
- Name: Patient name
- Bed: Bed assignment
- Gender: Patient gender
- Age: Patient age
- Vital: Single vital point with time, pulse, blood pressure, respiration rate, SpO2, and temperature

