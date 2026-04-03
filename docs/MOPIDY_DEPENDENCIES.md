# Mopidy Dependencies - YoyoPod Reference

**Last Updated:** 2025-11-30
**Hardware:** Raspberry Pi Zero 2W
**Audio Output:** Whisplay HAT (wm8960 codec, hw:1)

---

## Overview

This document lists all Mopidy-related dependencies and their working versions for the YoyoPod project. These versions have been tested and confirmed working together for Spotify playback on the Whisplay HAT speaker.

---

## Python Packages (pip)

All packages installed via pip with `--break-system-packages` flag in user space.

### Core Mopidy

| Package | Version | Source | Install Command |
|---------|---------|--------|-----------------|
| **mopidy** | 4.0.0a7 | [GitHub](https://github.com/mopidy/mopidy/releases/tag/v4.0.0a7) | `pip install --upgrade --break-system-packages 'mopidy==4.0.0a7'` |
| **mopidy-spotify** | 5.0.0a5 | [GitHub](https://github.com/mopidy/mopidy-spotify/releases/tag/v5.0.0a5) | `pip install --upgrade --break-system-packages 'mopidy-spotify==5.0.0a5'` |
| **mopidy-mpd** | 4.0.0a2 | [GitHub](https://github.com/mopidy/mopidy-mpd/releases/tag/v4.0.0a2) | `pip install --upgrade --break-system-packages 'mopidy-mpd==4.0.0a2'` |

### Python Dependencies

Automatically installed by mopidy packages:

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | 2.12.0 | Data validation |
| pygobject | 3.54.3 | GObject introspection bindings |
| pykka | 4.4.0 | Actor framework |
| requests | 2.32.5 | HTTP library |
| tornado | 6.5.2 | Async networking |

---

## System Packages (apt/deb)

### GStreamer Spotify Plugin

| Package | Version | Source | Install Command |
|---------|---------|--------|-----------------|
| **gst-plugin-spotify** | 0.15.0~alpha.1-4 | [GitHub](https://github.com/kingosticks/gst-plugins-rs-build/releases/tag/gst-plugin-spotify_0.15.0-alpha.1-4) | `wget <deb-url> && sudo dpkg -i gst-plugin-spotify_*.deb` |

**Download URL:**
```
https://github.com/kingosticks/gst-plugins-rs-build/releases/download/gst-plugin-spotify_0.15.0-alpha.1-4/gst-plugin-spotify_0.15.0.alpha.1-4_arm64.deb
```

### MPD Client

| Package | Version | Purpose | Notes |
|---------|---------|---------|-------|
| **mpc** | 0.35-1+b2 | Command-line MPD client | Shows harmless "MPD 0.21 required" warning |

---

## Configuration

### Audio Output

**mopidy.conf:**
```ini
[audio]
output = alsasink device=hw:1
```

- **hw:1** = Whisplay HAT (wm8960 soundcard)
- Uses ALSA direct hardware access
- No need for `plughw` as hw:1 handles format conversion

### Spotify Configuration

**mopidy.conf:**
```ini
[spotify]
enabled = true
client_id = <your_client_id>
client_secret = <your_client_secret>
bitrate = 320
allow_cache = true
cache_size = 8192
```

**Authentication:**
- Get credentials from: https://www.mopidy.com/authenticate
- Client ID and secret are sufficient (no username/password needed)
- Credentials cached in: `~/.local/share/mopidy/spotify/credentials-cache/`

### MPD Server

**mopidy.conf:**
```ini
[mpd]
enabled = true
hostname = 0.0.0.0
port = 6600
```

---

## Installation Steps

### Fresh Install

```bash
# 1. Install core mopidy
pip install --upgrade --break-system-packages 'mopidy==4.0.0a7'

# 2. Install mopidy-spotify
pip install --upgrade --break-system-packages 'mopidy-spotify==5.0.0a5'

# 3. Install mopidy-mpd
pip install --upgrade --break-system-packages 'mopidy-mpd==4.0.0a2'

# 4. Download and install GStreamer Spotify plugin
cd /tmp
wget https://github.com/kingosticks/gst-plugins-rs-build/releases/download/gst-plugin-spotify_0.15.0-alpha.1-4/gst-plugin-spotify_0.15.0.alpha.1-4_arm64.deb
sudo dpkg -i gst-plugin-spotify_0.15.0.alpha.1-4_arm64.deb

# 5. Clear GStreamer cache
rm -rf ~/.cache/gstreamer-1.0/

# 6. Configure mopidy (see Configuration section above)
nano ~/.config/mopidy/mopidy.conf

# 7. Start mopidy
systemctl --user start mopidy
```

### Verify Installation

```bash
# Check versions
pip show mopidy mopidy-spotify mopidy-mpd
dpkg -l | grep gst-plugin-spotify

# Test playback
mpc clear
mpc add 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'
mpc play

# Check status
mpc status
```

---

## Troubleshooting

### Issue: "GStreamer error: Resource not found"

**Cause:** Incompatible versions of mopidy/mopidy-spotify/gst-plugin-spotify

**Solution:** Update all three components to the versions listed above

### Issue: "track is not available" from spotifyaudiosrc

**Cause:** Old version of gst-plugin-spotify (0.15.0-alpha.1-3 or earlier)

**Solution:** Update to gst-plugin-spotify 0.15.0-alpha.1-4

### Issue: "OAuth token refresh failed: invalid_client"

**Cause:** Invalid or expired Spotify credentials

**Solution:**
1. Go to https://www.mopidy.com/authenticate
2. Authenticate with your Spotify Premium account
3. Copy new client_id and client_secret
4. Update mopidy.conf
5. Clear credential cache: `rm -rf ~/.local/share/mopidy/spotify/`
6. Restart mopidy

### Issue: "warning: MPD 0.21 required"

**Cause:** mpc client expects newer MPD protocol version

**Impact:** Harmless cosmetic warning, does not affect functionality

**Solution:** Ignore it - everything works correctly despite the warning

---

## Update History

| Date | Component | Old Version | New Version | Reason |
|------|-----------|-------------|-------------|--------|
| 2025-11-30 | mopidy | 4.0.0a4 | 4.0.0a7 | Fix playback issues |
| 2025-11-30 | mopidy-spotify | 5.0.0a5.dev4 | 5.0.0a5 | Fix track availability errors |
| 2025-11-30 | gst-plugin-spotify | 0.15.0~alpha.1-3 | 0.15.0~alpha.1-4 | Fix "track is not available" error |
| 2025-11-30 | mopidy-mpd | (old) | 4.0.0a2 | Update to latest alpha release |

---

## Known Issues

1. **MPC Warning:** The `mpc` tool shows "warning: MPD 0.21 required" because mopidy-mpd reports MPD protocol version 0.19.0. This is harmless and can be ignored.

2. **Alpha Versions:** All mopidy components are alpha releases. These specific versions have been tested and work together, but newer versions may introduce breaking changes.

3. **Audio Format:** Whisplay HAT requires specific audio formats. Use `hw:1` (not `hw:1,0`) for best compatibility.

---

## Testing Checklist

After installation or updates, verify:

- [ ] Mopidy service starts without errors: `systemctl --user status mopidy`
- [ ] Spotify authentication successful: Check logs for "Logged into Spotify Web API"
- [ ] Playlists load: Verify count in logs (e.g., "Refreshing 41 Spotify playlists")
- [ ] Audio device configured: `alsasink device=hw:1` in config
- [ ] Playback works: `mpc play` successfully plays audio
- [ ] No GStreamer errors: Check logs for "Resource not found" errors

---

## Useful Commands

```bash
# View mopidy logs
journalctl --user -u mopidy -f

# Run mopidy in foreground (for debugging)
mopidy --config ~/.config/mopidy/mopidy.conf

# Test with GStreamer debug output
GST_DEBUG=3 mopidy --config ~/.config/mopidy/mopidy.conf

# Test audio output directly
speaker-test -D hw:1 -c 2 -t wav -l 1

# Test GStreamer audio
gst-launch-1.0 audiotestsrc ! alsasink device=hw:1

# Check mopidy version
mopidy --version

# List available audio devices
aplay -l
```

---

## References

- **Mopidy Documentation:** https://docs.mopidy.com/
- **Mopidy Spotify:** https://github.com/mopidy/mopidy-spotify
- **GStreamer Spotify Plugin:** https://github.com/kingosticks/gst-plugins-rs-build
- **Spotify API Console:** https://www.mopidy.com/authenticate
- **YoyoPod Project:** https://github.com/your-repo/yoyo-py

---

## Notes

- All versions listed are confirmed working as of 2025-11-30
- Tested on Raspberry Pi Zero 2W running Debian Trixie
- Requires Spotify Premium account for playback
- Installation uses `--break-system-packages` due to Python 3.13 externally-managed-environment
