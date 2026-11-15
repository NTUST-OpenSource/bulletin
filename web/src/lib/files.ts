// An article's attachments: which ones preview, their badges and sizes, and the image shown at
// the article's end.
import type { Attachment } from "./api";

export type Kind = "image" | "pdf" | "docx";

const PREVIEWS: Record<string, Kind> = {
  png: "image",
  jpg: "image",
  jpeg: "image",
  gif: "image",
  webp: "image",
  pdf: "pdf",
  docx: "docx",
};
const SCRIPTS = new Set(["php", "asp", "aspx", "htm", "html", "jsp", "cgi"]); // a school page that hands out the file

const suffix = (name: string) => /\.([a-z][a-z0-9]{0,4})$/i.exec(name)?.[1]?.toLowerCase() ?? "";

/** How a click previews `attachment`; null when it follows the school's link. */
export function kind(attachment: Attachment): Kind | null {
  // The API types a stored copy by the name at the end of its path, as the browser will get it.
  return attachment.file === null ? null : (PREVIEWS[suffix(attachment.file)] ?? null);
}

/** The attachment's type for its badge; "" when unknown. */
export function extension(attachment: Attachment): string {
  const named = suffix(attachment.name);
  if (named) return named;
  try {
    const linked = suffix(new URL(attachment.url).pathname);
    return SCRIPTS.has(linked) ? "" : linked;
  } catch {
    return "";
  }
}

/** A byte count as the list shows it. */
export function size(bytes: number | null): string {
  if (bytes === null) return "";
  return bytes >= 1_048_576 ? `${(bytes / 1_048_576).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

/** The image shown at the article's end: the only image among the attachments. */
export function single(attachments: Attachment[]): Attachment | null {
  const images = attachments.filter((attachment) => kind(attachment) === "image");
  return images.length === 1 ? images[0]! : null;
}
