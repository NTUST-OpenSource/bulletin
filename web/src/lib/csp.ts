// The page's policy. The build writes it into index.html, so `vite preview` enforces what
// production does; `frame-ancestors` only works as a header, which the server sends.
export const POLICY = [
  "default-src 'self'",
  "img-src 'self' https: data: blob:", // school pages embed images from other hosts
  "style-src 'self' 'unsafe-inline'", // Svelte's transitions write inline styles
  "frame-src 'self'",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
].join("; ");

export const NO_FRAMES = "frame-ancestors 'none'";
