use clap::Parser;

#[derive(Parser)]
#[command(
    name = env!("CARGO_BIN_NAME"),
    version = env!("CARGO_PKG_VERSION"),
    about = env!("CARGO_PKG_DESCRIPTION")
)]
struct Cli {}

fn main() {
    Cli::parse();
}
