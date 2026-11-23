import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const VISUAL_ROOT = join(ROOT, "visual");
const PORT = Number(process.env.PORT ?? 5173);

const types = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
]);

function resolveAsset(urlPath) {
  const cleanPath = decodeURIComponent(urlPath.split("?")[0] ?? "/");
  const target = cleanPath === "/" ? "/index.html" : cleanPath;
  const filePath = resolve(VISUAL_ROOT, `.${normalize(target)}`);
  if (!filePath.startsWith(VISUAL_ROOT)) return null;
  return filePath;
}

const server = createServer((req, res) => {
  const filePath = resolveAsset(req.url ?? "/");
  if (!filePath || !existsSync(filePath) || !statSync(filePath).isFile()) {
    res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    res.end("Not found");
    return;
  }

  res.writeHead(200, {
    "content-type": types.get(extname(filePath)) ?? "application/octet-stream",
    "cache-control": "no-store",
  });
  createReadStream(filePath).pipe(res);
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`Evidence Broker visual dashboard: http://127.0.0.1:${PORT}`);
});
