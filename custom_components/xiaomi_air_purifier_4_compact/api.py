"""Local MIoT client for the Xiaomi Smart Air Purifier 4 Compact.

Synchronous (python-miio): the coordinator runs every call in the executor
and serializes them, since the miIO protocol keeps a message id per device.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from miio import Device, DeviceException
from miio.exceptions import DeviceError

from .const import (
    DEVICE_RETRIES,
    DEVICE_TIMEOUT,
    POLLED_PROPERTIES,
    PROPERTIES_PER_REQUEST,
)

_LOGGER = logging.getLogger(__name__)


class PurifierError(Exception):
    """Base error of the purifier client."""


class PurifierConnectionError(PurifierError):
    """The device did not answer (offline, wrong address or wrong token)."""


class PurifierCommandError(PurifierError):
    """The device answered with an error code."""


@dataclass(frozen=True)
class PurifierInfo:
    """Identity of the device, from miIO.info."""

    model: str | None
    mac: str | None
    firmware: str | None
    hardware: str | None


class XiaomiAirPurifier:
    """Minimal MIoT client: miIO.info, get/set properties, actions."""

    def __init__(self, ip: str, token: str, timeout: int = DEVICE_TIMEOUT) -> None:
        """Create the client; no network traffic until the first call."""
        self.ip = ip
        self._device = Device(ip, token, timeout=timeout)

    def _send(self, command: str, parameters: Any) -> Any:
        try:
            return self._device.send(command, parameters, retry_count=DEVICE_RETRIES)
        except DeviceError as err:
            raise PurifierCommandError(str(err)) from err
        except (DeviceException, OSError) as err:
            raise PurifierConnectionError(str(err)) from err

    def info(self) -> PurifierInfo:
        """Read miIO.info (model, MAC address, firmware)."""
        raw = self._send("miIO.info", [])
        if not isinstance(raw, dict):
            raise PurifierCommandError(f"Unexpected miIO.info answer: {raw!r}")
        return PurifierInfo(
            model=raw.get("model"),
            mac=raw.get("mac"),
            firmware=raw.get("fw_ver"),
            hardware=raw.get("hw_ver"),
        )

    def status(self) -> dict[str, Any]:
        """Read all polled properties; missing ones are left out."""
        items = list(POLLED_PROPERTIES.items())
        by_iid = {iids: key for key, iids in items}
        values: dict[str, Any] = {}
        for start in range(0, len(items), PROPERTIES_PER_REQUEST):
            chunk = items[start : start + PROPERTIES_PER_REQUEST]
            request = [{"did": key, "siid": s, "piid": p} for key, (s, p) in chunk]
            answer = self._send("get_properties", request)
            if not isinstance(answer, list):
                raise PurifierCommandError(f"Unexpected answer: {answer!r}")
            for item in answer:
                key = by_iid.get((item.get("siid"), item.get("piid")))
                if key is None:
                    continue
                if item.get("code", 0) == 0 and "value" in item:
                    values[key] = item["value"]
                else:
                    _LOGGER.debug("Property %s not readable: code %s", key, item.get("code"))
        return values

    def set_property(self, siid: int, piid: int, value: Any) -> None:
        """Write one property; raise PurifierCommandError if refused."""
        answer = self._send(
            "set_properties",
            [{"did": f"set-{siid}-{piid}", "siid": siid, "piid": piid, "value": value}],
        )
        code = _first_code(answer)
        if code != 0:
            raise PurifierCommandError(f"Writing {siid}.{piid}={value!r} failed with code {code}")

    def call_action(self, siid: int, aiid: int, in_params: list[Any] | None = None) -> None:
        """Run a MIoT action; raise PurifierCommandError if refused."""
        answer = self._send(
            "action",
            {"did": f"action-{siid}-{aiid}", "siid": siid, "aiid": aiid, "in": in_params or []},
        )
        code = _first_code(answer)
        if code != 0:
            raise PurifierCommandError(f"Action {siid}.{aiid} failed with code {code}")


def _first_code(answer: Any) -> int | None:
    """Error code of a set_properties / action answer (0 = success)."""
    if isinstance(answer, list) and answer and isinstance(answer[0], dict):
        return answer[0].get("code")
    if isinstance(answer, dict):
        return answer.get("code")
    return None
