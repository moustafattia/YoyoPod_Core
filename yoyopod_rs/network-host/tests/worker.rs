use std::fs;
use std::sync::{Mutex, OnceLock};

use yoyopod_network_host::worker::run_with_io;

fn env_lock() -> &'static Mutex<()> {
    static LOCK: OnceLock<Mutex<()>> = OnceLock::new();
    LOCK.get_or_init(|| Mutex::new(()))
}

#[test]
fn worker_emits_ready_snapshot_and_stopped_for_network_shutdown_command() {
    let _guard = env_lock().lock().expect("env lock");
    let temp = tempfile::tempdir().expect("tempdir");
    let config_dir = temp.path().join("config");
    let network_dir = config_dir.join("network");
    fs::create_dir_all(&network_dir).expect("network dir");
    fs::write(
        network_dir.join("cellular.yaml"),
        concat!(
            "network:\n",
            "  enabled: true\n",
            "  serial_port: /dev/ttyUSB2\n",
            "  ppp_port: /dev/ttyUSB3\n",
            "  baud_rate: 115200\n",
            "  apn: internet\n",
            "  gps_enabled: true\n",
            "  ppp_timeout: 30\n"
        ),
    )
    .expect("write config");
    let input = br#"{"schema_version":1,"kind":"command","type":"network.shutdown","request_id":"shutdown-1","timestamp_ms":0,"deadline_ms":0,"payload":{}}
"#;
    let mut output = Vec::new();

    run_with_io(
        config_dir.to_str().expect("config dir"),
        input.as_slice(),
        &mut output,
    )
    .expect("worker exits cleanly");

    let stdout = String::from_utf8(output).expect("utf8");
    let mut lines = stdout.lines();
    let ready = lines.next().expect("ready line");
    let snapshot = lines.next().expect("snapshot line");
    let stopped = lines.next().expect("stopped line");

    assert!(ready.contains("\"schema_version\":1"));
    assert!(ready.contains("\"kind\":\"event\""));
    assert!(ready.contains("\"type\":\"network.ready\""));
    assert!(ready.contains(&format!(
        "\"config_dir\":\"{}\"",
        config_dir
            .to_str()
            .expect("config dir")
            .replace('\\', "\\\\")
    )));

    assert!(snapshot.contains("\"schema_version\":1"));
    assert!(snapshot.contains("\"kind\":\"event\""));
    assert!(snapshot.contains("\"type\":\"network.snapshot\""));
    assert!(snapshot.contains(&format!(
        "\"config_dir\":\"{}\"",
        config_dir
            .to_str()
            .expect("config dir")
            .replace('\\', "\\\\")
    )));
    assert!(snapshot.contains("\"enabled\":true"));
    assert!(snapshot.contains("\"gps_enabled\":true"));
    assert!(snapshot.contains("\"state\":\"off\""));

    assert!(stopped.contains("\"schema_version\":1"));
    assert!(stopped.contains("\"kind\":\"event\""));
    assert!(stopped.contains("\"type\":\"network.stopped\""));
    assert!(stopped.contains("\"reason\":\"shutdown\""));
}

#[test]
fn worker_degrades_snapshot_instead_of_aborting_on_bad_config() {
    let _guard = env_lock().lock().expect("env lock");
    let temp = tempfile::tempdir().expect("tempdir");
    let config_dir = temp.path().join("config");
    let network_dir = config_dir.join("network");
    fs::create_dir_all(&network_dir).expect("network dir");
    fs::write(network_dir.join("cellular.yaml"), "network: [broken\n").expect("write config");
    let input = br#"{"schema_version":1,"kind":"command","type":"network.shutdown","request_id":"shutdown-1","timestamp_ms":0,"deadline_ms":0,"payload":{}}
"#;
    let mut output = Vec::new();

    run_with_io(
        config_dir.to_str().expect("config dir"),
        input.as_slice(),
        &mut output,
    )
    .expect("worker should degrade instead of aborting");

    let stdout = String::from_utf8(output).expect("utf8");
    let mut lines = stdout.lines();
    let ready = lines.next().expect("ready line");
    let snapshot = lines.next().expect("snapshot line");
    let stopped = lines.next().expect("stopped line");

    assert!(ready.contains("\"type\":\"network.ready\""));
    assert!(snapshot.contains("\"type\":\"network.snapshot\""));
    assert!(snapshot.contains("\"state\":\"degraded\""));
    assert!(snapshot.contains("\"error_code\":\"config_load_failed\""));
    assert!(snapshot.contains("\"error_message\":\""));
    assert!(stopped.contains("\"type\":\"network.stopped\""));
}

#[test]
fn worker_degrades_snapshot_instead_of_aborting_on_bad_env_override() {
    let _guard = env_lock().lock().expect("env lock");
    let temp = tempfile::tempdir().expect("tempdir");
    let config_dir = temp.path().join("config");
    let network_dir = config_dir.join("network");
    fs::create_dir_all(&network_dir).expect("network dir");
    fs::write(
        network_dir.join("cellular.yaml"),
        concat!(
            "network:\n",
            "  enabled: true\n",
            "  serial_port: /dev/ttyUSB2\n",
            "  ppp_port: /dev/ttyUSB3\n",
            "  baud_rate: 115200\n",
            "  apn: internet\n",
            "  gps_enabled: true\n",
            "  ppp_timeout: 30\n"
        ),
    )
    .expect("write config");
    let input = br#"{"schema_version":1,"kind":"command","type":"network.shutdown","request_id":"shutdown-1","timestamp_ms":0,"deadline_ms":0,"payload":{}}
"#;
    let mut output = Vec::new();

    std::env::set_var("YOYOPOD_MODEM_PPP_TIMEOUT", "not-a-number");
    let result = run_with_io(
        config_dir.to_str().expect("config dir"),
        input.as_slice(),
        &mut output,
    );
    std::env::remove_var("YOYOPOD_MODEM_PPP_TIMEOUT");

    result.expect("worker should degrade instead of aborting");

    let stdout = String::from_utf8(output).expect("utf8");
    let mut lines = stdout.lines();
    let _ready = lines.next().expect("ready line");
    let snapshot = lines.next().expect("snapshot line");

    assert!(snapshot.contains("\"type\":\"network.snapshot\""));
    assert!(snapshot.contains("\"state\":\"degraded\""));
    assert!(snapshot.contains("\"error_code\":\"config_load_failed\""));
}
