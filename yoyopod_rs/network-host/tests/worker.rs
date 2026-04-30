use yoyopod_network_host::worker::run_with_io;

#[test]
fn worker_emits_ready_and_stopped_for_network_shutdown_command() {
    let input = br#"{"schema_version":1,"kind":"command","type":"network.shutdown","request_id":"shutdown-1","timestamp_ms":0,"deadline_ms":0,"payload":{}}
"#;
    let mut output = Vec::new();

    run_with_io("config", input.as_slice(), &mut output).expect("worker exits cleanly");

    let stdout = String::from_utf8(output).expect("utf8");
    let mut lines = stdout.lines();
    let ready = lines.next().expect("ready line");
    let stopped = lines.next().expect("stopped line");

    assert!(ready.contains("\"schema_version\":1"));
    assert!(ready.contains("\"kind\":\"event\""));
    assert!(ready.contains("\"type\":\"network.ready\""));
    assert!(ready.contains("\"config_dir\":\"config\""));

    assert!(stopped.contains("\"schema_version\":1"));
    assert!(stopped.contains("\"kind\":\"event\""));
    assert!(stopped.contains("\"type\":\"network.stopped\""));
    assert!(stopped.contains("\"reason\":\"shutdown\""));
}
