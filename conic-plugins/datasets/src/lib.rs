use std::collections::BTreeMap;
use std::sync::LazyLock;

use regex::Regex;
use serde::Deserialize;

const REGISTRY_TOML: &str = include_str!("../../../src/conic/datasets/registry.toml");

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

static TITLE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\(\d{4}\)\.\s*(.*?)\.").unwrap());

fn title_from_citation(citation: &str) -> &str {
    TITLE_RE
        .captures(citation)
        .and_then(|c| c.get(1))
        .map(|m| m.as_str())
        .unwrap_or(citation)
}

fn wrap_title(title: &str, suffix: &str) -> String {
    let prefix = "\u{258C} ";
    let first_budget = MAX_WIDTH - prefix.len() - suffix.len();
    let cont_indent = "  ";
    let cont_budget = MAX_WIDTH - cont_indent.len();

    let words: Vec<&str> = title.split_whitespace().collect();
    let mut lines: Vec<String> = Vec::new();
    let mut current = String::new();
    let mut is_first = true;

    for word in &words {
        let budget = if is_first { first_budget } else { cont_budget };
        let needed = if current.is_empty() {
            word.len()
        } else {
            current.len() + 1 + word.len()
        };

        if !current.is_empty() && needed > budget {
            lines.push(current);
            current = String::new();
            is_first = false;
        }

        if current.is_empty() {
            current.push_str(word);
        } else {
            current.push(' ');
            current.push_str(word);
        }
    }

    if !current.is_empty() {
        lines.push(current);
    }

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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn registry_parses() {
        let reg = &*REGISTRY;
        assert_eq!(reg.sources.len(), 4);
    }

    #[test]
    fn source_has_entries() {
        let reg = &*REGISTRY;
        let prem = &reg.sources["premstaller"];
        assert_eq!(prem.entries.len(), 2);
        assert!(prem.entries.contains_key("cptu"));
        assert!(prem.entries.contains_key("scptu"));
    }

    #[test]
    fn title_extraction() {
        let title = title_from_citation(
            "Geyin, M. (2020). CPT-Based Liquefaction Case Histories. DesignSafe-CI.",
        );
        assert_eq!(title, "CPT-Based Liquefaction Case Histories");
    }

    #[test]
    fn unknown_source_handled() {
        list_datasets(Some("nonexistent"));
    }
}
