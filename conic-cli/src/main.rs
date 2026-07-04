use clap::{Args, Parser, Subcommand};

#[derive(Parser)]
#[command(
    name    = env!("CARGO_BIN_NAME"),
    version = env!("CARGO_PKG_VERSION"),
    about   = env!("CARGO_PKG_DESCRIPTION"),
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    #[command(about = "Browse and fetch curated CPTu/SCPTu datasets")]
    Datasets(DatasetsArgs),
}

#[derive(Args)]
struct DatasetsArgs {
    #[arg(short, long)]
    list: bool,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Datasets(args) => {
            if args.list {
                conic_datasets::list_datasets(None);
            }
        }
    }
}
