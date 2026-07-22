FROM osrf/ros:humble-desktop-full

# ── System packages ─────────────────────────────────────────────────
# VNC + window manager, basic dev tools (ROS2 Humble comes from base image)
# NOTE: No Nav2, TurtleBot3, Gazebo, or rosbridge pre-installed.
#       Inductees must install simulation packages themselves.
RUN apt-get update && apt-get install -y --no-install-recommends \
    fluxbox tigervnc-standalone-server \
    python3-pip git curl wget nano \
    sudo gosu \
    && rm -rf /var/lib/apt/lists/*

# ── noVNC (browser-based VNC client) — pinned to release tags ───────
RUN git clone --depth 1 --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone --depth 1 --branch v0.12.0 https://github.com/novnc/websockify /opt/novnc/utils/websockify

# ── Environment ─────────────────────────────────────────────────────
ENV DISPLAY=:1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 6080

WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
