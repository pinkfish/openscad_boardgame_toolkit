import * as vscode from "vscode";
import { PythonScadChecker } from "./checker";
import { promptForExecutable } from "./executableFinder";
import { exportFile } from "./exportCommand";
import { isPythonScadOrScadDocument } from "./pythonScadFile";
import { PythonScadStatusBar } from "./statusBar";

export function activate(context: vscode.ExtensionContext): void {
  const output = vscode.window.createOutputChannel("PythonSCAD");
  const diagnostics = vscode.languages.createDiagnosticCollection("pythonscad");
  const checker = new PythonScadChecker(output, diagnostics);
  const statusBar = new PythonScadStatusBar();

  context.subscriptions.push(output, diagnostics, statusBar);

  let debounceTimer: NodeJS.Timeout | undefined;
  const scheduleTypeCheck = (document: vscode.TextDocument) => {
    const config = vscode.workspace.getConfiguration("pythonscad", document.uri);
    if (!config.get<boolean>("checkOnType", false)) {
      return;
    }
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
    const delay = config.get<number>("checkOnTypeDelay", 1000);
    debounceTimer = setTimeout(() => void checker.check(document), Math.max(delay, 100));
  };

  context.subscriptions.push(
    vscode.commands.registerCommand("pythonscad.checkFile", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !isPythonScadOrScadDocument(editor.document)) {
        vscode.window.showWarningMessage("Open a .scad or PythonSCAD .py file to check it.");
        return;
      }
      await checker.check(editor.document);
      const fileDiagnostics = diagnostics.get(editor.document.uri) ?? [];
      const errors = fileDiagnostics.filter((d) => d.severity === vscode.DiagnosticSeverity.Error).length;
      const warnings = fileDiagnostics.filter((d) => d.severity === vscode.DiagnosticSeverity.Warning).length;
      if (errors === 0 && warnings === 0) {
        vscode.window.setStatusBarMessage("$(check) PythonSCAD: no problems found", 4000);
      } else {
        vscode.window.setStatusBarMessage(
          `$(error) PythonSCAD: ${errors} error(s), ${warnings} warning(s)`,
          6000
        );
      }
    }),

    vscode.commands.registerCommand("pythonscad.exportFile", () => exportFile(output)),

    vscode.commands.registerCommand("pythonscad.selectExecutable", async () => {
      const picked = await promptForExecutable();
      if (picked) {
        vscode.window.showInformationMessage(`PythonSCAD executable set to ${picked}`);
        statusBar.refresh();
      }
    }),

    vscode.commands.registerCommand("pythonscad.showOutput", () => output.show(true)),

    vscode.commands.registerCommand("pythonscad.trustWorkspaceForPython", async () => {
      const config = vscode.workspace.getConfiguration("pythonscad");
      await config.update("trustPythonExecution", "always", vscode.ConfigurationTarget.Workspace);
      vscode.window.showInformationMessage(
        "PythonSCAD will now execute .py files in this workspace (pythonscad.trustPythonExecution = always)."
      );
      const editor = vscode.window.activeTextEditor;
      if (editor && isPythonScadOrScadDocument(editor.document)) {
        void checker.check(editor.document);
      }
    }),

    vscode.workspace.onDidSaveTextDocument((document) => {
      const config = vscode.workspace.getConfiguration("pythonscad", document.uri);
      if (config.get<boolean>("checkOnSave", true) && isPythonScadOrScadDocument(document)) {
        void checker.check(document);
      }
    }),

    vscode.workspace.onDidChangeTextDocument((event) => {
      if (isPythonScadOrScadDocument(event.document)) {
        scheduleTypeCheck(event.document);
      }
    }),

    vscode.workspace.onDidCloseTextDocument((document) => {
      diagnostics.delete(document.uri);
    }),

    vscode.window.onDidChangeActiveTextEditor(() => statusBar.refresh()),

    vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration("pythonscad.executablePath")) {
        statusBar.refresh();
      }
    })
  );

  // Check the already-active editor on startup so diagnostics appear immediately.
  const active = vscode.window.activeTextEditor;
  if (active && isPythonScadOrScadDocument(active.document)) {
    void checker.check(active.document);
  }
}

export function deactivate(): void {}
