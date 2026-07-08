import { execFile } from "child_process";
import * as crypto from "crypto";
import * as fs from "fs/promises";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";
import { findExecutable } from "./executableFinder";
import { parseIssues } from "./outputParser";
import { isPythonScadDocument, isPythonScadOrScadDocument } from "./pythonScadFile";

const SEVERITY: Record<string, vscode.DiagnosticSeverity> = {
  error: vscode.DiagnosticSeverity.Error,
  warning: vscode.DiagnosticSeverity.Warning,
  info: vscode.DiagnosticSeverity.Information,
};

const CHECK_TIMEOUT_MS = 30_000;

function shouldTrustPython(): boolean {
  const config = vscode.workspace.getConfiguration("pythonscad");
  const mode = config.get<string>("trustPythonExecution", "workspaceTrust");
  if (mode === "always") {
    return true;
  }
  if (mode === "never") {
    return false;
  }
  return vscode.workspace.isTrusted;
}

/**
 * Writes the live (possibly unsaved) buffer to a hidden sibling file so relative
 * `use <...>` / `include <...>` / Python imports next to the real file keep
 * resolving. Returns the original path unchanged when the document has no
 * unsaved changes, since then the check can just run on disk in place.
 */
async function materialize(document: vscode.TextDocument): Promise<{ filePath: string; cleanup: () => Promise<void> }> {
  if (!document.isDirty) {
    return { filePath: document.uri.fsPath, cleanup: async () => {} };
  }

  const dir = path.dirname(document.uri.fsPath);
  const ext = path.extname(document.uri.fsPath);
  const base = path.basename(document.uri.fsPath, ext);
  const tempPath = path.join(dir, `.${base}.pythonscad-check.${crypto.randomBytes(4).toString("hex")}${ext}`);
  await fs.writeFile(tempPath, document.getText(), "utf8");
  return {
    filePath: tempPath,
    cleanup: async () => {
      await fs.rm(tempPath, { force: true });
    },
  };
}

export class PythonScadChecker {
  constructor(
    private readonly output: vscode.OutputChannel,
    private readonly diagnostics: vscode.DiagnosticCollection
  ) {}

  async check(document: vscode.TextDocument): Promise<void> {
    if (!isPythonScadOrScadDocument(document)) {
      return;
    }

    const executable = findExecutable();
    if (!executable) {
      this.output.appendLine("PythonSCAD executable not found. Run 'PythonSCAD: Select Executable...' to set one.");
      return;
    }

    const isPython = isPythonScadDocument(document);
    if (isPython && !shouldTrustPython()) {
      this.diagnostics.set(document.uri, []);
      this.output.appendLine(
        `Skipped ${document.uri.fsPath}: this workspace is not trusted to execute Python. ` +
          `Use "PythonSCAD: Trust This Workspace to Run Python Files" or adjust pythonscad.trustPythonExecution.`
      );
      return;
    }

    const config = vscode.workspace.getConfiguration("pythonscad", document.uri);
    const format = config.get<string>("checkExportFormat", "ast");
    const backend = config.get<string>("backend", "Manifold");
    const extraArgs = config.get<string[]>("extraArgs", []);

    const { filePath, cleanup } = await materialize(document);
    const outFile = path.join(os.tmpdir(), `pythonscad-check-${crypto.randomBytes(6).toString("hex")}.${format}`);

    const args = ["-o", outFile, "--export-format", format, "--backend", backend];
    if (isPython) {
      args.push("--trust-python");
    }
    args.push(...extraArgs, filePath);

    this.output.appendLine(`$ ${executable} ${args.join(" ")}`);

    try {
      const { stdout, stderr } = await runProcess(executable, args);
      if (stdout.trim().length > 0) {
        this.output.append(stdout);
      }
      if (stderr.trim().length > 0) {
        this.output.append(stderr);
      }

      const issues = parseIssues(stdout, stderr, isPython);
      const diagnostics = issues.map((issue) => {
        const lineIndex = Math.max(0, issue.line - 1);
        const lineLength = lineIndex < document.lineCount ? document.lineAt(lineIndex).text.length : 0;
        const range = new vscode.Range(lineIndex, 0, lineIndex, Math.max(lineLength, 1));
        const diagnostic = new vscode.Diagnostic(range, issue.message, SEVERITY[issue.severity]);
        diagnostic.source = "pythonscad";
        return diagnostic;
      });
      this.diagnostics.set(document.uri, diagnostics);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      this.output.appendLine(`PythonSCAD check failed to run: ${message}`);
      vscode.window.showErrorMessage(`PythonSCAD check failed to run: ${message}`);
    } finally {
      await cleanup();
      await fs.rm(outFile, { force: true });
    }
  }
}

function runProcess(executable: string, args: string[]): Promise<{ stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    execFile(
      executable,
      args,
      { timeout: CHECK_TIMEOUT_MS, maxBuffer: 10 * 1024 * 1024 },
      (error, stdout, stderr) => {
        if (error && (error as NodeJS.ErrnoException).code === "ENOENT") {
          reject(new Error(`Executable not found: ${executable}`));
          return;
        }
        if (error && (error as { killed?: boolean; signal?: string }).signal === "SIGTERM") {
          reject(new Error(`Timed out after ${CHECK_TIMEOUT_MS}ms`));
          return;
        }
        // A non-zero exit code from PythonSCAD is expected when there are
        // compile errors - the real signal is in stdout/stderr, which the
        // caller parses, so it is not treated as a rejection here.
        resolve({ stdout, stderr });
      }
    );
  });
}
