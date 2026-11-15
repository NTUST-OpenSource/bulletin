// Units as the pickers group them: school-wide and administrative ones, then each college.
import type { Site } from "./api";

export type Group = { title: string | null; sites: Site[] };

/** The sites whose unit contains `query`, grouped: `school` first, then academic by college. */
export function unitGroups(sites: Site[], query: string, school: string, other: string): Group[] {
  const q = query.trim().toLowerCase();
  const matching = sites.filter((site) => site.unit.toLowerCase().includes(q));
  const groups: Group[] = [{ title: school, sites: matching.filter((site) => site.kind !== "academic") }];
  for (const site of matching.filter((s) => s.kind === "academic")) {
    const title = site.college ?? other;
    const group = groups.find((g) => g.title === title);
    if (group) group.sites.push(site);
    else groups.push({ title, sites: [site] });
  }
  return groups.filter((group) => group.sites.length > 0);
}
