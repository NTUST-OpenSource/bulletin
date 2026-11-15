import { expect, test } from "vitest";
import { POLICY } from "./csp";

test("The page: no script, style or font loads from another origin", () => {
  const directives = new Map(POLICY.split("; ").map((d) => [d.split(" ")[0], d.split(" ").slice(1)]));

  expect(directives.get("default-src")).toEqual(["'self'"]);
  for (const name of ["script-src", "font-src", "connect-src"]) expect(directives.has(name)).toBe(false);
  expect(directives.get("style-src")).toEqual(["'self'", "'unsafe-inline'"]);
});
