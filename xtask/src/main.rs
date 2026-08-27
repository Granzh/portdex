use cargo_metadata::MetadataCommand;
use std::process::Command;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let task = std::env::args().nth(1);
    match task.as_deref() {
        Some("dist") => build_distribution()?,
        Some("lint") => run_lints()?,
        Some("check-fitness") => run_fitness_checks()?,
        _ => print_help(),
    }
    Ok(())
}

fn build_distribution() -> Result<(), Box<dyn std::error::Error>> {
    println!("Building release bundle...");
    let status = Command::new("cargo")
        .args(["build", "--release"])
        .status()?;

    if !status.success() {
        return Err("Build failed".into());
    }
    Ok(())
}

fn print_help() {
    eprintln!("Usage: cargo xtask <dist>");
}

fn run_lints() -> Result<(), Box<dyn std::error::Error>> {
    println!("--> Checking formatting...");

    let status_fmt = Command::new("cargo")
        .args(["fmt", "--all", "--", "--check"])
        .status()?;

    if !status_fmt.success() {
        return Err("fmt failed".into());
    }

    println!("--> Running clippy...");

    let status_clippy = Command::new("cargo")
        .args([
            "clippy",
            "--workspace",
            "--all-targets",
            "--all-features",
            "--",
            "-D",
            "warnings",
        ])
        .status()?;

    if !status_clippy.success() {
        return Err("clippy failed".into());
    }

    println!("Pass!");

    Ok(())
}

fn run_fitness_checks() -> Result<(), Box<dyn std::error::Error>> {
    println!("--> Starting Architecture Fitness Funcsions");

    let status_dependency = Command::new("cargo").args(["deny", "check"]).status()?;

    if !status_dependency.success() {
        return Err("Dependencies topoly is invalid".into());
    }

    check_app_core_isolation()?;

    Ok(())
}

fn check_app_core_isolation() -> Result<(), Box<dyn std::error::Error>> {
    println!("Check isolation for app_core...");

    let metadata = MetadataCommand::new().exec()?;

    let app_core_pkg = metadata
        .workspace_packages()
        .into_iter()
        .find(|pkg| pkg.name == "app_core")
        .ok_or("Crate `app_core` not found!")?;

    let other_workspace_crates: Vec<String> = metadata
        .workspace_packages()
        .into_iter()
        .map(|pkg| pkg.name.clone())
        .filter(|name| name != "app_core")
        .collect();

    for dep in &app_core_pkg.dependencies {
        if other_workspace_crates.contains(&dep.name) {
            eprintln!("❌ FITNESS FUNCTION FAILED: `app_core` violates architecture!");
            eprintln!("   Found banned addiction: `{}`", dep.name);
            std::process::exit(1);
        }
    }

    println!("    `app_core` isolated from other application crates!.\n");
    Ok(())
}
