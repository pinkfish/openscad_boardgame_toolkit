import * as path from "path";
import * as vscode from "vscode";
import { findExecutable } from "./executableFinder";
import { isPythonScadOrScadDocument } from "./pythonScadFile";

export class PythonScadStatusBar {
  private readonly item: vscode.StatusBarItem;

  constructor() {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    this.item.command = "pythonscad.selectExecutable";
    this.refresh();
  }

  refresh(): void {
    const editor = vscode.window.activeTextEditor;
    if (!editor || !isPythonScadOrScadDocument(editor.document)) {
      this.item.hide();
      return;
    }

    const executable = findExecutable();
    if (executable) {
      this.item.text = `$(tools) PythonSCAD: ${path.basename(executable, path.extname(executable))}`;
      this.item.tooltip = `${executable}\nClick to change the PythonSCAD executable`;
    } else {
      this.item.text = "$(warning) PythonSCAD: not found";
      this.item.tooltip = "Click to select a PythonSCAD executable";
    }
    this.item.show();
  }

  dispose(): void {
    this.item.dispose();
  }
}
