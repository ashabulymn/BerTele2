from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.plugins.base import PluginBase

router = APIRouter()


def _info(plugin: PluginBase) -> dict[str, Any]:
    return {
        "plugin_id": plugin.plugin_id,
        "name": plugin.name,
        "version": plugin.version,
        "state": plugin.lifecycle.state.value,
        "started": plugin.lifecycle.active,
    }


def _manager(request: Request):
    manager = getattr(getattr(request.app.state, "container", None), "plugin_manager", None)
    if manager is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Plugin manager unavailable")
    return manager


@router.get("/plugins")
async def list_plugins(request: Request) -> dict[str, Any]:
    manager = _manager(request)
    return {"items": [_info(plugin) for plugin in manager.list_plugins()]}


@router.post("/plugins/{plugin_id}/start")
async def start_plugin(plugin_id: str, request: Request) -> dict[str, Any]:
    manager = _manager(request)
    plugin = manager.get_plugin(plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")
    try:
        await manager.start(plugin_id)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _info(plugin)


@router.post("/plugins/{plugin_id}/stop")
async def stop_plugin(plugin_id: str, request: Request) -> dict[str, Any]:
    manager = _manager(request)
    plugin = manager.get_plugin(plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")
    try:
        await manager.stop_plugin(plugin_id)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _info(plugin)


@router.post("/plugins/{plugin_id}/reload")
async def reload_plugin(plugin_id: str, request: Request) -> dict[str, Any]:
    manager = _manager(request)
    plugin = manager.get_plugin(plugin_id)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")
    try:
        await plugin.on_reload()
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _info(plugin)
