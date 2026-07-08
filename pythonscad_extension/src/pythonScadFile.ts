import * as vscode from "vscode";

const IMPORT_PATTERN = /^\s*(?:from\s+openscad\s+import\b|import\s+openscad\b)/m;
const SCAN_LINES = 60;

/**
 * PythonSCAD's .py mode is a superset of plain Python (via `from openscad import *`),
 * so this extension must not treat every open .py file as a PythonSCAD file - that
 * would put compile diagnostics on unrelated Python code. When the heuristic setting
 * is enabled, only .py files that actually import the `openscad` module qualify.
 */
export function isPythonScadDocument(document: vscode.TextDocument): boolean {
  if (document.languageId !== "python") {
    return false;
  }

  const config = vscode.workspace.getConfiguration("pythonscad", document.uri);
  if (!config.get<boolean>("pythonFileHeuristic", true)) {
    return true;
  }

  const lineCount = Math.min(document.lineCount, SCAN_LINES);
  const text = document.getText(
    new vscode.Range(0, 0, lineCount, 0)
  );
  return IMPORT_PATTERN.test(text);
}

export function isScadDocument(document: vscode.TextDocument): boolean {
  return document.uri.fsPath.toLowerCase().endsWith(".scad");
}

export function isPythonScadOrScadDocument(document: vscode.TextDocument): boolean {
  return isScadDocument(document) || isPythonScadDocument(document);
}
