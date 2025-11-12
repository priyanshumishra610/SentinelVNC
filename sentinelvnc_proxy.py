#!/usr/bin/env python3
"""
SentinelVNC Proxy - Security Layer for VNC Sessions
Transparent TCP proxy that monitors VNC traffic, detects exfiltration patterns,
and supports containment actions.

This is a security monitoring tool - all attack detection is benign and for testing only.
"""
import socket
import threading
import time
import json
import argparse
import logging
from typing import Dict, Optional, Tuple
from collections import deque
from datetime import datetime
import requests
from urllib.parse import urljoin


class VNCProxy:
    """
    TCP proxy that sits between VNC client and server.
    Monitors traffic and detects exfiltration heuristics.
    """
    
    def __init__(
        self,
        listen_host: str = "0.0.0.0",
        listen_port: int = 5900,
        server_host: str = "localhost",
        server_port: int = 5901,
        alert_url: str = "http://localhost:8000/api/v1/alerts",
        contain_on_alert: bool = False,
        clipboard_threshold_kb: int = 200,
        frameburst_threshold_bytes: int = 10 * 1024 * 1024,  # 10MB
        file_transfer_rate_threshold_kbps: int = 1000,  # 1MB/s
        file_transfer_window_sec: int = 5
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.server_host = server_host
        self.server_port = server_port
        self.alert_url = alert_url
        self.contain_on_alert = contain_on_alert
        
        # Heuristic thresholds
        self.clipboard_threshold_kb = clipboard_threshold_kb
        self.frameburst_threshold_bytes = frameburst_threshold_bytes
        self.file_transfer_rate_threshold_kbps = file_transfer_rate_threshold_kbps
        self.file_transfer_window_sec = file_transfer_window_sec
        
        # Session tracking
        self.sessions: Dict[str, Dict] = {}
        self.contained_sessions = set()
        
        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _generate_session_id(self, client_addr: Tuple[str, int]) -> str:
        """Generate unique session ID."""
        return f"session_{client_addr[0]}_{client_addr[1]}_{int(time.time())}"
    
    def _create_session(self, session_id: str, client_addr: Tuple[str, int]) -> Dict:
        """Create a new session tracking dict."""
        session = {
            "session_id": session_id,
            "client_ip": client_addr[0],
            "client_port": client_addr[1],
            "upstream_ip": self.server_host,
            "upstream_port": self.server_port,
            "start_time": time.time(),
            "client_to_server_bytes": 0,
            "server_to_client_bytes": 0,
            "client_to_server_packets": 0,
            "server_to_client_packets": 0,
            "recent_samples": deque(maxlen=100),  # Last 100 data points
            "last_activity": time.time()
        }
        self.sessions[session_id] = session
        return session
    
    def _check_heuristics(self, session: Dict, direction: str, data_size: int) -> Optional[Dict]:
        """
        Check if heuristics are triggered.
        Returns alert dict if triggered, None otherwise.
        """
        current_time = time.time()
        session["last_activity"] = current_time
        
        # Update counters
        if direction == "client_to_server":
            session["client_to_server_bytes"] += data_size
            session["client_to_server_packets"] += 1
        else:
            session["server_to_client_bytes"] += data_size
            session["server_to_client_packets"] += 1
        
        # Store recent sample
        sample = {
            "timestamp": current_time,
            "direction": direction,
            "bytes": data_size
        }
        session["recent_samples"].append(sample)
        
        # Heuristic 1: Clipboard threshold (client->server burst)
        if direction == "client_to_server":
            # Check for sudden burst in client->server traffic
            recent_samples = list(session["recent_samples"])[-10:]  # Last 10 samples
            recent_client_bytes = sum(
                s["bytes"] for s in recent_samples 
                if s["direction"] == "client_to_server"
            )
            
            if recent_client_bytes > (self.clipboard_threshold_kb * 1024):
                return {
                    "heuristic": "clipboard_exfiltration",
                    "bytes": recent_client_bytes,
                    "threshold_kb": self.clipboard_threshold_kb,
                    "description": f"Client->server burst detected: {recent_client_bytes / 1024:.1f}KB"
                }
        
        # Heuristic 2: Frameburst detection (server->client large frames)
        if direction == "server_to_client":
            if data_size > self.frameburst_threshold_bytes:
                return {
                    "heuristic": "frameburst",
                    "bytes": data_size,
                    "threshold_bytes": self.frameburst_threshold_bytes,
                    "description": f"Large frame burst: {data_size / (1024*1024):.1f}MB"
                }
        
        # Heuristic 3: File-transfer-like detection (sustained high rate)
        if direction == "client_to_server":
            window_start = current_time - self.file_transfer_window_sec
            window_samples = [
                s for s in session["recent_samples"]
                if s["timestamp"] >= window_start and s["direction"] == "client_to_server"
            ]
            window_bytes = sum(s["bytes"] for s in window_samples)
            window_kbps = (window_bytes * 8) / (self.file_transfer_window_sec * 1024)
            
            if window_kbps > self.file_transfer_rate_threshold_kbps:
                return {
                    "heuristic": "file_transfer_like",
                    "bytes": window_bytes,
                    "rate_kbps": window_kbps,
                    "threshold_kbps": self.file_transfer_rate_threshold_kbps,
                    "description": f"Sustained high rate: {window_kbps:.1f} kbps over {self.file_transfer_window_sec}s"
                }
        
        return None
    
    def _send_alert(self, session: Dict, heuristic_alert: Dict) -> Optional[Dict]:
        """Send alert to backend API."""
        alert_payload = {
            "session_id": session["session_id"],
            "client_ip": session["client_ip"],
            "upstream_ip": session["upstream_ip"],
            "timestamp": time.time(),
            "heuristic": heuristic_alert["heuristic"],
            "bytes": heuristic_alert["bytes"],
            "recent_samples": [
                {
                    "timestamp": s["timestamp"],
                    "direction": s["direction"],
                    "bytes": s["bytes"]
                }
                for s in list(session["recent_samples"])[-20:]  # Last 20 samples
            ],
            "session_stats": {
                "client_to_server_bytes": session["client_to_server_bytes"],
                "server_to_client_bytes": session["server_to_client_bytes"],
                "client_to_server_packets": session["client_to_server_packets"],
                "server_to_client_packets": session["server_to_client_packets"],
                "duration_seconds": time.time() - session["start_time"]
            }
        }
        
        try:
            response = requests.post(
                self.alert_url,
                json=alert_payload,
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Alert sent for session {session['session_id']}: {heuristic_alert['heuristic']}")
            
            # Check if backend wants containment
            if result.get("action") == "contain" or self.contain_on_alert:
                return {"action": "contain"}
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send alert: {e}")
            return None
    
    def _handle_client(self, client_socket: socket.socket, client_addr: Tuple[str, int]):
        """Handle a single client connection."""
        session_id = self._generate_session_id(client_addr)
        session = self._create_session(session_id, client_addr)
        
        self.logger.info(f"New session: {session_id} from {client_addr}")
        
        try:
            # Connect to upstream VNC server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.settimeout(30)
            server_socket.connect((self.server_host, self.server_port))
            self.logger.info(f"Connected to upstream server {self.server_host}:{self.server_port}")
            
            # Check if session is already contained
            if session_id in self.contained_sessions:
                self.logger.warning(f"Session {session_id} is contained, closing connection")
                client_socket.close()
                server_socket.close()
                return
            
            # Start bidirectional forwarding
            def forward_data(source: socket.socket, dest: socket.socket, direction: str):
                """Forward data and monitor for heuristics."""
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                        
                        # Check heuristics
                        if session_id not in self.contained_sessions:
                            heuristic_alert = self._check_heuristics(session, direction, len(data))
                            
                            if heuristic_alert:
                                self.logger.warning(
                                    f"Heuristic triggered in {session_id}: {heuristic_alert['heuristic']}"
                                )
                                
                                # Send alert
                                result = self._send_alert(session, heuristic_alert)
                                
                                # Contain if requested
                                if result and result.get("action") == "contain":
                                    self.logger.critical(f"CONTAINING session {session_id}")
                                    self.contained_sessions.add(session_id)
                                    break
                        
                        # Forward data
                        dest.sendall(data)
                        
                except (socket.error, OSError) as e:
                    self.logger.debug(f"Connection closed in {direction} direction: {e}")
                finally:
                    try:
                        source.close()
                        dest.close()
                    except:
                        pass
            
            # Start forwarding threads
            client_to_server_thread = threading.Thread(
                target=forward_data,
                args=(client_socket, server_socket, "client_to_server"),
                daemon=True
            )
            server_to_client_thread = threading.Thread(
                target=forward_data,
                args=(server_socket, client_socket, "server_to_client"),
                daemon=True
            )
            
            client_to_server_thread.start()
            server_to_client_thread.start()
            
            # Wait for threads to complete
            client_to_server_thread.join()
            server_to_client_thread.join()
            
        except socket.error as e:
            self.logger.error(f"Socket error in session {session_id}: {e}")
        except Exception as e:
            self.logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            # Cleanup
            try:
                client_socket.close()
            except:
                pass
            try:
                server_socket.close()
            except:
                pass
            
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            self.logger.info(f"Session {session_id} closed")
    
    def contain_session(self, session_id: str) -> bool:
        """Manually contain a session (called by backend)."""
        if session_id in self.sessions:
            self.contained_sessions.add(session_id)
            self.logger.info(f"Session {session_id} manually contained")
            return True
        return False
    
    def start(self):
        """Start the proxy server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.listen_host, self.listen_port))
        server_socket.listen(10)
        
        self.logger.info(
            f"SentinelVNC Proxy listening on {self.listen_host}:{self.listen_port}"
        )
        self.logger.info(f"Forwarding to {self.server_host}:{self.server_port}")
        self.logger.info(f"Alert URL: {self.alert_url}")
        
        try:
            while True:
                client_socket, client_addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_addr),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            self.logger.info("Shutting down proxy...")
        finally:
            server_socket.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SentinelVNC Security Proxy")
    parser.add_argument("--listen", default="0.0.0.0:5900", help="Listen address:port")
    parser.add_argument("--server", default="localhost:5901", help="Upstream VNC server address:port")
    parser.add_argument("--alert-url", default="http://localhost:8000/api/v1/alerts", help="Backend alert URL")
    parser.add_argument("--contain-on-alert", action="store_true", help="Automatically contain on alert")
    parser.add_argument("--clipboard-threshold-kb", type=int, default=200, help="Clipboard threshold in KB")
    parser.add_argument("--frameburst-threshold-mb", type=int, default=10, help="Frameburst threshold in MB")
    parser.add_argument("--file-transfer-rate-kbps", type=int, default=1000, help="File transfer rate threshold in kbps")
    
    args = parser.parse_args()
    
    # Parse listen address
    listen_host, listen_port = args.listen.rsplit(":", 1)
    listen_port = int(listen_port)
    
    # Parse server address
    server_host, server_port = args.server.rsplit(":", 1)
    server_port = int(server_port)
    
    # Create and start proxy
    proxy = VNCProxy(
        listen_host=listen_host,
        listen_port=listen_port,
        server_host=server_host,
        server_port=server_port,
        alert_url=args.alert_url,
        contain_on_alert=args.contain_on_alert,
        clipboard_threshold_kb=args.clipboard_threshold_kb,
        frameburst_threshold_bytes=args.frameburst_threshold_mb * 1024 * 1024,
        file_transfer_rate_threshold_kbps=args.file_transfer_rate_kbps
    )
    
    proxy.start()


if __name__ == "__main__":
    main()

