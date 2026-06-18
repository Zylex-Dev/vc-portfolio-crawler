/** Truncate to `max` chars, trimming trailing space and appending an ellipsis. */
export function clamp(text: string, max: number): string {
  if (!text) return "";
  return text.length <= max ? text : text.slice(0, max).trimEnd() + "…";
}
