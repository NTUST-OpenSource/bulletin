// Requirement: Attachments (web-frontend): which attachments preview, and how the list names them.
import { describe, expect, test } from "vitest";
import type { Attachment } from "./api";
import { extension, kind, single, size } from "./files";

const stored = (name: string) => `/api/v1/files/${"a".repeat(64)}/${encodeURIComponent(name)}`;
const at = (name: string, file: string | null = stored(name), url = "https://www.ntust.edu.tw/var/file/1/1.bin"): Attachment => ({
  name,
  url,
  size: 1,
  file,
});

describe("Attachments", () => {
  test("a stored image, PDF or DOCX previews; other types and files kept only at the school do not", () => {
    for (const name of ["poster.JPG", "a.jpeg", "a.png", "a.gif", "a.webp"]) expect(kind(at(name))).toBe("image");
    expect(kind(at("form.pdf"))).toBe("pdf");
    expect(kind(at("form.docx"))).toBe("docx");
    expect(kind(at("list.xlsx"))).toBeNull();
    expect(kind(at("form.doc"))).toBeNull();
    expect(kind(at("form.pdf", null))).toBeNull();
    // The API types a stored copy by the name it was stored under, which may have no extension.
    expect(kind(at("notes", stored("notes"), "https://rd.ntust.edu.tw/var/file/413.pdf"))).toBeNull();
  });

  test("the badge takes the type from the name, else from the school's file URL", () => {
    expect(extension(at("poster.JPG"))).toBe("jpg");
    expect(extension(at("notes", null, "https://rd.ntust.edu.tw/var/file/413.pdf"))).toBe("pdf");
    expect(extension(at("notes", null, "https://bulletin.ntust.edu.tw/app/index.php?Action=downloadfile"))).toBe("");
    expect(extension(at("v1.2 final", null, "https://www.ntust.edu.tw/download"))).toBe("");
  });

  test("sizes in KB below a megabyte, else in MB", () => {
    expect(size(null)).toBe("");
    expect(size(100)).toBe("1 KB");
    expect(size(290_892)).toBe("284 KB");
    expect(size(1_182_314)).toBe("1.1 MB");
  });

  test("One image attachment: the only stored image shows at the end", () => {
    const image = at("poster.jpg");
    expect(single([image, at("a.pdf"), at("b.pdf")])).toBe(image);
    expect(single([image, at("other.png")])).toBeNull();
    expect(single([at("poster.jpg", null)])).toBeNull();
    expect(single([])).toBeNull();
  });
});
