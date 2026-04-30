use serde_json::json;
use yoyopod_runtime::state::{CallState, RuntimeState, WorkerDomain, WorkerState};

#[test]
fn media_snapshot_updates_ui_payload() {
    let mut state = RuntimeState::default();

    state.apply_media_snapshot(&json!({
        "connected": true,
        "playback_state": "playing",
        "current_track": {
            "uri": "file:///music/song.mp3",
            "name": "Little Song",
            "artists": ["YoYo"]
        },
        "playlists": [{"uri":"playlist://sleep","name":"Sleep","track_count": 3}],
        "recent_tracks": [{"uri":"file:///music/song.mp3","title":"Little Song","artist":"YoYo"}]
    }));

    let payload = state.ui_snapshot_payload();

    assert_eq!(payload["music"]["playing"], true);
    assert_eq!(payload["music"]["title"], "Little Song");
    assert_eq!(payload["music"]["artist"], "YoYo");
    assert_eq!(payload["music"]["playlists"][0]["title"], "Sleep");
}

#[test]
fn voip_snapshot_updates_call_and_status_payloads() {
    let mut state = RuntimeState::default();

    state.apply_voip_snapshot(&json!({
        "registered": true,
        "registration_state": "ok",
        "call_state": "incoming",
        "active_call_peer": "sip:mama@example.test",
        "muted": true
    }));

    assert_eq!(state.call.state, CallState::Incoming);
    assert_eq!(state.call.peer_address, "sip:mama@example.test");

    let ui = state.ui_snapshot_payload();
    assert_eq!(ui["call"]["state"], "incoming");
    assert_eq!(ui["call"]["muted"], true);

    let status = state.status_payload();
    assert_eq!(status["voip"]["registered"], true);
}

#[test]
fn voip_snapshot_normalizes_current_worker_call_states() {
    let mut state = RuntimeState::default();

    state.apply_voip_snapshot(&json!({"call_state": "streams_running"}));
    assert_eq!(state.call.state, CallState::Active);
    assert_eq!(state.ui_snapshot_payload()["call"]["state"], "active");

    state.apply_voip_snapshot(&json!({"call_state": "outgoing_init"}));
    assert_eq!(state.call.state, CallState::Outgoing);
    assert_eq!(state.ui_snapshot_payload()["call"]["state"], "outgoing");

    state.apply_voip_snapshot(&json!({"call_state": "outgoing_custom"}));
    assert_eq!(state.call.state, CallState::Outgoing);
    assert_eq!(state.ui_snapshot_payload()["call"]["state"], "outgoing");

    state.apply_voip_snapshot(&json!({"call_state": "released"}));
    assert_eq!(state.call.state, CallState::Idle);
    assert_eq!(state.ui_snapshot_payload()["call"]["state"], "idle");
}

#[test]
fn worker_state_is_visible_in_status() {
    let mut state = RuntimeState::default();

    state.mark_worker(WorkerDomain::Media, WorkerState::Degraded, "process_exited");

    let status = state.status_payload();
    assert_eq!(status["workers"]["media"]["state"], "degraded");
    assert_eq!(status["workers"]["media"]["last_reason"], "process_exited");
}
