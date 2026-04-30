use anyhow::Result;
use clap::Parser;

#[derive(Debug, Parser)]
#[command(name = "yoyopod-runtime")]
#[command(about = "YoYoPod Rust top-level runtime host")]
struct Args {
    #[arg(long, default_value = "config")]
    config_dir: String,
}

fn main() -> Result<()> {
    let _args = Args::parse();
    Ok(())
}
