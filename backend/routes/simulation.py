"""Simulation upload, execution, status, and result APIs."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.config import Settings, get_settings
from backend.database.database import get_db
from backend.database.models import Simulation
from backend.models.response_models import SimulationResponse, SimulationResultsResponse
from backend.services.energyplus_service import EnergyPlusService, get_energyplus_service
from backend.utils.exceptions import EcoSphereError, SimulationError
from backend.utils.helpers import create_directory, current_timestamp, generate_uuid
from backend.utils.logger import get_logger

router = APIRouter(prefix="/simulation", tags=["Simulation"])
logger = get_logger(__name__)


async def _save_upload(upload: UploadFile, destination: Path, expected_extension: str) -> Path:
    """Validate and save an uploaded EnergyPlus input file."""
    filename = upload.filename or ""
    if Path(filename).suffix.lower() != expected_extension:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Expected a {expected_extension} file",
        )
    content = await upload.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is empty")
    create_directory(destination.parent)
    destination.write_bytes(content)
    return destination


@router.post("/run", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def run_simulation(
    building_name: str = Form(..., min_length=1, max_length=255),
    idf_file: UploadFile = File(..., description="EnergyPlus IDF building model"),
    weather_file: UploadFile = File(..., description="EnergyPlus EPW weather file"),
    database_session: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    service: EnergyPlusService = Depends(get_energyplus_service),
) -> Simulation:
    """Upload inputs, run EnergyPlus, parse results, and persist the outcome."""
    upload_id = generate_uuid()
    uploaded_idf = await _save_upload(
        idf_file, settings.upload_directory / "idf" / f"{upload_id}.idf", ".idf"
    )
    uploaded_weather = await _save_upload(
        weather_file, settings.upload_directory / "weather" / f"{upload_id}.epw", ".epw"
    )
    simulation = Simulation(
        building_name=building_name,
        status="running",
        idf_file=str(uploaded_idf),
        weather_file=str(uploaded_weather),
    )
    database_session.add(simulation)
    database_session.commit()
    database_session.refresh(simulation)

    output_folder = settings.output_directory / f"simulation_{simulation.id:06d}"
    simulation.output_folder = str(output_folder)
    database_session.commit()
    logger.info("Simulation started: id=%s", simulation.id)
    try:
        service.run_simulation(uploaded_idf, uploaded_weather, output_folder)
        energy = service.read_results(output_folder)
        simulation.electricity = energy["electricity"]
        simulation.cooling = energy["cooling"]
        simulation.heating = energy["heating"]
        simulation.hvac = energy["hvac"]
        simulation.total_energy = energy["electricity"]
        simulation.status = "completed"
        simulation.finished_at = current_timestamp()
        database_session.commit()
        database_session.refresh(simulation)
        logger.info("Simulation finished: id=%s", simulation.id)
        return simulation
    except EcoSphereError:
        simulation.status = "failed"
        simulation.finished_at = current_timestamp()
        database_session.commit()
        logger.exception("Simulation failed: id=%s", simulation.id)
        raise
    except Exception as error:
        simulation.status = "failed"
        simulation.finished_at = current_timestamp()
        database_session.commit()
        logger.exception("Simulation failed unexpectedly: id=%s", simulation.id)
        raise SimulationError("Simulation failed unexpectedly") from error


@router.get("/status/{simulation_id}", response_model=SimulationResponse)
def simulation_status(simulation_id: int, database_session: Session = Depends(get_db)) -> Simulation:
    """Return the current state and metadata for a simulation."""
    simulation = database_session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")
    return simulation


@router.get("/results/{simulation_id}", response_model=SimulationResultsResponse)
def simulation_results(
    simulation_id: int, database_session: Session = Depends(get_db)
) -> SimulationResultsResponse:
    """Return parsed energy results for a completed simulation."""
    simulation = database_session.get(Simulation, simulation_id)
    if simulation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation not found")
    if simulation.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Results are unavailable while simulation status is '{simulation.status}'",
        )
    return SimulationResultsResponse(
        status=simulation.status,
        energy={
            "total_energy": simulation.total_energy,
            "electricity": simulation.electricity,
            "cooling": simulation.cooling,
            "heating": simulation.heating,
            "hvac": simulation.hvac,
        },
    )
