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

    Ok(())
}

fn run_fitness_checks() -> Result<(), Box<dyn std::error::Error>> {
    println!("--> Starting Architecture Fitness Funcsions");

    let status_dependency = Command::new("cargo").args(["deny", "check"]).status()?;

    if !status_dependency.success() {
        return Err("Dependencies topoly is invalid".into());
    }

    Ok(())
}
