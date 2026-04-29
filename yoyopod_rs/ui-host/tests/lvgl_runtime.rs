use yoyopod_ui_host::lvgl::open_default_facade;

#[cfg(not(feature = "native-lvgl"))]
#[test]
fn open_default_facade_without_native_feature_returns_contextual_error() {
    let error = match open_default_facade(None) {
        Ok(_) => panic!("native-lvgl should be required"),
        Err(error) => error,
    };

    assert!(error.to_string().contains("native-lvgl feature"));
}

#[cfg(feature = "native-lvgl")]
use std::path::Path;

#[cfg(feature = "native-lvgl")]
#[test]
fn open_default_facade_with_missing_source_returns_contextual_error() {
    let error = match open_default_facade(Some(Path::new("missing-lvgl-source"))) {
        Ok(_) => panic!("missing LVGL source must fail"),
        Err(error) => error,
    };

    assert!(error.to_string().contains("LVGL source"));
}

#[cfg(feature = "native-lvgl")]
#[test]
fn open_default_facade_with_configured_source_opens_backend() {
    if std::env::var_os("YOYOPOD_LVGL_SOURCE_DIR").is_none()
        && std::env::var_os("LVGL_SOURCE_DIR").is_none()
    {
        return;
    }

    open_default_facade(None).expect("configured native backend should open");
}
