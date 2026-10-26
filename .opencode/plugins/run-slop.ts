import { spawnSync } from "node:child_process";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

import { Plugin } from "@opencode/plugin";

const pluginDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = dirname(dirname(pluginDir));

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang (.slop) file with Sloperator and return the program's stdout, stderr, and exit code.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Path to the .slop file to run, relative to the project root.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            stdout: { type: "string" },
            stderr: { type: "string" },
            exitCode: { type: "number" },
          },
          required: ["stdout", "stderr", "exitCode"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path } = input as { path: string };

          const result = spawnSync(
            "uv",
            ["run", "--no-active", "sloperator.py", path],
            { cwd: projectRoot, encoding: "utf-8" },
          );

          const stdout = result.stdout ?? "";
          const stderr = result.stderr ?? "";
          const exitCode = result.status ?? 1;

          const output = { stdout, stderr, exitCode };
          return { output, content: JSON.stringify(output, null, 2) };
        },
      });
    });
  },
});
