import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";

/** Candidate executable paths to probe when no explicit configuration is set. */
function defaultCandidates(): string[] {
  switch (os.platform()) {
    case "darwin":
      return [
        "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
        path.join(os.homedir(), "Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD"),
      ];
    case "win32":
      return [
        "C:\\Program Files\\PythonSCAD\\PythonSCAD.exe",
        "C:\\Program Files (x86)\\PythonSCAD\\PythonSCAD.exe",
      ];
    default:
      return ["/usr/bin/pythonscad", "/usr/local/bin/pythonscad", "/opt/pythonscad/pythonscad"];
  }
}

/** Resolves an app bundle path (macOS .app) to its actual executable binary. */
function resolveAppBundle(candidate: string): string {
  if (os.platform() === "darwin" && candidate.endsWith(".app")) {
    const name = path.basename(candidate, ".app");
    return path.join(candidate, "Contents", "MacOS", name);
  }
  return candidate;
}

function isExecutableFile(p: string): boolean {
  try {
    const stat = fs.statSync(p);
    if (!stat.isFile()) {
      return false;
    }
    fs.accessSync(p, fs.constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function which(binaryName: string): string | undefined {
  const pathEnv = process.env.PATH ?? "";
  const exts = os.platform() === "win32" ? [".exe", ".cmd", ".bat", ""] : [""];
  for (const dir of pathEnv.split(path.delimiter)) {
    for (const ext of exts) {
      const candidate = path.join(dir, binaryName + ext);
      if (isExecutableFile(candidate)) {
        return candidate;
      }
    }
  }
  return undefined;
}

/**
 * Finds the PythonSCAD executable to use, honoring the `pythonscad.executablePath`
 * setting first, then falling back to well-known install locations and PATH.
 * Returns undefined if nothing usable was found.
 */
export function findExecutable(): string | undefined {
  const config = vscode.workspace.getConfiguration("pythonscad");
  const configured = config.get<string>("executablePath", "").trim();
  if (configured.length > 0) {
    const resolved = resolveAppBundle(configured);
    return isExecutableFile(resolved) ? resolved : undefined;
  }

  for (const candidate of defaultCandidates()) {
    const resolved = resolveAppBundle(candidate);
    if (isExecutableFile(resolved)) {
      return resolved;
    }
  }

  return which("pythonscad") ?? which("openscad");
}

/**
 * Prompts the user to pick a PythonSCAD executable (file picker, defaulting to
 * app bundles on macOS) and stores it in the workspace configuration.
 */
export async function promptForExecutable(): Promise<string | undefined> {
  const filters: Record<string, string[]> =
    os.platform() === "darwin" ? { Application: ["app"] } : { Executable: ["exe", ""] };

  const picked = await vscode.window.showOpenDialog({
    canSelectFiles: true,
    canSelectFolders: os.platform() === "darwin",
    canSelectMany: false,
    openLabel: "Select PythonSCAD executable",
    filters,
  });
  if (!picked || picked.length === 0) {
    return undefined;
  }

  const resolved = resolveAppBundle(picked[0].fsPath);
  if (!isExecutableFile(resolved)) {
    vscode.window.showErrorMessage(`"${resolved}" is not an executable file.`);
    return undefined;
  }

  const config = vscode.workspace.getConfiguration("pythonscad");
  await config.update("executablePath", resolved, vscode.ConfigurationTarget.Global);
  return resolved;
}
