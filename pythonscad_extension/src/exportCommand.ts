import { execFile } from "child_process";
import * as path from "path";
import * as vscode from "vscode";
import { findExecutable } from "./executableFinder";
import { isPythonScadDocument, isPythonScadOrScadDocument } from "./pythonScadFile";

const EXPORT_FORMATS = ["stl", "3mf", "off", "amf", "csg", "svg", "dxf", "pdf", "png"];

export async function exportFile(output: vscode.OutputChannel): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || !isPythonScadOrScadDocument(editor.document)) {
    vscode.window.showWarningMessage("Open a .scad or PythonSCAD .py file to export it.");
    return;
  }
  const document = editor.document;

  if (document.isDirty) {
    const saved = await document.save();
    if (!saved) {
      vscode.window.showErrorMessage("Save the file before exporting.");
      return;
    }
  }

  const executable = findExecutable();
  if (!executable) {
    vscode.window.showErrorMessage("PythonSCAD executable not found. Run 'PythonSCAD: Select Executable...' first.");
    return;
  }

  const isPython = isPythonScadDocument(document);
  if (isPython && !vscode.workspace.isTrusted) {
    vscode.window.showErrorMessage("This workspace is not trusted, so PythonSCAD cannot execute this .py file.");
    return;
  }

  const format = await vscode.window.showQuickPick(EXPORT_FORMATS, {
    placeHolder: "Export format",
  });
  if (!format) {
    return;
  }

  const defaultUri = vscode.Uri.file(
    path.join(path.dirname(document.uri.fsPath), `${path.basename(document.uri.fsPath, path.extname(document.uri.fsPath))}.${format}`)
  );
  const target = await vscode.window.showSaveDialog({ defaultUri });
  if (!target) {
    return;
  }

  const config = vscode.workspace.getConfiguration("pythonscad", document.uri);
  const backend = config.get<string>("backend", "Manifold");
  const args = ["-o", target.fsPath, "--backend", backend];
  if (isPython) {
    args.push("--trust-python");
  }
  args.push(document.uri.fsPath);

  output.show(true);
  output.appendLine(`$ ${executable} ${args.join(" ")}`);

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `PythonSCAD: exporting ${format}...` },
    () =>
      new Promise<void>((resolve) => {
        execFile(executable, args, { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
          if (stdout.trim()) {
            output.append(stdout);
          }
          if (stderr.trim()) {
            output.append(stderr);
          }
          if (error) {
            vscode.window.showErrorMessage(`PythonSCAD export failed: see the PythonSCAD output channel.`);
          } else {
            vscode.window.showInformationMessage(`Exported to ${target.fsPath}`);
          }
          resolve();
        });
      })
  );
}
