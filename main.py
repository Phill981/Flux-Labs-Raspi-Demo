from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
import ijson
from functools import lru_cache
from pydantic import BaseModel
import time
from datetime import datetime

app = FastAPI(title="Patient Vitals API", version="1.0.0")

# Global state for tracking current index
current_index = 0
previous_index = 0  # Track the previous index
patients_metadata = None  # Store only metadata, not full data
vitals_length = 0
file_path = 'patients_data.json'
saved_snapshot = None  # Store saved snapshot data
snapshot_id = 0  # Track snapshot identifier

class PatientResponse(BaseModel):
    Identifier: int
    Name: str
    Bed: str
    Gender: str
    Age: int
    Vital: Dict[str, Any]  # Single vital point

class SnapshotResponse(BaseModel):
    identifier: int
    patients: List[PatientResponse]

def load_patients_metadata():
    """Load only patient metadata (not full vitals data) for efficiency"""
    global patients_metadata, vitals_length
    
    try:
        print("Loading patient metadata...")
        start_time = time.time()
        
        # First pass: count total patients and get vitals length from first patient
        with open(file_path, 'rb') as f:
            parser = ijson.parse(f)
            patients_metadata = []
            current_patient = None
            vitals_count = 0
            patient_count = 0
            first_patient_vitals_done = False
            
            for prefix, event, value in parser:
                if prefix.endswith('.Identifier') and event == 'number':
                    if current_patient:
                        patients_metadata.append(current_patient)
                        patient_count += 1
                    current_patient = {'Identifier': value}
                elif current_patient and prefix.endswith('.Name') and event == 'string':
                    current_patient['Name'] = value
                elif current_patient and prefix.endswith('.Bed') and event == 'string':
                    current_patient['Bed'] = value
                elif current_patient and prefix.endswith('.Gender') and event == 'string':
                    current_patient['Gender'] = value
                elif current_patient and prefix.endswith('.Age') and event == 'number':
                    current_patient['Age'] = value
                elif current_patient and prefix.endswith('.Vitals.item') and event == 'start_map':
                    vitals_count += 1
                elif current_patient and prefix.endswith('.Vitals.item') and event == 'end_map':
                    # We've finished a vital entry
                    if patient_count == 0 and not first_patient_vitals_done:
                        # This is the first patient, count their vitals
                        pass
                elif current_patient and prefix.endswith('.Vitals') and event == 'end_array':
                    # We've finished the vitals array for the current patient
                    if patient_count == 0 and not first_patient_vitals_done:
                        vitals_length = vitals_count
                        first_patient_vitals_done = True
                        print(f"First patient has {vitals_length} vital points")
                
                # Continue loading all patients for metadata
                # Don't break early - we need all patient metadata
        
        # Add the last patient if exists
        if current_patient:
            patients_metadata.append(current_patient)
            patient_count += 1
        
        load_time = time.time() - start_time
        print(f"Loaded metadata for {len(patients_metadata)} patients with {vitals_length} vital points each in {load_time:.2f}s")
        
        if not patients_metadata:
            raise ValueError("No patient data found")
            
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Patient data file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading patient metadata: {str(e)}")

def get_vitals_at_index(index: int) -> List[Dict[str, Any]]:
    """Efficiently load vitals data for a specific index using streaming JSON parser"""
    if patients_metadata is None:
        raise HTTPException(status_code=500, detail="Patient metadata not loaded")
    
    vitals_data = []
    
    try:
        # Use ijson.items to get specific vital items
        with open(file_path, 'rb') as f:
            # Parse each patient's vitals array
            patients = ijson.items(f, 'item')
            
            for patient in patients:
                if len(vitals_data) >= len(patients_metadata):
                    break
                    
                # Get the vital at the specific index
                if index < len(patient['Vitals']):
                    vital = patient['Vitals'][index]
                    patient_data = {
                        'Identifier': patient['Identifier'],
                        'Name': patient['Name'],
                        'Bed': patient['Bed'],
                        'Gender': patient['Gender'],
                        'Age': patient['Age'],
                        'Vital': vital
                    }
                    vitals_data.append(patient_data)
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading vitals data: {str(e)}")
    
    return vitals_data

def increment_index():
    """Increment the current index and reset to 0 if it reaches the vitals length"""
    global current_index, previous_index
    previous_index = current_index  # Store current as previous
    current_index = (current_index + 1) % vitals_length
    return current_index

@app.on_event("startup")
async def startup_event():
    """Load patient metadata on startup"""
    load_patients_metadata()

@app.get("/")
async def root():
    return {"message": "Patient Vitals API", "current_index": current_index, "total_vitals": vitals_length}

