"""Mirror Klipper position updates into the Gazebo position controller."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from pentos_klipper_bridge.klipper_status import (
    BridgePosition,
    extract_status_update,
    status_to_bridge_position,
    subscription_request,
)

try:
    import websockets
except ImportError:  # pragma: no cover - exercised in runtime environments
    websockets = None


LOGGER = logging.getLogger(__name__)
DEFAULT_COMMAND_TOPIC = "/pentos_position_controller/commands"
DEFAULT_MOONRAKER_URL = "ws://127.0.0.1:7125/websocket"


class MoonrakerPositionClient:
    """Background Moonraker websocket client that stores the latest pose."""

    def __init__(
        self,
        url: str,
        a_default: float,
        b_default: float,
        reconnect_delay: float,
        logger: logging.Logger,
    ) -> None:
        self.url = url
        self.a_default = a_default
        self.b_default = b_default
        self.reconnect_delay = reconnect_delay
        self.logger = logger
        self._lock = threading.Lock()
        self._position: BridgePosition | None = None
        self._last_update_monotonic: float | None = None
        self._connected = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if websockets is None:
            raise RuntimeError(
                "Python package 'websockets' is required for the Klipper bridge"
            )
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def snapshot(self) -> tuple[BridgePosition | None, float | None, bool]:
        with self._lock:
            return self._position, self._last_update_monotonic, self._connected

    def _set_connected(self, connected: bool) -> None:
        with self._lock:
            self._connected = connected

    def _set_position(self, position: BridgePosition) -> None:
        with self._lock:
            self._position = position
            self._last_update_monotonic = time.monotonic()

    def _run_loop(self) -> None:
        asyncio.run(self._connect_forever())

    async def _connect_forever(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self._connect_once()
            except Exception as exc:  # pragma: no cover - network integration
                self.logger.warning("Moonraker websocket disconnected: %s", exc)
            self._set_connected(False)
            await asyncio.sleep(self.reconnect_delay)

    async def _connect_once(self) -> None:
        assert websockets is not None
        async with websockets.connect(self.url) as websocket:
            self._set_connected(True)
            self.logger.info("Connected to Moonraker at %s", self.url)
            await websocket.send(json.dumps(subscription_request()))
            while not self._stop_event.is_set():
                try:
                    raw_message = await asyncio.wait_for(websocket.recv(), timeout=0.25)
                except asyncio.TimeoutError:
                    continue
                message = json.loads(raw_message)
                status = extract_status_update(message)
                if status is None:
                    continue
                position = status_to_bridge_position(
                    status,
                    a_default=self.a_default,
                    b_default=self.b_default,
                )
                if position is not None:
                    self._set_position(position)


class KlipperGazeboBridge(Node):
    """ROS node that publishes Klipper positions to Gazebo."""

    def __init__(self) -> None:
        super().__init__("klipper_gazebo_bridge")
        self.declare_parameter("moonraker_url", DEFAULT_MOONRAKER_URL)
        self.declare_parameter("publish_rate_hz", 20.0)
        self.declare_parameter("a_default", 0.0)
        self.declare_parameter("b_default", 0.0)
        self.declare_parameter("command_topic", DEFAULT_COMMAND_TOPIC)
        self.declare_parameter("stale_timeout_sec", 1.0)
        self.declare_parameter("reconnect_delay_sec", 2.0)

        moonraker_url = self.get_parameter("moonraker_url").value
        publish_rate_hz = max(float(self.get_parameter("publish_rate_hz").value), 1.0)
        a_default = float(self.get_parameter("a_default").value)
        b_default = float(self.get_parameter("b_default").value)
        command_topic = self.get_parameter("command_topic").value
        self.stale_timeout_sec = float(
            self.get_parameter("stale_timeout_sec").value
        )

        self.publisher = self.create_publisher(Float64MultiArray, command_topic, 10)
        self.client = MoonrakerPositionClient(
            url=str(moonraker_url),
            a_default=a_default,
            b_default=b_default,
            reconnect_delay=float(self.get_parameter("reconnect_delay_sec").value),
            logger=self.get_logger(),
        )
        self.client.start()
        self.timer = self.create_timer(1.0 / publish_rate_hz, self._publish_latest)

    def destroy_node(self) -> bool:
        self.client.stop()
        return super().destroy_node()

    def _publish_latest(self) -> None:
        position, updated_at, connected = self.client.snapshot()
        if position is None or updated_at is None:
            return
        if not connected and time.monotonic() - updated_at > self.stale_timeout_sec:
            return
        self.publisher.publish(Float64MultiArray(data=position.as_list()))


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = KlipperGazeboBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
