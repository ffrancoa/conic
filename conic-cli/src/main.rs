use std::fs;
use std::io::{BufRead, BufReader, IsTerminal, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStderr, ChildStdin, ChildStdout, Command, Stdio};
use std::time::Duration;

use clap::builder::styling::{AnsiColor, Effects, Styles};
use clap::{Args, Parser, Subcommand};
use indicatif::{ProgressBar, ProgressStyle};

const DEFAULT_CONFIG: &str = include_str!("../../src/conic/config/defaults.toml");

const MAIN_TEMPLATE: &str = "import conic.express as cx\n\n\
     config = cx.build_configurator(\"config.toml\")\n";

const PYPROJECT_TEMPLATE: &str = "\
[project]
name = \"{name}\"
version = \"0.1.0\"
description = \"Add your description here\"
requires-python = \">=3.12\"
dependencies = [\"conic>={version}\"]
";

const HELP_STYLES: Styles = Styles::styled()
    .header(AnsiColor::Green.on_default().effects(Effects::BOLD))
    .usage(AnsiColor::Green.on_default().effects(Effects::BOLD))
    .literal(AnsiColor::Cyan.on_default().effects(Effects::BOLD))
    .placeholder(AnsiColor::Cyan.on_default())
    .valid(AnsiColor::Green.on_default().effects(Effects::BOLD))
    .invalid(AnsiColor::Yellow.on_default().effects(Effects::BOLD))
    .error(AnsiColor::Red.on_default().effects(Effects::BOLD));

#[derive(Parser)]
#[command(
    name    = env!("CARGO_BIN_NAME"),
    version = env!("CARGO_PKG_VERSION"),
    about   = env!("CARGO_PKG_DESCRIPTION"),
    styles  = HELP_STYLES,
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    #[command(about = "Browse and fetch curated CPTu/SCPTu datasets")]
    Datasets(DatasetsArgs),
    #[command(about = "Initialize a conic project or a configuration file")]
    Init(InitArgs),
}

#[derive(Args)]
#[group(required = true, multiple = false)]
struct DatasetsArgs {
    #[arg(short, long, help = "List the curated datasets and their metadata")]
    list: bool,

    #[arg(
        short,
        long,
        value_name = "SOURCE",
        help = "Download a dataset by its source name"
    )]
    fetch: Option<String>,
}

#[derive(Args)]
#[group(multiple = false)]
struct InitArgs {
    #[arg(
        value_name = "NAME",
        help = "Project folder to create; omit to only create config.toml here"
    )]
    name_pos: Option<String>,

    #[arg(
        short,
        long = "name",
        value_name = "NAME",
        help = "Project folder to create"
    )]
    name_flag: Option<String>,
}

fn python_candidates() -> Vec<PathBuf> {
    let mut candidates = Vec::new();

    // installed wheel: the binary sits next to the interpreter.
    if let Ok(exe) = std::env::current_exe().and_then(|p| p.canonicalize())
        && let Some(dir) = exe.parent()
    {
        for name in ["python3", "python", "python3.exe", "python.exe"] {
            let candidate = dir.join(name);
            if candidate.is_file() {
                candidates.push(candidate);
            }
        }
    }

    // active virtualenv (dev: `cargo run` inside a venv).
    if let Ok(venv) = std::env::var("VIRTUAL_ENV") {
        for rel in [
            "bin/python3",
            "bin/python",
            "Scripts/python.exe",
            "Scripts/python3.exe",
        ] {
            let candidate = PathBuf::from(&venv).join(rel);
            if candidate.is_file() {
                candidates.push(candidate);
            }
        }
    }

    candidates.push(PathBuf::from("python3"));
    candidates.push(PathBuf::from("python"));
    candidates
}

struct PyServer {
    child: Child,
    python: PathBuf,
    stdin: Option<ChildStdin>,
    stdout: BufReader<ChildStdout>,
    stderr: Option<ChildStderr>,
}

impl PyServer {
    fn start() -> Result<Self, String> {
        for python in python_candidates() {
            let spawned = Command::new(&python)
                .args(["-m", "conic._server"])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn();

            if let Ok(mut child) = spawned {
                let stdin = child.stdin.take().expect("piped stdin");
                let stdout = BufReader::new(child.stdout.take().expect("piped stdout"));
                let stderr = child.stderr.take().expect("piped stderr");
                return Ok(Self {
                    child,
                    python,
                    stdin: Some(stdin),
                    stdout,
                    stderr: Some(stderr),
                });
            }
        }

        Err(
            "could not find a python interpreter to run the conic backend; \
             activate the environment where conic is installed"
                .into(),
        )
    }

    fn request(
        &mut self,
        request: &serde_json::Value,
    ) -> Result<serde_json::Value, String> {
        let stdin = self
            .stdin
            .as_mut()
            .ok_or("the conic backend is not running")?;
        let line = serde_json::to_string(request).map_err(|e| e.to_string())?;

        stdin
            .write_all(line.as_bytes())
            .and_then(|_| stdin.write_all(b"\n"))
            .and_then(|_| stdin.flush())
            .map_err(|_| "lost contact with the conic backend".to_string())?;

        let mut response = String::new();
        let read = self
            .stdout
            .read_line(&mut response)
            .map_err(|_| "lost contact with the conic backend".to_string())?;

        if read == 0 {
            return Err(self.exit_reason());
        }

        serde_json::from_str(&response)
            .map_err(|_| "the conic backend sent an unreadable response".to_string())
    }

