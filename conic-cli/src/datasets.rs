use std::collections::BTreeMap;
use std::sync::LazyLock;

use regex::Regex;
use serde::Deserialize;

const REGISTRY_TOML: &str = include_str!("../../src/conic/datasets/registry.toml");

const MAX_WIDTH: usize = 72;
#[derive(Deserialize)]
struct Registry {
    sources: BTreeMap<String, Source>,
}

#[derive(Deserialize)]
struct Source {
    citation: String,
    doi: String,
    license: String,
    #[allow(dead_code)]
    record: String,
    reference: String,
    entries: BTreeMap<String, Entry>,
}

#[derive(Deserialize)]
struct Entry {
    #[allow(dead_code)]
    filename: String,
    #[allow(dead_code)]
    sha256: String,
    n_soundings: u32,
}

fn test_type_label(key: &str) -> &'static str {
    match key {
        "cptu" => "CPTu",
        "scptu" => "SCPTu",
        _ => "Unknown",
    }
}

static REGISTRY: LazyLock<Registry> =
    LazyLock::new(|| toml::from_str(REGISTRY_TOML).expect("invalid registry.toml"));

static TITLE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\(\d{4}\)\.\s*(.*?)\.").unwrap());

fn title_from_citation(citation: &str) -> &str {
    TITLE_RE
        .captures(citation)
        .and_then(|c| c.get(1))
        .map(|m| m.as_str())
        .unwrap_or(citation)
}

fn wrap_title(title: &str, suffix: &str) -> String {
    let prefix = "\u{258C} ";
    let cont_indent = "  ";
    let prefix_width = prefix.chars().count();
    let cont_width = cont_indent.chars().count();
    let suffix_width = suffix.chars().count();

    let words: Vec<&str> = title.split_whitespace().collect();

    if words.is_empty() {
        return format!("{prefix}{}", suffix.trim_start());
    }

    let mut lines: Vec<String> = Vec::new();
    let mut current = String::new();

    for (index, word) in words.iter().enumerate() {
        let indent = if lines.is_empty() {
            prefix_width
        } else {
            cont_width
        };
        let budget = MAX_WIDTH - indent;

        let reserved = if index + 1 == words.len() {
            suffix_width
        } else {
            0
        };

        let needed = if current.is_empty() {
            word.chars().count() + reserved
        } else {
            current.chars().count() + 1 + word.chars().count() + reserved
        };

        if !current.is_empty() && needed > budget {
            lines.push(current);
            current = String::new();
        }

        if current.is_empty() {
            current.push_str(word);
        } else {
            current.push(' ');
            current.push_str(word);
        }
    }

    lines.push(current);

    let last = lines.len() - 1;
    lines[last].push_str(suffix);

    let mut out = format!("{prefix}{}", lines[0]);
    for line in &lines[1..] {
        out.push('\n');
        out.push_str(cont_indent);
        out.push_str(line);
    }
    out
}

pub fn list_datasets(name: Option<&str>) {
    let registry = &*REGISTRY;

    let sources: Vec<&str> = match name {
        Some(n) => vec![n],
        None => registry.sources.keys().map(String::as_str).collect(),
    };

    for source_name in sources {
        let Some(source) = registry.sources.get(source_name) else {
            let available = registry
                .sources
                .keys()
                .map(String::as_str)
                .collect::<Vec<_>>()
                .join(", ");
            eprintln!("unknown dataset source {source_name:?}; available: {available}");
            continue;
        };

        let title = title_from_citation(&source.citation);
        let suffix = format!(" [{source_name:?}]");
        let variants: Vec<String> = source
            .entries
            .iter()
            .map(|(key, e)| format!("{} ({})", test_type_label(key), e.n_soundings))
            .collect();

        println!("\n{}", wrap_title(title, &suffix));
        println!("    Reference : {}", source.reference);
        println!("    Soundings : {}", variants.join(" \u{00B7} "));
        println!("    DOI       : {}", source.doi);
        println!("    License   : {}", source.license);
    }
}
