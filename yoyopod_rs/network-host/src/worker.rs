use std::io::{self, BufRead, Read, Write};

use anyhow::Result;

use crate::protocol::{ready_event, stopped_event, EnvelopeKind, WorkerEnvelope};

pub fn run(config_dir: &str) -> Result<()> {
    let stdin = io::stdin();
    let mut stdout = io::stdout().lock();
    run_with_io(config_dir, stdin.lock(), &mut stdout)
}

pub fn run_with_io<R, W>(config_dir: &str, input: R, output: &mut W) -> Result<()>
where
    R: Read,
    W: Write,
{
    write_envelope(output, &ready_event(config_dir))?;

    let reader = io::BufReader::new(input);
    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }

        let envelope = WorkerEnvelope::decode(line.as_bytes())?;
        if envelope.kind != EnvelopeKind::Command {
            continue;
        }

        if matches!(
            envelope.message_type.as_str(),
            "network.shutdown" | "worker.stop"
        ) {
            write_envelope(output, &stopped_event("shutdown"))?;
            break;
        }
    }

    Ok(())
}

fn write_envelope(output: &mut dyn Write, envelope: &WorkerEnvelope) -> Result<()> {
    writeln!(output, "{}", serde_json::to_string(envelope)?)?;
    output.flush()?;
    Ok(())
}