    /// Human-readable reason for an unexpected backend exit.
    fn exit_reason(&mut self) -> String {
        let details = self.drain_stderr();

        if details.contains("No module named 'conic'") {
            format!(
                "the python interpreter '{}' cannot import conic; \
                 install conic in that environment or activate its virtualenv",
                self.python.display()
            )
        } else if details.is_empty() {
            "the conic backend stopped unexpectedly".into()
        } else {
            format!("the conic backend stopped unexpectedly:\n{details}")
        }
    }

    fn drain_stderr(&mut self) -> String {
        let mut buffer = String::new();
        if let Some(mut stderr) = self.stderr.take() {
            let _ = stderr.read_to_string(&mut buffer);
        }
        buffer.trim().to_string()
    }

    fn shutdown(mut self) {
        self.stdin.take();
        let _ = self.child.wait();
    }
}

/// Bold, colored `label:` when the stream is a terminal, plain otherwise.
fn styled_label(
    label: &str,
    is_tty: bool,
    color: clap::builder::styling::AnsiColor,
) -> String {
    if !is_tty {
        return format!("{label}:");
    }

    let style = clap::builder::styling::Style::new()
        .bold()
        .fg_color(Some(color.into()));
    format!("{style}{label}:{style:#}")
}

fn print_info(message: &str) {
    let label = styled_label(
        "info",
        std::io::stdout().is_terminal(),
        clap::builder::styling::AnsiColor::Green,
    );
    println!("{label} {message}");
}

fn print_error(message: &str) {
    let label = styled_label(
        "error",
        std::io::stderr().is_terminal(),
        clap::builder::styling::AnsiColor::Red,
    );
    eprintln!("{label} {message}");
}

fn fetch(source: &str) {
    let mut server = match PyServer::start() {
        Ok(server) => server,
        Err(error) => {
            print_error(&error);
            std::process::exit(1);
        }
    };

    let spinner = ProgressBar::new_spinner();
    spinner.set_style(
        ProgressStyle::with_template("{spinner} {msg}")
            .unwrap_or_else(|_| ProgressStyle::default_spinner()),
    );
    spinner.set_message(format!("Fetching {source}..."));
    spinner.enable_steady_tick(Duration::from_millis(100));

    let request = serde_json::json!({ "cmd": "fetch", "source": source });
    let result = server.request(&request);
    server.shutdown();

    spinner.finish_and_clear();

    match result {
        Ok(response) if response["status"] == "ok" => {
            print_info(&format!("\"{source}\" dataset fetched successfully"));
        }
        Ok(response) => {
            let message = response["message"]
                .as_str()
                .unwrap_or("the conic backend reported an unknown error");
            print_error(message);
            std::process::exit(1);
        }
        Err(error) => {
            print_error(&error);
            std::process::exit(1);
        }
    }
}

/// Scaffold config: `defaults.toml` without the trailing
/// `[columns.correlation.*]` tables (derived output names users rarely rename).
fn scaffold_config() -> String {
    let body = match DEFAULT_CONFIG.find("[columns.correlation") {
        Some(cut) => DEFAULT_CONFIG[..cut].trim_end(),
        None => DEFAULT_CONFIG.trim_end(),
    };
    format!("{body}\n")
}

fn write_file(project: &str, dir: &Path, filename: &str, content: &str) {
    if let Err(error) = fs::write(dir.join(filename), content) {
        print_error(&format!(
            "could not write {filename} in \"{project}\": {error}"
        ));
        std::process::exit(1);
    }
}

fn create_project(name: &str) {
    let dir = PathBuf::from(name);

    if let Err(error) = fs::create_dir(&dir) {
        let reason = if error.kind() == std::io::ErrorKind::AlreadyExists {
            format!("\"{name}\" already exists; choose a different project name")
        } else {
            format!("could not create the project folder \"{name}\": {error}")
        };
        print_error(&reason);
        std::process::exit(1);
    }

    let project_name = dir
        .file_name()
        .map(|component| component.to_string_lossy().into_owned())
        .unwrap_or_else(|| name.to_string());
    let pyproject = PYPROJECT_TEMPLATE
        .replace("{name}", &project_name)
        .replace("{version}", env!("CARGO_PKG_VERSION"));

    write_file(name, &dir, "config.toml", &scaffold_config());
    write_file(name, &dir, "main.py", MAIN_TEMPLATE);
    write_file(name, &dir, "pyproject.toml", &pyproject);

    let location = dir.canonicalize().unwrap_or(dir);
    print_info(&format!(
        "'{project_name}' project created at '{}'",
        location.display()
    ));
}

fn create_config() {
    let path = PathBuf::from("config.toml");

    if path.exists() {
        print_error("\"config.toml\" already exists in the current folder");
        std::process::exit(1);
    }

    if let Err(error) = fs::write(&path, scaffold_config()) {
        print_error(&format!("could not write config.toml: {error}"));
        std::process::exit(1);
    }

    let location = path.canonicalize().unwrap_or(path);
    print_info(&format!(
        "configuration file created at '{}'",
        location.display()
    ));
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Datasets(args) => {
            if args.list {
                conic_datasets::list_datasets(None);
            } else if let Some(source) = args.fetch.as_deref() {
                fetch(source);
            }
        }
        Commands::Init(args) => match args.name_flag.or(args.name_pos) {
            Some(name) => create_project(&name),
            None => create_config(),
        },
    }
}
