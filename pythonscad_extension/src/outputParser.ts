export interface ParsedIssue {
  /** 1-based line number in the checked document. */
  line: number;
  message: string;
  severity: "error" | "warning" | "info";
}

const SCAD_MESSAGE = /^(ERROR|WARNING|TRACE|DEPRECATED):\s*(.*?)(?:\s+in file\s+"?[^,"]*"?,\s*line\s+(\d+))?\s*$/;

const SEVERITY_MAP: Record<string, ParsedIssue["severity"]> = {
  ERROR: "error",
  WARNING: "warning",
  TRACE: "info",
  DEPRECATED: "warning",
};

/**
 * Parses OpenSCAD/PythonSCAD's own diagnostic lines, e.g.:
 *   ERROR: Parser error: syntax error in file bad.scad, line 3
 *   WARNING: variable "x" not specified as parameter in file bad2.scad, line 4
 * These are emitted for both .scad files and for PythonSCAD-level issues in .py files.
 */
export function parseScadMessages(output: string): ParsedIssue[] {
  const issues: ParsedIssue[] = [];
  for (const rawLine of output.split(/\r?\n/)) {
    const match = SCAD_MESSAGE.exec(rawLine.trim());
    if (!match) {
      continue;
    }
    const [, kind, message, lineStr] = match;
    issues.push({
      line: lineStr ? parseInt(lineStr, 10) : 1,
      message: message.trim(),
      severity: SEVERITY_MAP[kind] ?? "error",
    });
  }
  return issues;
}

const STRING_FRAME = /^\s*File "([^"]*)", line (\d+)(?:, in .*)?$/;
const IGNORED_UNINDENTED_LINES = new Set([
  "traceback (most recent call last):",
  "python code globally trusted",
  "no top-level csg object",
]);

/**
 * Parses a raw Python traceback produced by executing a PythonSCAD .py file with
 * --trust-python. PythonSCAD evaluates the file's text as an in-memory string, so
 * every frame in the user's own code is reported as `File "<string>", line N`
 * rather than the real file path - the line number is still accurate for the
 * checked document.
 */
export function parsePythonTraceback(stderr: string): ParsedIssue[] {
  const lines = stderr.split(/\r?\n/);

  let lastStringFrameLine: number | undefined;
  let lastFrameLine: number | undefined;
  for (const line of lines) {
    const match = STRING_FRAME.exec(line);
    if (!match) {
      continue;
    }
    const [, file, lineNoStr] = match;
    const lineNo = parseInt(lineNoStr, 10);
    lastFrameLine = lineNo;
    if (file === "<string>") {
      lastStringFrameLine = lineNo;
    }
  }

  let message: string | undefined;
  for (const line of lines) {
    if (line.length === 0 || /^\s/.test(line)) {
      continue;
    }
    if (SCAD_MESSAGE.test(line.trim())) {
      continue;
    }
    if (IGNORED_UNINDENTED_LINES.has(line.trim().toLowerCase())) {
      continue;
    }
    message = line.trim();
  }

  if (!message) {
    return [];
  }

  return [
    {
      line: lastStringFrameLine ?? lastFrameLine ?? 1,
      message,
      severity: "error",
    },
  ];
}

export function parseIssues(stdout: string, stderr: string, isPython: boolean): ParsedIssue[] {
  const combined = `${stdout}\n${stderr}`;
  const scadIssues = parseScadMessages(combined);
  if (!isPython) {
    return scadIssues;
  }
  const pythonIssues = parsePythonTraceback(stderr);
  return [...scadIssues, ...pythonIssues];
}
