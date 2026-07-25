"""Model Context Protocol (MCP) server for EcoSphere AI Building Intelligence."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from backend.mcp.tools import (
    compare_runs_tool,
    history_tool,
    modify_idf_tool,
    optimize_building_tool,
    read_results_tool,
    run_simulation_tool,
)

# Initialize FastMCP Server
mcp_server = FastMCP(
    "EcoSphere Building Intelligence",
    dependencies=["eppy", "fastapi", "sqlalchemy", "pydantic"],
)


@mcp_server.tool()
def run_simulation(
    idf_path: str,
    weather_path: str,
    output_folder: str | None = None,
) -> dict[str, Any]:
    """Run EnergyPlus simulation on specified IDF building model and EPW weather file."""
    return run_simulation_tool(idf_path, weather_path, output_folder)


@mcp_server.tool()
def modify_idf(
    idf_path: str,
    output_path: str,
    cooling_setpoint: float | None = None,
    heating_setpoint: float | None = None,
    lighting_multiplier: float | None = None,
    hvac_schedule_status: str | None = None,
    occupancy_multiplier: float | None = None,
) -> dict[str, Any]:
    """Safely modify setpoint temperatures, lighting levels, or HVAC/occupancy schedules in an IDF file."""
    return modify_idf_tool(
        idf_path=idf_path,
        output_path=output_path,
        cooling_setpoint=cooling_setpoint,
        heating_setpoint=heating_setpoint,
        lighting_multiplier=lighting_multiplier,
        hvac_schedule_status=hvac_schedule_status,
        occupancy_multiplier=occupancy_multiplier,
    )


@mcp_server.tool()
def read_results(output_folder: str) -> dict[str, Any]:
    """Parse CSV simulation results from an EnergyPlus output directory."""
    return read_results_tool(output_folder)


@mcp_server.tool()
def compare_runs(simulation_id_1: int, simulation_id_2: int) -> dict[str, Any]:
    """Compare energy consumption metrics and percentage savings between two simulation runs."""
    return compare_runs_tool(simulation_id_1, simulation_id_2)


@mcp_server.tool()
def history(simulation_id: int) -> dict[str, Any]:
    """Retrieve closed-loop runs, metrics history, and agent decision history for a simulation."""
    return history_tool(simulation_id)


@mcp_server.tool()
def optimize_building(
    simulation_id: int,
    max_iterations: int = 5,
    target_reduction: float = 15.0,
) -> dict[str, Any]:
    """Trigger autonomous multi-agent closed-loop optimization for a completed simulation."""
    return optimize_building_tool(
        simulation_id=simulation_id,
        max_iterations=max_iterations,
        target_reduction=target_reduction,
    )


def run_mcp_server() -> None:
    """Entrypoint to launch the FastMCP server over stdio transport."""
    mcp_server.run()


if __name__ == "__main__":
    run_mcp_server()
