// GitHub Release API
// used by UserScript to query version info
// deploy this on Cloudflare Workers
// enable Caching in settings

export default {
  async fetch(request, env, ctx) {
    if (new URL(request.url).pathname !== "/") {
      return new Response(null, {
        status: 400,
        statusText: "Bad Request",
      });
    }

    let resp = await fetch("https://api.github.com/repos/eh-jap/Database/releases/latest", {
      headers: {
        Authorization: `Bearer ${env.GH_TOK}`,
        "X-GitHub-Api-Version": "2026-03-10",
        Accept: "application/vnd.github+json",
        "User-Agent": "dropout",
      },
      cf: {
        cacheTtl: 3600,
        cacheEverything: true,
      },
    });
    // Reconstruct the Response object to make its headers mutable.
    resp = new Response(resp.body, resp);
    resp.headers.set("Cache-Control", "max-age=3600");
    return resp;
  }
};
