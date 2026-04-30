use serde::{Deserialize, Serialize};

use crate::config::NetworkHostConfig;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum NetworkLifecycleState {
    Off,
    Probing,
    Ready,
    Registering,
    Registered,
    PppStarting,
    Online,
    PppStopping,
    Recovering,
    Degraded,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct SignalSnapshot {
    pub csq: Option<u8>,
    pub bars: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct PppSnapshot {
    pub up: bool,
    pub interface: String,
    pub pid: Option<u32>,
    pub default_route_owned: bool,
    pub last_failure: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct GpsSnapshot {
    pub has_fix: bool,
    pub lat: Option<f64>,
    pub lng: Option<f64>,
    pub altitude: Option<f64>,
    pub speed: Option<f64>,
    pub timestamp: Option<String>,
    pub last_query_result: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct NetworkRuntimeSnapshot {
    pub enabled: bool,
    pub gps_enabled: bool,
    pub config_dir: String,
    pub state: NetworkLifecycleState,
    pub sim_ready: bool,
    pub registered: bool,
    pub carrier: String,
    pub network_type: String,
    pub signal: SignalSnapshot,
    pub ppp: PppSnapshot,
    pub gps: GpsSnapshot,
    pub connected: bool,
    pub gps_has_fix: bool,
    pub connection_type: String,
    pub network_status: String,
    pub gps_status: String,
    pub recovering: bool,
    pub retryable: bool,
    pub reconnect_attempts: u32,
    pub next_retry_at_ms: Option<u64>,
    pub error_code: String,
    pub error_message: String,
    pub updated_at_ms: u64,
}

impl NetworkRuntimeSnapshot {
    pub fn offline(config_dir: &str) -> Self {
        let mut snapshot = Self {
            enabled: false,
            gps_enabled: false,
            config_dir: config_dir.to_string(),
            state: NetworkLifecycleState::Off,
            sim_ready: false,
            registered: false,
            carrier: String::new(),
            network_type: String::new(),
            signal: SignalSnapshot { csq: None, bars: 0 },
            ppp: PppSnapshot {
                up: false,
                interface: String::new(),
                pid: None,
                default_route_owned: false,
                last_failure: String::new(),
            },
            gps: GpsSnapshot {
                has_fix: false,
                lat: None,
                lng: None,
                altitude: None,
                speed: None,
                timestamp: None,
                last_query_result: "idle".to_string(),
            },
            connected: false,
            gps_has_fix: false,
            connection_type: String::new(),
            network_status: String::new(),
            gps_status: String::new(),
            recovering: false,
            retryable: false,
            reconnect_attempts: 0,
            next_retry_at_ms: None,
            error_code: String::new(),
            error_message: String::new(),
            updated_at_ms: 0,
        };
        snapshot.refresh_derived();
        snapshot
    }

    pub fn from_config(config_dir: &str, config: &NetworkHostConfig) -> Self {
        let mut snapshot = Self::offline(config_dir);
        snapshot.enabled = config.enabled;
        snapshot.gps_enabled = config.gps_enabled;
        snapshot.refresh_derived();
        snapshot
    }

    pub fn degraded_config_error(config_dir: &str, error: &str) -> Self {
        let mut snapshot = Self::offline(config_dir);
        snapshot.state = NetworkLifecycleState::Degraded;
        snapshot.retryable = false;
        snapshot.error_code = "config_load_failed".to_string();
        snapshot.error_message = error.to_string();
        snapshot.refresh_derived();
        snapshot
    }

    pub fn refresh_derived(&mut self) {
        self.connected = self.enabled && self.ppp.up;
        self.gps_has_fix = self.enabled && self.gps_enabled && self.gps.has_fix;
        self.connection_type = if self.enabled && (self.connected || self.has_cellular_visibility())
        {
            "4g".to_string()
        } else {
            "none".to_string()
        };
        self.network_status = self.derive_network_status().to_string();
        self.gps_status = self.derive_gps_status().to_string();
    }

    fn has_cellular_visibility(&self) -> bool {
        self.registered
            || self.sim_ready
            || !self.carrier.trim().is_empty()
            || !self.network_type.trim().is_empty()
            || self.signal.bars > 0
            || matches!(
                self.state,
                NetworkLifecycleState::Probing
                    | NetworkLifecycleState::Ready
                    | NetworkLifecycleState::Registering
                    | NetworkLifecycleState::Registered
                    | NetworkLifecycleState::PppStarting
                    | NetworkLifecycleState::Online
                    | NetworkLifecycleState::PppStopping
                    | NetworkLifecycleState::Recovering
                    | NetworkLifecycleState::Degraded
            )
    }

    fn derive_network_status(&self) -> &'static str {
        if !self.enabled {
            return "disabled";
        }
        if self.connected {
            return "online";
        }
        match self.state {
            NetworkLifecycleState::Registered | NetworkLifecycleState::PppStarting | NetworkLifecycleState::PppStopping => {
                "registered"
            }
            NetworkLifecycleState::Probing
            | NetworkLifecycleState::Ready
            | NetworkLifecycleState::Registering
            | NetworkLifecycleState::Recovering => "connecting",
            NetworkLifecycleState::Degraded => "degraded",
            _ => "offline",
        }
    }

    fn derive_gps_status(&self) -> &'static str {
        if !self.enabled || !self.gps_enabled {
            return "disabled";
        }
        if self.gps_has_fix {
            return "fix";
        }
        match self.state {
            NetworkLifecycleState::Off
            | NetworkLifecycleState::Probing
            | NetworkLifecycleState::Ready => "starting",
            NetworkLifecycleState::Registering
            | NetworkLifecycleState::Registered
            | NetworkLifecycleState::PppStarting
            | NetworkLifecycleState::Online
            | NetworkLifecycleState::PppStopping
            | NetworkLifecycleState::Recovering
            | NetworkLifecycleState::Degraded => "searching",
        }
    }
}
