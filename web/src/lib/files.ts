// An article's attachments: which ones preview, their badges and sizes, and the image shown at
// the article's end.
import type { Attachment } from "./api";

export type Kind = "image" | "pdf" | "docx";

/** How a click previews `attachment`; null when it follows the school's link. */
export function kind(attachment: Attachment): Kind | null {
  throw new Error(`not implemented: ${attachment.name}`);
}

/** The attachment's type for its badge; "" when unknown. */
export function extension(attachment: Attachment): string {
  throw new Error(`not implemented: ${attachment.name}`);
}

/** A byte count as the list shows it. */
export function size(bytes: number | null): string {
  throw new Error(`not implemented: ${bytes}`);
}

/** The image shown at the article's end: the only image among the attachments. */
export function single(attachments: Attachment[]): Attachment | null {
  throw new Error(`not implemented: ${attachments.length}`);
}
