// Reads one JSON object {"text": "..."} per line and answers one {"problems": [...]} line each,
// naming what Discord's Markdown parser makes of the text that a rendition must not hold.
import { createInterface } from "node:readline";
import { iter, parse } from "@discord/markdown-wasm";

const SCHEMES = new Set(["http:", "https:"]);

function isWeb(url) {
  try {
    return SCHEMES.has(new URL(url).protocol);
  } catch {
    return false;
  }
}

function problems(text) {
  const found = new Set();
  for (const node of iter(parse(text))) {
    if (node.type === "mention") {
      found.add("mention");
    } else if (node.type === "link" && !isWeb(node.value.url)) {
      found.add("link scheme");
    } else if (node.type === "text" && node.value.includes("](")) {
      // A masked link the parser did not take shows its brackets as text.
      found.add("unparsed link");
    }
  }
  return [...found];
}

for await (const line of createInterface({ input: process.stdin })) {
  let answer;
  try {
    answer = { problems: problems(JSON.parse(line).text) };
  } catch (error) {
    answer = { error: String(error) };
  }
  process.stdout.write(`${JSON.stringify(answer)}\n`);
}