@app.get("/vitals/current", response_model=List[PatientResponse])
async def get_current_vitals():
    """Get the i-th vital point for all patients"""
    if patients_metadata is None:
        raise HTTPException(status_code=500, detail="Patient metadata not loaded")
    
    if current_index >= vitals_length:
        raise HTTPException(status_code=400, detail="Invalid index")
    
    # Use efficient loading with caching
    vitals_data = get_vitals_at_index(current_index)
    
    # Get current timestamp
    current_timestamp = datetime.now().isoformat()
    
    result = []
    for patient_data in vitals_data:
        # Replace the historical timestamp with current timestamp
        vital_data = patient_data["Vital"].copy()
        vital_data["time"] = current_timestamp
        
        patient_response = PatientResponse(
            Identifier=patient_data["Identifier"],
            Name=patient_data["Name"],
            Bed=patient_data["Bed"],
            Gender=patient_data["Gender"],
            Age=patient_data["Age"],
            Vital=vital_data
        )
        result.append(patient_response)
    
    return result

@app.get("/vitals/previous", response_model=List[PatientResponse])
async def get_previous_vitals():
    """Get the previous vital point for all patients (snapshot of what was current)"""
    if patients_metadata is None:
        raise HTTPException(status_code=500, detail="Patient metadata not loaded")
    
    # Use the stored previous index (snapshot behavior)
    vitals_data = get_vitals_at_index(previous_index)
    
    # Get current timestamp
    current_timestamp = datetime.now().isoformat()
    
    result = []
    for patient_data in vitals_data:
        # Replace the historical timestamp with current timestamp
        vital_data = patient_data["Vital"].copy()
        vital_data["time"] = current_timestamp
        
        patient_response = PatientResponse(
            Identifier=patient_data["Identifier"],
            Name=patient_data["Name"],
            Bed=patient_data["Bed"],
            Gender=patient_data["Gender"],
            Age=patient_data["Age"],
            Vital=vital_data
        )
        result.append(patient_response)
    
    return result

@app.get("/vitals/increment")
async def increment_vital_index():
    """Increment the current vital index and return the new index"""
    new_index = increment_index()
    return {
        "message": "Index incremented successfully",
        "new_index": new_index,
        "total_vitals": vitals_length
    }

@app.get("/vitals/status")
async def get_status():
    """Get current status including index and total vitals count"""
    return {
        "current_index": current_index,
        "previous_index": previous_index,
        "total_vitals": vitals_length,
        "total_patients": len(patients_metadata) if patients_metadata else 0,
        "has_snapshot": saved_snapshot is not None,
        "current_snapshot_id": snapshot_id if saved_snapshot is not None else None
    }

@app.get("/vitals/save")
async def save_current_vitals():
    """Save the current vitals as a snapshot"""
    if patients_metadata is None:
        raise HTTPException(status_code=500, detail="Patient metadata not loaded")
    
    if current_index >= vitals_length:
        raise HTTPException(status_code=400, detail="Invalid index")
    
    # Get current vitals data
    vitals_data = get_vitals_at_index(current_index)
    current_timestamp = datetime.now().isoformat()
    
    # Increment snapshot ID
    global saved_snapshot, snapshot_id
    snapshot_id += 1
    
    # Create snapshot with current timestamp
    saved_snapshot = []
    for patient_data in vitals_data:
        # Replace the historical timestamp with current timestamp
        vital_data = patient_data["Vital"].copy()
        vital_data["time"] = current_timestamp
        
        snapshot_patient = {
            "Identifier": patient_data["Identifier"],
            "Name": patient_data["Name"],
            "Bed": patient_data["Bed"],
            "Gender": patient_data["Gender"],
            "Age": patient_data["Age"],
            "Vital": vital_data
        }
        saved_snapshot.append(snapshot_patient)
    
    return {
        "message": "Current vitals saved as snapshot",
        "snapshot_id": snapshot_id,
        "timestamp": current_timestamp,
        "patients_count": len(saved_snapshot)
    }

@app.get("/vitals/snapshot", response_model=SnapshotResponse)
async def get_saved_snapshot():
    """Get the saved snapshot of vitals"""
    if saved_snapshot is None:
        raise HTTPException(status_code=404, detail="No snapshot saved yet")
    
    # Return the saved snapshot with current timestamp
    current_timestamp = datetime.now().isoformat()
    result = []
    
    for patient_data in saved_snapshot:
        # Update the timestamp to show when snapshot was accessed
        vital_data = patient_data["Vital"].copy()
        vital_data["time"] = current_timestamp
        
        patient_response = PatientResponse(
            Identifier=patient_data["Identifier"],
            Name=patient_data["Name"],
            Bed=patient_data["Bed"],
            Gender=patient_data["Gender"],
            Age=patient_data["Age"],
            Vital=vital_data
        )
        result.append(patient_response)
    
    return {"identifier":snapshot_id,
            "patients": result}

@app.get("/vitals/snapshot/info")
async def get_snapshot_info():
    """Get information about the current snapshot"""
    if saved_snapshot is None:
        raise HTTPException(status_code=404, detail="No snapshot saved yet")
    
    return {
        "snapshot_id": snapshot_id,
        "patients_count": len(saved_snapshot),
        "has_snapshot": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)

